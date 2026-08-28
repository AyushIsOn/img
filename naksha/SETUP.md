# Setting up and running NAKSHA

Two independent pieces. **Start with the solver.** It runs anywhere, proves the
engineering, and produces the drawings and numbers you need for the report. The
iOS app then consumes its output.

---

## Part 1, the solver

### Install

```bash
cd naksha/solver
python3 -m venv .venv && source .venv/bin/activate    # optional but tidy
pip install -r requirements.txt
```

Needs Python 3.9 or newer. Three dependencies: `networkx`, `matplotlib`,
`numpy`.

### Run

```bash
python3 run.py 2bhk --out out       # also: 1bhk, 3bhk
```

You get five files per plan in `out/`:

| File | What it is |
|---|---|
| `2bhk-sheet1-layout.png` | Layout plan, every device point, legend, load summary |
| `2bhk-sheet2-circuits.png` | Circuit grouping, conduit routing, circuit schedule |
| `2bhk-sheet3-schematic.png` | Single line diagram, bill of quantities, design checks |
| `2bhk-boq.csv` | Bill of quantities, opens in Excel |
| `2bhk-design.json` | The full design. **This is what the iOS app reads.** |

### The benchmark

```bash
python3 benchmark.py
```

Prints the measured comparison against current practice. This is the table to
quote in the Feasibility section.

### Changing the design rules

Everything a reviewer might question lives in one file, `naksha/model.py`:
target lux per room type, luminaire output, coefficient of utilisation, light
loss factor, circuit load and point limits, diversity factors, the conductor
ampacity table, minimum conductor sizes, and voltage drop budgets. Change a
constant, rerun, and every drawing and quantity updates.

### Adding your own floor plan

Copy a function in `naksha/plans.py`. Rooms are polygons in metres, doors are
points with the two rooms they join. Rooms must tile without overlapping,
because the routing grid is built from them.

---

## Part 2, the iOS app

> **The Swift has not been compiled.** It was written outside Xcode, so expect a
> few build errors on first open. They should be shallow. Send them to me and I
> will fix them against real compiler output rather than guessing.

### What you need

| | |
|---|---|
| Mac with Xcode 15+ | required |
| Room scanning | LiDAR device: iPhone 12 Pro or later Pro, or iPad Pro |
| AR overlay | any ARKit iPhone |
| Everything else | works in the Simulator |

### Opening it

**With XcodeGen, one command:**

```bash
brew install xcodegen
cd naksha/ios
xcodegen generate
open Naksha.xcodeproj
```

**Or by hand, about two minutes:**

1. Xcode, File, New, Project, iOS, App.
2. Name it **Naksha**, interface **SwiftUI**, language **Swift**.
3. Save it inside `naksha/ios/`, then delete the `ContentView.swift` and
   `NakshaApp.swift` Xcode generated.
4. Drag in `Naksha/Models`, `Naksha/Services`, `Naksha/Views` and
   `Naksha/NakshaApp.swift`. Choose **Create groups**.
5. Drag in `Naksha/Resources/sample-2bhk.json`. Check it appears under
   **Target, Build Phases, Copy Bundle Resources**. If it does not, the app
   will launch and then fail to load the sample.
6. **Target, Info**, add `NSCameraUsageDescription` with any short sentence.
   RoomPlan and ARKit both refuse to start without it.
7. Set the deployment target to **iOS 17**.
8. Run.

### First thing to try

Launch and tap **Open the sample design**. That loads real solver output, so the
drawing, circuit schedule, as-built list and product list all populate with no
device and no network. This is the fastest way to see whether the app works.

### The five screens

| Tab | What to check |
|---|---|
| **Drawing** | Plan renders, tapping a circuit chip dims the others |
| **Circuits** | Schedule matches sheet 2 from the solver |
| **AR** | Point at the floor, tap to drop the origin, then adjust heading and ceiling |
| **As-built** | Tick points as confirmed, add a note, export the file |
| **Buy** | Product list with the reason each item is recommended |

### Using your own design

Replace `Naksha/Resources/sample-2bhk.json` with any `*-design.json` the solver
produced. The schema is identical, so nothing else changes.

---

## Part 3, designing a house you scanned yourself

Scanning alone does not produce a design. The scan measures rooms; the solver
turns rooms into circuits. They are two separate programs and they have to be
introduced to each other. This is the part to do before a demo.

### Step 1, start the solver on your Mac

If you have not installed the dependencies yet, do that first. Skipping it gives
you `ModuleNotFoundError: No module named 'networkx'`.

```bash
cd naksha/solver
python3 -m pip install -r requirements.txt
python3 serve.py
```

#### Turning on the AI interview

The intake questions can be written by a language model. It runs here, on this
machine, so no key is ever shipped in the app or held on the phone. A free tier
is plenty for a demo.

| Provider | Key | Cost | Notes |
|---|---|---|---|
| **Groq** | `GROQ_API_KEY` | free, no card | Fastest. Recommended |
| **Google** | `GEMINI_API_KEY` | free tier | Also accepts `GOOGLE_API_KEY` |
| **OpenRouter** | `OPENROUTER_API_KEY` | free models | Routed, survives model delistings |
| OpenAI | `OPENAI_API_KEY` | paid | |
| Anthropic | `ANTHROPIC_API_KEY` | paid | |

Export one and check it before you rely on it:

```bash
export GROQ_API_KEY=gsk_...
python3 serve.py --check-llm
```

That makes one real request and prints the first question the model wrote. If it
fails it says why rather than quietly carrying on.

#### Which Groq model

The default is `openai/gpt-oss-120b`, which is the right choice. Of what Groq
hosts, only a few are general chat models at all:

| Model | Use |
|---|---|
| `openai/gpt-oss-120b` | **Default.** Best at returning clean structured JSON |
| `openai/gpt-oss-20b` | Fallback if rate limited. Faster, slightly looser |
| `qwen/qwen3.8-27b` | Reasonable alternative |
| `groq/compound`, `compound-mini` | Avoid. Agentic, with web search and code execution we do not want |
| `openai/gpt-oss-safeguard-20b` | Avoid. Moderation classifier |
| `meta-llama/llama-prompt-guard-2-*` | Avoid. Injection classifiers, not chat |
| `canopylabs/orpheus-*`, `whisper-*` | Avoid. Speech, not text |

If a default id has been retired, override it. Groq's older Llama ids were
withdrawn in June 2026, which is the kind of thing that happens:

```bash
export NAKSHA_MODEL=openai/gpt-oss-20b
```

Any other OpenAI-compatible host works too:

```bash
export NAKSHA_BASE_URL=https://example.com/v1/chat/completions
export NAKSHA_API_KEY=...
```

**With no key the app still works.** The server answers from a scripted set of
questions and the flow is identical, so a demo cannot be lost to a missing key.
The app labels which is running, "AI interview" or "Standard questions", so
nothing is overclaimed.

If pip refuses with `externally-managed-environment`, which Homebrew Python
does, use a virtual environment:

```bash
cd naksha/solver
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 serve.py
```

Every new terminal then needs `source .venv/bin/activate` before `serve.py`.

The server itself only needs `networkx`. `numpy` and `matplotlib` are for the
drawing sheets that `run.py` produces, so `pip install networkx` is enough if
you only want the app talking to the solver.

It prints the addresses the phone can reach, for example:

```
NAKSHA solver listening on port 8000
  Set solverEndpoint in the app to one of:
    http://192.168.1.42:8000
```

Leave that terminal running. Check it from the Mac first:

```bash
curl http://localhost:8000/health
```

### Step 2, tell the app where it is

In the app, tap the **gear icon** at the top right, paste the
`http://192.168.1.42:8000` address, and tap **Test connection**. You want
"Connected". The icon on the home screen turns into an aerial once it is set.

The phone and the Mac must be on the same Wi-Fi. Phone hotspot to Mac works
too. Hotel and campus networks usually block device to device traffic, so use a
personal hotspot if the test fails on one.

### Step 3, scan, answer, design

1. **Scan a room.** Walk the room slowly until the walls close up, tap Done,
   then give it a name and pick its type. The type matters: it decides socket
   counts and whether a fan belongs there.
2. **Repeat for every room.** One scan per room.
3. **Answer the questions.** Lights, fans, sockets, and the appliances you want
   where. This is what the design is actually built from.
4. **Tap Design the installation.** The rooms and answers go to the Mac, the
   solver places points, groups circuits, sites the board, routes the conduit,
   sizes the cable, and sends back a full design.
5. **Open the AR tab** to project it on your walls.

### What the scan gives you, and what it does not

RoomPlan scans one room at a time, and each scan has its own origin. Nothing in
the captured data says how the rooms adjoin, so the app does not pretend to
stitch them. What it keeps is what the scan genuinely measures, the floor area
and the room type. What it approximates is the arrangement: rooms become
rectangles of the measured area, packed into a connected layout with doorways
inferred wherever two rooms share a wall.

That trade is deliberate. Area drives the lighting count through the lumen
method and room type drives the socket rules, so the circuit schedule, the cable
sizing and the bill of quantities are all sound. The absolute geometry matters
for the AR overlay, which is why AR registration is aligned by hand against the
room you are standing in.

### If you have no Mac on the network

Leave the solver address empty and tap **Open the sample design**. Everything
except designing your own scan works: drawing, schedule, AR overlay, as-built
and product list all run from bundled solver output.

---

## Troubleshooting

**"sample-2bhk.json is missing from the app bundle"**
It is not in Copy Bundle Resources. Target, Build Phases, add it.

**RoomPlan screen is greyed out**
No LiDAR on that device. Use the architect's plan or sketch path instead.

**AR screen is black**
`NSCameraUsageDescription` is missing from Info.plist, or you are running in the
Simulator. AR needs a real device.

**The AR overlay is in the wrong place**
Expected. Registration is manual by design. Tap **Reposition**, tap the floor
again at a known corner, then set heading with the slider. An overlay that is
confidently wrong is worse than one you placed yourself.

**"No solver address set, so the scanned rooms cannot be designed"**
Expected when no address is configured. Start `python3 serve.py` on the Mac and
paste the address it prints into the gear icon. Or tap **Open the sample
design** to explore the app without a solver.

**Test connection fails but the Mac says the server is running**
Three usual causes. The phone is on a different Wi-Fi network. The network
blocks device to device traffic, common on campus and hotel Wi-Fi, so use a
personal hotspot instead. Or the Mac firewall is prompting for permission to
accept incoming connections, so allow Python. Confirm the server itself is
healthy with `curl http://localhost:8000/health` on the Mac.

**Design fails with "could not design this plan"**
The solver could not build a valid layout from those rooms, usually because a
scan closed with a degenerate outline. The terminal running `serve.py` prints
the full reason. Rescanning that one room normally fixes it.

**Solver says maximum demand exceeds sanctioned load**
That is not an error, it is the finding. A 2 BHK with three air conditioners and
two water heaters really does exceed a 5 kW sanction. Change
`sanctioned_load_w` in `plans.py` to see it clear.

**matplotlib complains about a display**
It should not, the backend is forced to Agg in `draw.py`. If you see it, you are
importing matplotlib somewhere else first.

---

## What matches the original brief, and what does not

Honest status against the product as described.

| Requirement | Status | Notes |
|---|---|---|
| iOS application | Done | SwiftUI, iOS 17 |
| Import the architect's map | Done | Photo or PDF, set scale by tapping a known dimension, then trace rooms |
| Roughly draw the floor plan | Done | Room by room with sizes |
| AI asks about requirements | **Partial** | Adaptive and reacts to earlier answers, but rule driven. `LLMQuestionSource` is the seam for a real model; nothing is wired to one yet |
| Place the wiring for the whole floor in 3D | Done | Solver produces the model, app renders it |
| AR mode with LiDAR onto walls and ceiling | Done | Ceiling runs plus vertical drops to wall devices |
| Make a map out of it | Done | As-built tab, per point confirmation, notes, exportable file |
| Suggest and market V-Guard products | Done | Every recommendation is generated from a point in the design and shows its reason |

### Known gaps, stated plainly

- **No language model is connected.** The question flow is deterministic. This
  is defensible for a prototype and arguably correct for safety, but it is not
  what "generated by AI" implies, so do not claim it.
- **RoomPlan captures one room at a time.** Separate scans share no coordinate
  frame, so the app keeps the measured area and room type and approximates the
  arrangement rather than stitching. The schedule and quantities are sound; the
  plan geometry is representative, not surveyed.
- **The solver runs on a laptop, not on the phone.** The two connect over local
  Wi-Fi, so a demo needs both on the same network. Porting the solver to Swift
  would remove that, at the cost of maintaining the engineering logic twice.
- **Traced and scanned rooms become axis aligned rectangles.** Fine for the
  rectilinear rooms this targets, wrong for curved or slanted walls.
- **AR registration accuracy on a live site is unproven.** Promise dimensioned
  guidance, not millimetre placement.
- **Routing is modelled on a 0.5 m ceiling grid.** Real chasing follows
  structural constraints the model does not know about.
- **Prices are indicative placeholders**, not a catalogue feed.
