"""The conversational stage, driven by a language model.

Two rules shape this file.

The model asks and interprets. It never engineers. It cannot choose a cable
size, an MCB rating or a circuit grouping, because those come from the rule
engine where every decision is traceable to a clause. What the model produces is
a *profile*: what the household intends to own and how they intend to live.
That profile is then converted to requirements deterministically.

The key lives here, on the machine running the solver, and never reaches the
phone. If no key is configured, or the call fails, the rule based script takes
over and the interview still completes.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple

TIMEOUT = 45

# Reasoning models bill their thinking against this, so it is not a cap on the
# question length. Too small and `content` comes back empty.
MAX_OUTPUT_TOKENS = 4096

# --------------------------------------------------------------- the brief

SYSTEM = """\
You are the intake interviewer for NAKSHA, an app that designs the electrical \
installation for a home in India before the walls are closed.

Your job is to build a picture of what this household will plug in and how they \
live. A separate rule engine sizes cables and groups circuits against Indian \
standards. You must never suggest a cable size, an MCB rating, a circuit count \
or any wiring decision.

Ask ONE question at a time. Adapt to what you already know: never ask something \
already answered, and follow up when an answer implies more. A family of six \
implies different socket pressure from a couple. Three air conditioners against \
a 3 kW sanctioned load is worth a gentle flag, phrased as a question about \
their plan rather than as advice.

Keep prompts under 90 characters, plain, warm and specific. No jargon, no \
greetings after the first question, never mention that you are an AI.

Cover, roughly in this order, and stop once you have enough:
1. Their name.
2. Sanctioned load from the electricity bill, in kW.
3. How many bedrooms, and how many people will live there.
4. Air conditioners: how many, and which rooms.
5. Water heating: how many bathrooms need it.
6. Kitchen: chimney, induction, refrigerator, purifier.
7. Anything unusual: home office, EV charging, water pump, inverter backup.

Reply with JSON only, no prose and no code fence:

{
  "question": {
    "id": "short_snake_case_key",
    "prompt": "the question",
    "helper": "one short clarifying line, or null",
    "kind": "text" | "number" | "count" | "choice" | "multi",
    "unit": "kW" | null,
    "min": number or null,
    "max": number or null,
    "options": ["..."]
  },
  "profile": {
    "name": string or null,
    "sanctioned_load_w": number or null,
    "bedrooms": number or null,
    "occupants": number or null,
    "appliances": [{"kind": "ac|geyser|chimney|induction|refrigerator|ro|pump|ev|washing_machine|tv", "count": number, "rooms": ["..."]}],
    "notes": ["short observations worth carrying into the design"],
    "summary": "two sentences describing this household"
  },
  "done": false
}

"appliances" and "profile" must always be the COMPLETE picture so far, not just \
the newest answer. Set "done" true and "question" null when you have enough to \
plan the installation, which is usually after seven to nine questions.

Use "count" for small integers, "choice" when there is a short fixed list, \
"multi" when several options can apply, "number" for a measured quantity.
"""

# Appliance wattages. The model states intent; the rule engine states load, so
# these are never taken from the model even if it offers them.
WATTS = {
    "ac": 1500.0, "geyser": 2000.0, "chimney": 250.0, "induction": 2000.0,
    "refrigerator": 200.0, "ro": 60.0, "pump": 750.0, "ev": 3300.0,
    "washing_machine": 500.0, "tv": 150.0,
}

DEDICATED = {"ac", "geyser", "induction", "ev"}

VGUARD_CATEGORY = {
    "ac": "Air Conditioners", "geyser": "Water Heaters",
    "chimney": "Kitchen Appliances", "induction": "Kitchen Appliances",
    "ro": "Water Purifiers", "pump": "Pumps",
}

LABEL = {
    "ac": "Air conditioner 1 T", "geyser": "Water heater 15 L",
    "chimney": "Chimney", "induction": "Induction cooktop",
    "refrigerator": "Refrigerator", "ro": "RO purifier",
    "pump": "Water pump", "ev": "EV charger 3.3 kW",
    "washing_machine": "Washing machine", "tv": "Television",
}

# Which room kinds an appliance belongs in, best first.
PREFERRED_ROOMS = {
    "ac": ["bedroom", "living", "study"],
    "geyser": ["bath"],
    "chimney": ["kitchen"],
    "induction": ["kitchen"],
    "refrigerator": ["kitchen", "dining"],
    "ro": ["kitchen", "utility"],
    "pump": ["utility", "bath"],
    "ev": ["utility", "passage", "living"],
    "washing_machine": ["utility", "bath"],
    "tv": ["living", "bedroom"],
}


# ------------------------------------------------------------ model access
#
# Everything except Anthropic speaks the OpenAI chat-completions shape, so one
# code path covers Groq, Google, OpenRouter and OpenAI. Whichever key is present
# is used, in this order. Free tiers first, because that is what a prototype
# should run on.
#
#   GROQ_API_KEY        fastest free tier, no card required
#   GEMINI_API_KEY      or GOOGLE_API_KEY, free tier
#   OPENROUTER_API_KEY  free models, routed
#   OPENAI_API_KEY      paid
#   ANTHROPIC_API_KEY   paid, native API
#
# Any of it can be overridden:
#   NAKSHA_MODEL     model id, if a default has been retired
#   NAKSHA_BASE_URL  full chat-completions URL for any other compatible host
#   NAKSHA_API_KEY   key to go with NAKSHA_BASE_URL

GEMINI_URL = ("https://generativelanguage.googleapis.com"
              "/v1beta/openai/chat/completions")

PROVIDERS = [
    # env var,            label,        chat completions URL,                            default model
    ("GROQ_API_KEY",       "groq",       "https://api.groq.com/openai/v1/chat/completions",
     # The Llama ids most examples still use were retired in June 2026; this is
     # where Groq now points new traffic.
     "openai/gpt-oss-120b"),
    ("GEMINI_API_KEY",     "gemini",     GEMINI_URL, "gemini-2.5-flash"),
    ("GOOGLE_API_KEY",     "gemini",     GEMINI_URL, "gemini-2.5-flash"),
    ("OPENROUTER_API_KEY", "openrouter", "https://openrouter.ai/api/v1/chat/completions",
     # A router rather than a fixed id, because OpenRouter's free list churns
     # constantly and it filters for models that support structured output.
     "openrouter/free"),
    ("OPENAI_API_KEY",     "openai",     "https://api.openai.com/v1/chat/completions",
     "gpt-4o"),
]


def _provider() -> Optional[Dict]:
    """The active provider, or None if no key is configured."""
    override = os.environ.get("NAKSHA_BASE_URL")
    if override:
        key = os.environ.get("NAKSHA_API_KEY") or ""
        return {"label": "custom", "url": override, "key": key,
                "model": os.environ.get("NAKSHA_MODEL", "")}

    for env, label, url, model in PROVIDERS:
        key = os.environ.get(env)
        if key:
            return {"label": label, "url": url, "key": key,
                    "model": os.environ.get("NAKSHA_MODEL", model)}

    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return {"label": "anthropic",
                "url": "https://api.anthropic.com/v1/messages",
                "key": key,
                "model": os.environ.get("NAKSHA_MODEL",
                                        "claude-sonnet-4-5-20250929")}
    return None


def available() -> bool:
    return _provider() is not None


def provider_name() -> str:
    p = _provider()
    return f"{p['label']}:{p['model']}" if p else "none"


def _post(url: str, payload: Dict, headers: Dict) -> Dict:
    body = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode())


def _complete(transcript: List[Dict]) -> str:
    """One completion. Raises on any transport or auth problem."""
    p = _provider()
    if p is None:
        raise RuntimeError("no model key configured")

    if p["label"] == "anthropic":
        data = _post(p["url"],
                     {"model": p["model"], "max_tokens": 1200,
                      "system": SYSTEM, "messages": transcript},
                     {"content-type": "application/json",
                      "x-api-key": p["key"],
                      "anthropic-version": "2023-06-01"})
        return "".join(b.get("text", "") for b in data.get("content", []))

    messages = [{"role": "system", "content": SYSTEM}] + transcript
    headers = {"content-type": "application/json",
               "authorization": f"Bearer {p['key']}"}
    if p["label"] == "openrouter":
        headers["HTTP-Referer"] = "https://github.com/AyushIsOn/img"
        headers["X-Title"] = "NAKSHA"

    # The budget is deliberately generous. gpt-oss and the Qwen 3 family are
    # reasoning models whose thinking is billed against the same limit, so a
    # tight cap returns an empty `content` and looks exactly like a failure.
    # reasoning_effort is set low because this is one short structured question,
    # not a problem that needs deliberation.
    #
    # Hosts disagree about parameter names and about which extras they accept,
    # and a rejected parameter is indistinguishable from a bad key unless the
    # request is retried. So the variants are tried in order, most capable
    # first, falling back to the plainest request any host must accept.
    variants: List[Dict] = [
        {"max_completion_tokens": MAX_OUTPUT_TOKENS,
         "response_format": {"type": "json_object"},
         "reasoning_effort": "low"},
        {"max_completion_tokens": MAX_OUTPUT_TOKENS,
         "response_format": {"type": "json_object"}},
        {"max_tokens": MAX_OUTPUT_TOKENS,
         "response_format": {"type": "json_object"}},
        {"max_tokens": MAX_OUTPUT_TOKENS},
        {},
    ]

    last: Optional[Exception] = None
    for extras in variants:
        try:
            data = _post(p["url"],
                         dict({"model": p["model"], "messages": messages},
                              **extras),
                         headers)
        except urllib.error.HTTPError as exc:
            # 400 class means the request shape was wrong, so try a plainer
            # one. Anything else is auth, rate limiting or the network, and
            # retrying with fewer parameters would not help.
            if exc.code not in (400, 404, 415, 422):
                raise
            last = exc
            continue

        choice = (data.get("choices") or [{}])[0].get("message", {})
        text = (choice.get("content")
                or choice.get("reasoning_content") or "").strip()
        if text:
            return text
        # Reasoning consumed the whole budget. A plainer request usually
        # leaves room for an answer.
        last = RuntimeError("model returned no content, budget exhausted "
                            "by reasoning")

    raise last or RuntimeError("no usable reply from the model")


def _extract_json(text: str) -> Dict:
    """Models sometimes fence the JSON or add a sentence. Recover anyway."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model reply")
    return json.loads(text[start:end + 1])


# ---------------------------------------------------------------- the turn

def next_turn(answers: List[Dict], profile: Optional[Dict] = None) -> Dict:
    """The next question, given every answer so far.

    `answers` is a list of {"id", "prompt", "answer"}. Returns the payload the
    app renders, always including which source produced it so the interface can
    be honest about whether the model is running.
    """
    if available():
        try:
            transcript = [{
                "role": "user",
                "content": json.dumps({
                    "answers_so_far": answers,
                    "profile_so_far": profile or {},
                }),
            }]
            reply = _extract_json(_complete(transcript))
            reply["source"] = "llm"
            reply.setdefault("done", False)
            reply.setdefault("profile", profile or {})
            if reply.get("done"):
                reply["question"] = None
            return reply
        except Exception as exc:               # noqa: BLE001
            print(f"  interview: {provider_name()} unavailable ({exc}), "
                  f"falling back to the script")

    return _scripted(answers, profile or {})


# ------------------------------------------------------- scripted fallback

SCRIPT = [
    {"id": "name", "prompt": "What should we call you?",
     "helper": "This goes on the drawing.", "kind": "text"},
    {"id": "sanctioned_load", "prompt": "What is your sanctioned load?",
     "helper": "On your electricity bill. Most homes start at 3 to 5 kW.",
     "kind": "number", "unit": "kW", "min": 1, "max": 20},
    {"id": "bedrooms", "prompt": "How many bedrooms will the house have?",
     "helper": None, "kind": "count", "min": 1, "max": 8},
    {"id": "occupants", "prompt": "How many people will live there?",
     "helper": "It changes how many sockets you will want.",
     "kind": "count", "min": 1, "max": 12},
    {"id": "ac", "prompt": "How many air conditioners are you planning?",
     "helper": "Include ones you might add later.",
     "kind": "count", "min": 0, "max": 6},
    {"id": "geyser", "prompt": "How many bathrooms need a water heater?",
     "helper": None, "kind": "count", "min": 0, "max": 5},
    {"id": "kitchen", "prompt": "Which of these will the kitchen have?",
     "helper": "Pick all that apply.", "kind": "multi",
     "options": ["Chimney", "Induction cooktop", "Refrigerator",
                 "RO purifier"]},
    {"id": "extras", "prompt": "Anything else worth planning for?",
     "helper": "Pick all that apply.", "kind": "multi",
     "options": ["Home office", "EV charging", "Water pump",
                 "Inverter backup", "Washing machine"]},
]


def _scripted(answers: List[Dict], profile: Dict) -> Dict:
    asked = {a.get("id") for a in answers}
    profile = _fold(answers, profile)
    for step in SCRIPT:
        if step["id"] not in asked:
            return {"question": dict(step), "profile": profile,
                    "done": False, "source": "rules"}
    return {"question": None, "profile": profile, "done": True,
            "source": "rules"}


def _number(value) -> Optional[float]:
    try:
        return float(re.sub(r"[^0-9.\-]", "", str(value)) or 0)
    except ValueError:
        return None


def _fold(answers: List[Dict], profile: Dict) -> Dict:
    """Build the profile from scripted answers, mirroring the model's schema."""
    out = {"name": profile.get("name"),
           "sanctioned_load_w": profile.get("sanctioned_load_w"),
           "bedrooms": profile.get("bedrooms"),
           "occupants": profile.get("occupants"),
           "appliances": [], "notes": [], "summary": ""}
    picked: Dict[str, Dict] = {}

    def add(kind: str, count: int) -> None:
        if count > 0:
            picked[kind] = {"kind": kind, "count": count, "rooms": []}

    for a in answers:
        key, value = a.get("id"), a.get("answer")
        if key == "name":
            out["name"] = str(value).strip() or None
        elif key == "sanctioned_load":
            kw = _number(value) or 5
            out["sanctioned_load_w"] = kw * 1000 if kw <= 40 else kw
        elif key == "bedrooms":
            out["bedrooms"] = int(_number(value) or 1)
        elif key == "occupants":
            out["occupants"] = int(_number(value) or 2)
        elif key in ("ac", "geyser"):
            add(key, int(_number(value) or 0))
        elif key in ("kitchen", "extras"):
            chosen = value if isinstance(value, list) else [value]
            names = {str(c).lower() for c in chosen}
            for label, kind in (("chimney", "chimney"),
                                ("induction", "induction"),
                                ("refrigerator", "refrigerator"),
                                ("ro", "ro"), ("purifier", "ro"),
                                ("ev", "ev"), ("pump", "pump"),
                                ("washing", "washing_machine")):
                if any(label in n for n in names):
                    add(kind, 1)
            if any("office" in n for n in names):
                out["notes"].append("Home office, wants dedicated desk sockets")
            if any("inverter" in n for n in names):
                out["notes"].append("Inverter backup, lighting on a reserve way")

    out["appliances"] = list(picked.values())
    who = out.get("name") or "The household"
    beds = out.get("bedrooms") or "?"
    heads = out.get("occupants") or "?"
    out["summary"] = (f"{who}, {heads} people in a {beds} bedroom home on a "
                      f"{(out.get('sanctioned_load_w') or 5000) / 1000:g} kW "
                      f"sanction.")
    return out


# ----------------------------------------- profile to solver requirements

def requirements_from_profile(profile: Dict, rooms: List) -> Dict:
    """Turn the interview into per-room appliance placements.

    Deterministic on purpose. The model said what the family wants; where each
    appliance physically goes follows from room type and size, which is a rule,
    not a judgement.
    """
    by_kind: Dict[str, List] = {}
    for room in rooms:
        by_kind.setdefault(room.kind, []).append(room)
    for group in by_kind.values():
        group.sort(key=lambda r: -r.area)

    appliances: List[Dict] = []
    used: Dict[str, int] = {}

    for entry in profile.get("appliances") or []:
        kind = str(entry.get("kind", "")).lower()
        if kind not in WATTS:
            continue
        count = max(0, int(entry.get("count") or 0))

        # Rooms the model named, if they exist, then the preferred types.
        candidates: List = []
        for wanted in entry.get("rooms") or []:
            match = next((r for r in rooms
                          if r.name.lower() == str(wanted).lower()), None)
            if match:
                candidates.append(match)
        for kind_pref in PREFERRED_ROOMS.get(kind, []):
            candidates.extend(by_kind.get(kind_pref, []))

        placed = 0
        for room in candidates:
            if placed >= count:
                break
            # one of a kind per room, except the living room can take a second
            seen = used.get(f"{kind}:{room.name}", 0)
            if seen >= 1:
                continue
            used[f"{kind}:{room.name}"] = seen + 1
            appliances.append({
                "room": room.name,
                "kind": "fridge" if kind == "refrigerator" else kind,
                "name": LABEL.get(kind, kind.title()),
                "watts": WATTS[kind],
                "dedicated": kind in DEDICATED,
                "vguardCategory": VGUARD_CATEGORY.get(kind),
            })
            placed += 1

    return {
        "appliances": appliances,
        "perRoom": {},
        "sanctionedLoadW": profile.get("sanctioned_load_w") or 5000,
    }
