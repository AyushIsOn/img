# NAKSHA, complete project handoff

Everything needed to continue this project with no prior memory of it. Written 28 August 2026
because the session that built it is ending.

**Read sections 1, 2 and 12 before touching anything.** Section 12 is the list of decisions that
must not be undone. Section 9 holds the full report text so the words survive even if the repo
does not.

---

# 1. Project identity

| | |
|---|---|
| Name | **NAKSHA** |
| Competition | **V-Guard Big Idea Tech Design Competition 2026** |
| Track | **Track 4: Digital Solutions for Consumer Engagement** |
| Team | **TI3405_D38N** |
| Member | **AYUSH GUPTA** (sole member) |
| Repo | `https://github.com/AyushIsOn/img` (private) |
| User's clone | `/Users/izhu/Documents/img` |
| Submission date on cover | 28 August 2026 |

**Tagline:** an augmented reality service that plans a home's wiring, and sells the wire.

**What it is.** An iOS app plus a Python design engine. The owner answers about eight questions,
walks each room with the iPhone's LiDAR sensor, and gets a full electrical design: every light,
fan, socket, switchboard and appliance point placed, points grouped into circuits, cable and
breaker sized per circuit, distribution board sited, conduit routed, and a priced bill of
quantities. The design is then overlaid on the real walls in augmented reality at full size,
before anything is chased.

**The commercial argument.** It is a sales channel, not a product. Give it away, because the
revenue is the wire, water heater and chimney it specifies. Services get chosen once, during
construction, and never re-shopped.

**WHAT IS ACTUALLY BEING SUBMITTED: a Detailed Report plus a one minute demo video. Not code.**
The report is built and verified. The video is recorded by the user from the running app. Do not
refactor the app unless asked.

---

# 2. Current state, honestly

| Piece | State |
|---|---|
| Python solver, six stage pipeline | Working |
| iOS app, scan to drawing to AR | Working, builds clean |
| LLM interview on Groq | Working, live |
| Detailed Report DOCX and PDF | Built, verified, **merged to `main`** |
| AR overlay alignment | **Visibly off. User said "lets go with it".** |
| 3 exhibit images | **Placeholders. Only the user can fix.** |
| `NAKSHA-VIDEO-SCRIPT.md` | **Stale, contradicts the report. See section 10.** |
| `VIDEO-SCRIPT.md` | **Belongs to a different project. See section 10.** |

## 2.1 Open items, in priority order

1. **Swap 3 placeholder exhibit images.** `vguard-bigidea/exhibits/berger-express-painting.jpg`,
   `laser-projector.jpg`, `dusty-robotics.jpg` are generated placeholders at the correct aspect
   ratio, not real photographs. The user pasted the real images into chat, and an agent cannot
   write chat attachments to disk. Guessing source URLs was tried and failed. **Fix: open the
   DOCX in Word, right click each image, Change Picture, then re save as PDF.** Layout holds
   because the placeholders match the real aspect ratios. Do not substitute different images
   found on the web; that was considered and rejected for wrong subject matter and unclear
   licensing.
2. **Rewrite the video script.** See section 10. The existing one is 40 seconds, cites a
   statistic that was removed from the report as unsourceable, and describes an older version of
   the idea.
3. **Confirm the Drive link** in `report_content.py` matches the uploaded video.
4. **Verify the front page** against the user's template image.

AR alignment is knowingly imperfect and the user accepted it. Do not spend a session on it
unless asked.

---

# 3. Repository map

```
HANDOFF.md                       this file
CEED_RESOURCES.md                unrelated to NAKSHA, ignore
naksha/
  28_8_2026.glb                  LiDAR scan of the user's real room, dimensional ground truth
  README.md, SETUP.md
  .gitignore                     line 10 ignores .naksha-key
  solver/
    serve.py           312 ln    HTTP server, the only thing the phone talks to
    run.py             125 ln    CLI, renders sheets and BoQ to naksha/docs/examples
    benchmark.py       133 ln    routing savings. ITS NUMBERS MUST NOT GO IN THE REPORT
    requirements.txt
    .naksha-key                  Groq key, git ignored, created by --set-key
    naksha/
      __init__.py
      model.py         360 ln    dataclasses, geometry, CABLE_TABLE, sizing constants
      design.py        752 ln    THE ENGINE, six stages
      interview.py     585 ln    LLM interview, provider detection, key storage, rule fallback
      asbuilt.py       286 ln    the user's real surveyed room, hardcoded
      ingest.py        293 ln    RoomPlan JSON to FloorPlan
      draw.py          371 ln    three drawing sheets
      plans.py         166 ln    sample 1/2/3 BHK plans
  ios/
    project.yml                  XcodeGen spec. NO .xcodeproj in git, you must generate it
    README.md
    Naksha/
      NakshaApp.swift         63 ln
      DesignSystem/
        VGuardTheme.swift    106 ln   V-Guard amber #F59B1C, gold #FFC431, on black
        LiquidGlass.swift    238 ln   glass surfaces, animated MeshGradient backdrop
      Models/
        Design.swift         272 ln
        Interview.swift      192 ln
      Resources/
        sample-2bhk.json
      Services/
        DesignStore.swift    258 ln   solverAddress in UserDefaults, network calls
        QuestionEngine.swift 248 ln
        ProductCatalogue.swift 146 ln
        AsBuiltRecord.swift  282 ln
      Views/
        HomeView.swift       203 ln
        InterviewView.swift  407 ln
        RoomScanView.swift   538 ln   RoomPlan capture
        RoomBriefView.swift  379 ln   3 hardcoded per room questions
        PlanCanvasView.swift 326 ln   the 2D drawing. Contains `PlanAxis`, see 12.2
        ARWiringView.swift   699 ln   the AR overlay
        DesignTabsView.swift 234 ln
        RequirementsView.swift 392 ln
        ProfileSummaryView.swift 214 ln
        PlanImportView.swift 361 ln
        SolverSettingsView.swift 102 ln
  docs/examples/                 rendered output, 3 sheets + BoQ csv per plan, benchmark.txt
vguard-bigidea/
  report_content.py    355 ln    ALL report text, single source for both builders
  build_docx.py        287 ln    writes the DOCX, then verifies it
  build_report.py      301 ln    writes the PDF, then verifies it
  make_diagram.py      132 ln    writes exhibits/flow-diagram.png
  exhibits/
    flow-diagram.png             real, generated
    berger-express-painting.jpg  PLACEHOLDER
    laser-projector.jpg          PLACEHOLDER
    dusty-robotics.jpg           PLACEHOLDER
    README.md
  NAKSHA-Detailed-Report.docx    THE DELIVERABLE
  NAKSHA-Detailed-Report.pdf     THE DELIVERABLE
  NAKSHA-VIDEO-SCRIPT.md         STALE, see section 10
  SOURCE-full-draft.md           the user's original longer draft, superseded by report_content
  VIDEO-SCRIPT.md                DIFFERENT PROJECT, see section 10
  build_pdf.py, build_slides.py, build_naksha_final.py     SUPERSEDED, do not edit
  NAKSHA-Diagram.pdf, NAKSHA-Executive-Summary.pdf         older outputs
  INVIDIA-CORE-Executive-Summary.pdf, INVIDIA-CORE-Slides.pdf   DIFFERENT PROJECT
```

**The live report path is `report_content.py` plus `build_docx.py` plus `build_report.py` only.**
Everything else in `vguard-bigidea/` is history. `INVIDIA-CORE-*` and `VIDEO-SCRIPT.md` belong to
an entirely different competition idea, a stabilizer built into a distribution board, that was
abandoned in favour of NAKSHA.

---

# 4. Commands

```bash
# get current
cd /Users/izhu/Documents/img && git checkout main && git pull

# iOS. There is no committed .xcodeproj, it is generated
cd naksha/ios && xcodegen generate && open Naksha.xcodeproj
#   Set your own signing team.
#   Needs a LiDAR device, iPhone 12 Pro or later. RoomPlan and ARKit
#   do NOT run in the simulator.

# dependencies. A fresh machine has NONE of these.
# solver:  networkx>=3.0, matplotlib>=3.6, numpy>=1.24   (naksha/solver/requirements.txt)
# report:  reportlab (PDF), python-docx (DOCX), matplotlib (flow diagram)
pip3 install -r naksha/solver/requirements.txt
pip3 install reportlab python-docx matplotlib

# solver, on the Mac, phone on the same wifi
cd naksha/solver && pip3 install -r requirements.txt
NAKSHA_ASBUILT=1 python3 serve.py     # serves the user's real room. USE THIS FOR THE DEMO
python3 serve.py                      # normal, designs whatever the phone scanned
#   Prints http://<lan-ip>:8000. Type that address into the app's Solver Settings.

# Groq key, stored once, never on the phone.
# The real key is NOT in this repo and must not be committed, see rule 13.
# It is already saved on the user's Mac at naksha/solver/.naksha-key
python3 serve.py --set-key <groq-key>
python3 serve.py --check-llm          # confirms the model answers

# report, all three, in this order
cd vguard-bigidea && python3 make_diagram.py && python3 build_docx.py && python3 build_report.py

# solver CLI, renders sheets + BoQ without a phone
cd naksha/solver && python3 run.py
```

Environment variables: `NAKSHA_ASBUILT=1` serves the hardcoded real room. `NAKSHA_MODEL`
overrides the model id if the default is retired. `GROQ_API_KEY` works as an alternative to the
key file.

## 4.1 Server API, read from `serve.py`

| Method | Path | Behaviour |
|---|---|---|
| GET | `/health` | `{status, addresses, plans, interview: "llm"\|"rules", model}` |
| GET | `/sample/<1bhk\|2bhk\|3bhk>` | a full design with no scan needed |
| POST | `/design` | body `{rooms: [...]}`. Returns the design payload. 400 if `rooms` is empty, 413 over `MAX_BODY` |
| POST | `/interview` | body `{answers: [], profile: {}}`. Returns the next question |

Anything else returns 404 with `{"error": "not found", "try": ["/health", "/design", "/sample/2bhk"]}`.
`/interview` is handled before the rooms check, because the interview runs before any scan
exists.

---

# 5. The design engine

`design_floor(plan, reqs)` in `design.py` runs six stages in order. Each stage's output feeds the
next, so a bug surfaces downstream of its cause.

### Stage 1, `place_points(plan, reqs)`
Decides what goes where.
- `lumen_method_count(room)` sizes lighting from measured floor area against a lux target
- `_primary_door(plan, room)` finds the entry door
- `_wall_slots(room, count, avoid, ...)` puts switchboards on walls, avoiding door swings
- `_inset_from_wall(room, p, inset=0.28)` holds a 0.28 m offset off the wall
- `_perimeter_ring(room, n)` distributes sockets around the perimeter
- `_grid_positions(room, n, ...)` places fans and ceiling lights

### Stage 2, `group_circuits(points, plan)`
Clusters points into circuits through `_cluster(points, max_w, max_n, ...)`, bounded by maximum
watts and maximum points per circuit. Anything flagged `dedicated` gets its own circuit. Small
leftover groups are merged back if they fit within both bounds.

### Stage 3, `choose_board(plan, circuits, ...)`
Sites the distribution board by evaluating candidate positions with
`_mst_cost(nodes, root, ...)`, the minimum spanning tree cost from that board to every circuit.

### Stage 4, `build_route_graph(plan)` then `route_circuits(g, board, ...)`
Builds a graph of legal conduit paths through walls and ceiling, `_snap(g, p)` attaches points to
it, and routing runs a rectilinear Steiner minimal tree approximation so **circuits share trunk
runs** instead of each point getting its own cable back to the board. This is the Hanan 1966
problem, reference [5] in the report, the same one circuit board routers solve.

### Stage 5, `size_circuits(circuits)`
**Order matters and is a safety property.** The breaker is chosen from the design current first,
then a conductor whose ampacity covers that breaker. The reverse order is a protection violation,
because a breaker rated above the cable it protects will not trip before the cable overheats.
- `current_for(watts)` design current
- `select_mcb(design_current)` breaker
- `select_cable(design_current)` conductor from `CABLE_TABLE`
- `voltage_drop_percent(current, length_m, ...)` checked, conductor increased on failure

### Stage 6, `bill_of_quantities(d)`
Totals material. `_bucket(p)` classifies points. `maximum_demand(d)` applies diversity and
compares against the sanctioned load. `validate(d)` returns a list of code violations.

## 5.1 Engine constants, from `model.py`

```python
CABLE_TABLE = [   # (sq mm, ampacity A)
    (1.0, 11.0), (1.5, 14.0), (2.5, 18.5), (4.0, 25.0),
    (6.0, 32.0), (10.0, 43.0), (16.0, 57.0),
]

SUPPLY_VOLTAGE = 230.0
POWER_FACTOR   = 0.95

TARGET_LUX = {"living": 150, "bedroom": 120, "kitchen": 200, "bath": 100,
              "utility": 100, "passage": 75, "dining": 150, "study": 300,
              "balcony": 75}            # default 150 if room kind unknown

LUMINAIRE_LUMENS   = 1800.0   # an 18 W LED panel or batten
LUMINAIRE_WATTS    = 18.0
COEFF_UTILISATION  = 0.55     # light reaching the working plane
LIGHT_LOSS_FACTOR  = 0.80     # dirt and lamp depreciation

SOCKET_RULE = {   # (m2 per socket, minimum, maximum)
    "living": (6.0, 3, 8), "bedroom": (7.0, 3, 6), "kitchen": (4.0, 3, 8),
    "bath": (0.0, 1, 1), "utility": (8.0, 1, 3), "passage": (0.0, 1, 1),
    "dining": (8.0, 2, 4), "study": (5.0, 3, 6), "balcony": (0.0, 1, 2),
}

DIVERSITY = {   # (first circuit factor, remainder factor)
    "lighting": (1.00, 0.66), "sockets": (1.00, 0.40),
    "geyser":   (1.00, 0.50), "ac":      (1.00, 0.75),
    "fixed":    (1.00, 0.75),
}
```

Lumen method as implemented: `target = TARGET_LUX.get(room.kind, 150)`, denominator is
`LUMINAIRE_LUMENS * COEFF_UTILISATION * LIGHT_LOSS_FACTOR`.

Key dataclasses in `model.py`: `Door`, `Room`, `Window`, `Fixture`, `FloorPlan`, `Appliance`,
`RoomRequirement`, `Requirements`, `DevicePoint`, `Circuit`. Geometry helpers: `dist`,
`manhattan`, `polygon_area`, `centroid`, `point_in_polygon`, `edges_of`, `project_to_segment`.

**`benchmark.py` measures how much cable the shared tree saves. Do not put its output in the
report. See rule 1.**

---

# 6. The iOS app

## 6.1 Flow

Home → Interview (LLM) → Room scan (RoomPlan) → Room brief (3 questions) → Drawing
(`PlanCanvasView`) → AR (`ARWiringView`). Design tabs give circuits and bill of quantities.
Solver address is entered in `SolverSettingsView` and persisted to `UserDefaults` under key
`solverAddress` by `DesignStore`.

## 6.2 UI

Liquid Glass surfaces throughout, Apple system font, V-Guard colours: amber `#F59B1C` and gold
`#FFC431` on black, with an animated `MeshGradient` backdrop. In `DesignSystem/`.

## 6.3 Real room shapes

`RoomConverter` reads `room.floors[].polygonCorners` from RoomPlan, not bounding boxes, so an L
shaped room stays L shaped. On the solver side `_outline()` preserves the polygon through
`_pack()`. **If rooms ever start coming out rectangular, that pair is where it broke.**

## 6.4 AR, and why it is misaligned

`ARWiringView.swift`, 699 lines. Relevant types and line numbers:

| Line | Type |
|---|---|
| 16 | `struct ARWiringView: View` |
| 279 | `enum RoomCorner`, four corners, `planPoint(in room:)` at 295 maps corner to plan coords |
| 315 | `struct Placement`, holds the two corners tapped |
| 365 | `struct PlanTransform`, built from `Placement` and `Room` |
| 401 | `PlanTransform.world(_ p: CGPoint, _ height: Float) -> SIMD3<Float>` |
| 413 | `struct ARContainer: UIViewRepresentable` |
| 483 | `Coordinator.render(placement:visibleCircuit:)` builds entities |
| 585 | conduit builder, `thickness: Float = 0.040`, so 40 mm |
| 673 | `enum Palette` |

**Alignment method: the user taps two floor corners of the real room and the plan is fitted to
those two points**, which fixes position and rotation exactly. Ceiling height comes from the
scan. This was chosen deliberately. The rejected alternative was anchoring to the room centre
with a heading slider, which fails because in a furnished room nobody can tap the centre of the
floor; it is under the bed.

Materials are `UnlitMaterial` so runs stay bright and readable on camera. Captions are 3D text.
The controls overlay can be hidden, which exists specifically so the user can record the demo
without UI in frame.

It is still visibly off. Two tap fitting is sensitive to tap precision and to ARKit's floor plane
estimate. The user accepted it: "the ar thing its still not woking fine but lets go with it."

## 6.5 Room brief questions

`RoomBriefView` asks **3 hardcoded per room questions**, deliberately hardcoded for demo
reliability:
1. How many lights do you want?
2. How many fans do you want?
3. Do you want an AC here, and at what capacity?

Under the lighting question it shows advice computed from the scanned area, of this form: based
on the scan, 1 × 12 W panel and one 25 W tubelight, about 3,300 lm across 14.6 m², reaches the
140 lux a bedroom wants; put the tubelight on the wall opposite the window.

---

# 7. The LLM interview

`interview.py`, 585 lines. Provider is auto detected. **In use: Groq, model
`openai/gpt-oss-120b`.** The key lives in `naksha/solver/.naksha-key`, git ignored, written by
`save_key()` via `--set-key`. **The key never reaches the phone.** The phone posts to
`/interview` and the Mac calls Groq.

Functions: `_saved_key()`, `save_key(key)`, `_provider()`, `available()`, `provider_name()`,
`_post(url, payload, headers)`, `_complete(transcript)`, `_extract_json(text)`,
`next_turn(answers, profile)`, `_scripted(answers, profile)`, `_number(value)`,
`_fold(answers, profile)`, `requirements_from_profile(profile, rooms)`.

**The model only turns conversation into a profile.** It never sizes a cable, picks an MCB, or
places a device. Every decision that could hurt somebody is made by the rule engine. This is a
deliberate architectural boundary and the report makes a point of it. `next_turn` falls back to
`_scripted` if the provider is unreachable and the app behaves identically. `_fold` merges
answers into the profile. `requirements_from_profile` converts the profile into solver
`Requirements`.

**The first question is hardcoded to "What's your name?"** because the model kept producing "What
is the name of the homeowner?". Prompt only fixes were tried and did not hold.

## 7.1 Groq gotchas, each one cost real debugging time

1. **Cloudflare 403 with body `error code: 1010`.** Cause: no `User-Agent` header. Python
   urllib's default is fingerprinted and blocked. Send one.
2. **`response_format: {"type": "json_object"}` is rejected unless the messages contain the
   literal lowercase word "json".** The prompt therefore says "Reply with one json object, no
   prose, no code fence".
3. **gpt-oss returns its thinking in `reasoning`, not `reasoning_content`.** Only `content` is
   the answer. Reading the wrong field yields thinking text where JSON was expected.
4. **8000 tokens per minute limit**, and reasoning bills against it. Hence
   `MAX_OUTPUT_TOKENS = 900` and `reasoning_effort: "low"`.
5. **`openai/gpt-oss-20b` returns 403, blocked at the org level.** Not a usable fallback.
6. **GitHub push protection rejects any commit containing the Groq key.** Keep it out of tracked
   files.

`_extract_json` is defensive for a reason: it strips a ```json fence if present, otherwise takes
the substring from the first `{` to the last `}`.

---

# 8. The report, mechanics

`report_content.py` holds every word. `build_docx.py` and `build_report.py` each write their
format and then **read their own output back** and assert margins, font, spacing, embedded image
count and size, every required heading, and the absence of any institution name or the removed
claim.

## 8.1 Brief requirements

- PDF format
- 1.5 line spacing
- 3 cm margins
- Times New Roman, 11 pt
- Must not exceed 4,000 to 5,000 words, excluding exhibits, charts, sketches and supporting
  material, and excluding the summary
- Preceded by a synopsis of **no more than 300 words**
- Table of contents with topic headings
- References at the end, indicated at appropriate places in the text by serial numbers
  corresponding to the reference list
- **No college, university or institution name anywhere**

The user targeted roughly 2,500 words rather than the cap: "i don't want the report to be too
long i guess 2500 words would be enough".

## 8.2 Verified output

| | |
|---|---|
| Synopsis | 292 words by the builder's `count_words`, 293 by a naive whitespace split. Limit is 300, so it passes either way |
| Body | 1,681 words |
| References | 10, all cited inline, no orphans either direction |
| Exhibits | 4 of 4 embedded |
| Format | Times New Roman 11 pt, 1.5 spacing, 3 cm margins |
| PDF | 11 pages |
| Confirmed absent | Manipal, University, College, Institute, School, and the removed saving figures |

## 8.3 Front page

Reproduces the user's template exactly: black `DETAILED REPORT`, the competition line in red, the
instruction line, a bordered box containing team name and three numbered member slots, number of
words and date of submission, and `(First Page)` at the foot.

```
DETAILED REPORT
V-GUARD INDUSTRIES LTD – BIG IDEA TECH DESIGN COMPETITION 2026    (red)
The first page of the report must adhere to the format given below:
┌───────────────────────────────────────────────────────────────┐
│ Team Name: TI3405_D38N                                        │
│ Team Members (Full Name)                                      │
│     1) AYUSH GUPTA                                            │
│     2)                                                        │
│     3)                                                        │
│ Number of words: 1932         Date of Submission: 28 Aug 2026  │
└───────────────────────────────────────────────────────────────┘
                                                   (First Page)
```

The user's template arrived as unreadable compressed bytes, so the front page was rebuilt from
the rendered image rather than parsed from the file.

## 8.4 Content model

`BODY` is a list of `(style, text)` tuples. Styles:

| Style | Meaning |
|---|---|
| `h1` | numbered section heading |
| `h2` | subsection heading |
| `p` | paragraph |
| `b` | bullet |
| `box` | small bordered box, first line is its title |
| `img` | `path\|caption\|width_cm` |

## 8.5 Report build gotchas

- `ParagraphStyle(**base, fontSize=...)` raises a duplicate keyword error. Use the `make()`
  helper that does `spec.update(over)`.
- The front page `line()` helper takes 3 arguments, not 2.

## 8.6 Drive link

Currently in `report_content.py`, printed under the synopsis:

```
https://drive.google.com/file/d/1eBcNDpe4yKDJRv7YKbVwHbuWcS2VZ9WY/view?usp=sharing
```

**Confirm with the user before submission.** The user said "i will be ulploading the demo video
to the gdrive add its below sinopis", so its position under the synopsis is intentional.

---

# 9. The report, full text

Verbatim from `report_content.py` as merged. If the repo is lost, the report can be rebuilt from
this section alone.

## 9.1 Metadata

```
TEAM     = "TI3405_D38N"
MEMBERS  = ["AYUSH GUPTA"]
TITLE    = "NAKSHA"
SUBTITLE = "An augmented reality service that plans a home's wiring, and sells the wire"
DATE     = "28 August 2026"
```

## 9.2 Synopsis, 292 words

> A family building a house does not know where anything should go. Not the sockets, not the
> switchboards, not the water heater point. The architect's drawing, where there is one, says
> almost nothing about services. So the decisions get made on site by whoever is standing there.
> Runs are improvised, material is mis-ordered, and nothing is written down. Mumbai Fire Brigade,
> across 26,855 incidents over five years, attributes nearly three in four to electrical faults
> [1], and with no record of what was laid, later renovation is guesswork.
>
> NAKSHA is an app from V-Guard. The owner answers about eight questions, walks each room with
> the phone's LiDAR sensor, and gets a complete electrical design: every light, fan, socket and
> switchboard placed, the points grouped into circuits, the cable and breaker sized for each, and
> the quantity of material the house needs. The design is then projected onto the real walls in
> augmented reality, at full size, before anything is chased.
>
> The design is not produced by a language model. A rule engine produces it, so every decision is
> traceable. The model only runs the conversation.
>
> For the owner this replaces dependence on one electrician with a drawing, a quantity and a
> permanent record. For V-Guard it is a sales channel rather than a product. It can be given away
> free, because the revenue is the wire, the water heater and the chimney it specifies. Services
> are chosen once, during construction, and never re-shopped.
>
> A working prototype exists and designs a real surveyed room into three correctly sized circuits
> and a priced bill of quantities. A paid tier is also proposed, in which a trained partner
> projects the design onto the walls with a line laser so the electrician marks and chases against
> it.

## 9.3 Section 1. The problem

Paragraph: Sharpest outside the metros, which is where the growth is. Land prices in tier 2 and
tier 3 cities are expected to rise 25% to 100% over two to four years as metro prices peak [4],
and those are markets where the owner builds the house, not a developer.

Bullets:
- Often no architect. Where a drawing exists it shows walls and rooms, not services.
- The electrician plans it, executes it, and is the only person who knows what was done.
- Nothing is recorded. Once the plaster is on, the information is gone.
- The owner thinks ten times before drilling one hole in his own wall.
- Sockets end up where the furniture is not. Air conditioners get added later onto circuits never
  sized for them.

Paragraph: Every one of those decisions settles which brand of wire, water heater and chimney
goes into the house. V-Guard sells all of them and is present for none of it.

## 9.4 Section 2. What NAKSHA does

Bullets:
- Asks about eight questions: sanctioned load, bedrooms, occupants, how many air conditioners and
  where, which bathrooms need water heating, what the kitchen will have. Each question is written
  from the answers already given.
- The owner walks each room holding the phone. LiDAR measures walls, doors, windows and
  furniture. Nothing is typed.
- Produces a drawing: every light, fan, socket, switchboard and appliance point placed, conduit
  routed, distribution board sited.
- Produces a circuit schedule: which points share a circuit, breaker rating, cable size,
  connected load, voltage drop.
- Produces a bill of quantities: metres of cable by size, metres of conduit, counts of boxes and
  switchgear, priced.
- Projects the same design onto the actual walls in augmented reality, at full size, before
  anything is cut.
- Each point is ticked off as installed. What remains is an as-built record, a permanent map of
  where the cables actually went. That does not exist today.

## 9.5 Section 3. How it works

**Exhibit, `exhibits/flow-diagram.png`, 15.5 cm.** Caption: How the three stages fit together.
The language model handles the conversation and hands over a profile. Everything that could hurt
somebody happens in the rule engine, where each decision is traceable to a rule.

### 3.1 The conversation
- A language model asks the questions and produces one output: a profile of the household. What
  the family intends to own, not a wiring decision.
- This boundary matters more than anything else here. A model that hallucinates a cable size is a
  fire.
- If the model is unreachable, a fixed question set runs instead and the app behaves identically.

### 3.2 The design engine
- Lighting counts from the lumen method against measured floor area and an illuminance target per
  room type. Socket counts from spacing rules.
- Points grouped into lighting, power and dedicated circuits.
- Distribution board placed by solving for the position that minimises total cable.
- Conduit routed as a rectilinear Steiner minimal tree, the same problem circuit board routers
  solve [5].
- Sizing in a fixed order: breaker chosen from the design current, then a conductor whose ampacity
  covers that breaker. The reverse order is a protection violation, because a breaker rated above
  the cable it protects will not trip before the cable overheats.
- Voltage drop checked and the conductor increased if it fails. Maximum demand calculated with
  diversity and compared against the sanctioned load, so three air conditioners on a 5 kW
  sanction is flagged while the walls are still open.

### 3.3 The augmented reality view
- The user taps two floor corners, which fixes position and rotation exactly. Ceiling height
  comes from the scan.
- Registration is manual and visible on purpose. Automatic alignment drifts on a live site, and
  an overlay confidently in the wrong place is worse than one the user positioned himself.
- The authoritative output is always the dimensioned drawing, never the screen.

## 9.6 Section 4. NAKSHA as a service

Paragraph: The app is the free layer. Above it sits a paid one.

Bullets:
- A trained V-Guard partner arrives with a 3D line laser. It mounts on a tripod or clamps to the
  wall, sits in the middle of the room, and projects the design onto the walls and ceiling as
  real lines.
- The electrician marks and chases against the projection instead of measuring from paper. Socket
  heights, switchboard positions and conduit runs are set out in minutes.
- Commodity hardware, a few thousand rupees, already used by tile and false ceiling contractors.

**Exhibit, `exhibits/laser-projector.jpg`, 8.5 cm.** Caption: A 360 degree line laser with tripod
and wall mount. The marking instrument, not the design tool.

Paragraph: This is not speculative. The equivalent exists at industrial scale in the United
States. Dusty Robotics sends a small robot across a concrete slab printing the building model
directly onto the floor, and has printed onto hundreds of millions of square feet [6].

**Exhibit, `exhibits/dusty-robotics.jpg`, 6.5 cm.** Caption: Dusty Robotics printing a building
model onto a slab. It works on floors, which is where American layout is needed.

Bullets:
- The distinction matters. Dusty prints on the floor because that is where American layout
  happens. Indian services run in walls and ceilings, so a floor printer solves the wrong
  surface.
- A line laser projecting upward and outward is the correct instrument for the same job here.
- This tier does not have to scale. A handful of trained partners in metro cities is enough. Its
  purpose is positioning, not revenue.

## 9.7 Section 5. What this means for the user

Bullets:
- Not completely dependent on one electrician. He has a drawing, so a second opinion becomes
  possible.
- A 3D and augmented reality map of his own wiring, kept for the life of the building. Drilling a
  hole stops being a gamble.
- He knows what quantity of wire and switchgear the house needs, so he buys the right amount and
  overcharging becomes visible.
- He sees a brand that arrived before the wall closed rather than after something failed.
- The electrician is not displaced. He stays legally responsible. What he gets is the load
  calculation done, the sizes decided, the material list totalled, and a defensible answer when
  the owner asks why it costs what it costs.

**Box titled "Story time":**

> A few years ago my family used Berger's Express Painting service. It was expensive. It was not
> available in most pincodes. We used it in one room and nowhere else. To this day my father still
> curses Berger paint.
>
> He also still remembers the brand, exactly, years later. The service never scaled and never
> needed to. What it did was put a premium brand physically inside our house for two days. Asian
> Paints proved the mechanism first with Beautiful Homes and Berger followed [2]. Neither was
> trying to become a painting contractor. They were buying a position.

**Exhibit, `exhibits/berger-express-painting.jpg`, 11 cm.** Caption: Berger's Express Painting
service. A branded crew with branded equipment, inside the customer's house.

## 9.8 Section 6. What V-Guard gets from this

Bullets:
- V-Guard stops being only a trusted brand and becomes a technology first one. On the Forbes
  India and TRA Research list of most respected consumer technology brands, V-Guard currently
  sits behind Havells, Bajaj Electricals, Syska and Cona [3]. That repositioning is hard to buy
  with advertising and cheap to buy with a working app.
- Every design becomes an order. The output is a material schedule in metres and units, mappable
  to V-Guard product codes. Being specified beats advertising to whoever walks into a shop.
- The decision is captured years earlier, during construction, before the owner has any brand
  opinion. Nobody rewires a finished house.
- First hand market data: what is being installed, in which cities, at what load, in what
  quantity. Nobody in this category has that.

Paragraph: The margin case is why it is worth doing. In FY26 V-Guard's revenue grew about 7% to
Rs 5,966 crore while profit after tax fell 1.7% to Rs 308 crore, on an EBITDA margin of 8.8% [7].
Growth is not the problem; margin is. Meanwhile the organised share of the cables and wires
industry rose from roughly 67% in FY22 to about 80% in FY26 [8]. A documented design accelerates
that shift, because you cannot write a conductor size on a drawing and then buy loose unbranded
wire against it.

Paragraph: The channel also already exists. V-Guard runs Rishta, a loyalty programme for
electricians and plumbers with QR scanning and instant payouts [9]. Every major wire brand runs
something similar and all of them are points and rewards schemes. None puts a tool in the
electrician's hand that does actual work.

## 9.9 Section 7. Does it actually work?

Paragraph: A prototype exists: an iOS application and a design engine. It has been run on a real
room, 15 feet by 12 feet with a 10 foot ceiling, surveyed and cross checked against a mesh scan
that measured the footprint to within 1.4%.

Bullets:
- Eleven measured fittings: two lights, a ceiling fan, three switchboards, three sockets, an air
  conditioner, an existing MCB box.
- Three circuits produced: 6 A lighting on 1.5 sq mm, 16 A power on 2.5 sq mm, dedicated 25 A for
  the air conditioner on 4 sq mm.
- Maximum demand 1,959 W against a 4,500 W sanction. Material priced. No code violations raised.

Paragraph: The 25 A circuit is the part worth reading. A one ton air conditioner would normally
get a 16 A breaker. The isolator actually fitted in that room is 25 A, so the engine took the
larger device and raised the conductor to 4 sq mm, whose ampacity is exactly 25 A. A 2.5 sq mm
cable under a 25 A breaker would have been a protection violation. That is the difference between
a drawing and a decoration.

Paragraph: Delivery cost is software cost. No field organisation, no equipment to maintain, nobody
to place in every pincode. That is why the app is the base layer and the laser service sits above
it as an option.

## 9.10 Section 8. What it does not do yet

Bullets:
- The scan captures one room at a time and separate captures share no coordinate frame. Room
  shapes and areas are measured; the arrangement between rooms is approximated. Schedule and
  quantities are unaffected, because they depend on area and room type.
- Augmented reality accuracy on a live site is unproven. The promise is dimensioned guidance, not
  millimetre placement.
- Only the electrical layer is built. Water, gas and duct routing use the same geometry and the
  same router, but are not implemented.
- Liability needs legal structuring. The tool must be a decision aid a licensed contractor signs
  off, not the designer of record.
- Adoption, not technology, is the real risk. If it does not visibly save an electrician time
  from the first use, it will be ignored by the people who decide what gets bought.

Paragraph: Construction is the largest single consumer of cable in India at about 32% of demand
[10]. That is the pipeline. NAKSHA puts V-Guard at the front of it, in the hand of the person
deciding, at the one moment the decision is still open.

## 9.11 References, all 10, all cited inline

1. Addressing India's electrical fire risks, The Hindu, 2026. Delhi Fire Service attributes over
   80% of fires in the capital to electrical faults; Mumbai Fire Brigade, analysing 26,855
   incidents over five years, attributes nearly three in four to the same cause.
2. Asian Paints, Beautiful Homes Service; Berger Paints, Express Painting.
3. Forbes India and TRA Research, Most Respected Consumer Tech Brands, as reported in Forbes
   India, Havells: Making a Brand of a Commodity.
4. Beyond metros, a big realty boom is brewing, The Economic Times Brand Equity, on tier 2 and
   tier 3 land prices.
5. M. Hanan, On Steiner's problem with rectilinear distance, SIAM Journal on Applied Mathematics,
   vol. 14, no. 2, 1966, pp. 255 to 265.
6. Dusty Robotics, FieldPrinter, company deployment figures.
7. V-Guard Industries Limited, audited results for the quarter and year ended 31 March 2026,
   investor presentation.
8. Motilal Oswal Financial Services, Cables and Wires sector update, June 2026, on industry size
   and the organised share.
9. V-Guard Industries Limited, Rishta loyalty programme for electricians and plumbers,
   application listings.
10. CRU Group, State policies and clean energy boost India's cable market, on construction as a
    share of Indian cable demand.

## 9.12 Market facts gathered, for reuse

- V-Guard FY26: revenue about Rs 5,966 crore, up roughly 7%. Profit after tax Rs 308 crore, down
  1.7%. EBITDA margin 8.8%.
- Organised share of Indian cables and wires: roughly 67% in FY22 rising to about 80% in FY26.
- Construction is the largest single consumer of cable in India, about 32% of demand.
- Tier 2 and tier 3 land prices expected to rise 25% to 100% over two to four years.
- V-Guard sits behind Havells, Bajaj Electricals, Syska and Cona on the Forbes India and TRA
  Research most respected consumer tech brands list.
- V-Guard's electrician and plumber loyalty programme is called **Rishta**, with QR scanning and
  instant payouts.

---

# 10. Video, and two stale documents

The user's plan: **a one minute demo video** recorded from the running app, uploaded to Google
Drive, linked under the synopsis. "we are only gonna submit a video of this demo". The demo does
not need to be performed live for judges.

**Neither script in the repo matches this plan. Both need attention.**

## 10.1 `NAKSHA-VIDEO-SCRIPT.md`, stale and factually contradicts the report

Problems, all of them disqualifying as is:
- **Written for 40 seconds, 104 words.** The plan is one minute.
- **Opens with "forty-two percent of building fires here are electrical".** This claim was
  removed from the report because it could not be sourced. See rule 3. Using it in the video
  while the report cites the Mumbai figure is an inconsistency a judge can catch.
- Describes the app as taking "the architect's plan", which is the opposite of the current
  design. NAKSHA scans with LiDAR precisely because there is usually no architect's plan.
- Directs the presenter to screen record `NAKSHA-Diagram.pdf`, a static older diagram, rather
  than the working app.

Worth keeping from it: the channel insight, which is the strongest closing line in either
document. "Every Indian wire brand already has an electrician app. All of them just hand out
loyalty points. Nobody has put a tool in that channel that does actual work." And: "every design
NAKSHA produces is a purchase order for V-Guard wire."

Also reusable: export 1080p MP4 H.264, upload to Drive, set link sharing to anyone with the link,
then paste that link on the cover page.

## 10.2 `VIDEO-SCRIPT.md`, a different project entirely

This is the script for **INVIDIA CORE**, an abandoned earlier idea: putting voltage correction
inside the distribution board, shrinking the transformer by correcting only affected circuits and
only the shortfall voltage in series. 463 words, about 3 minutes, 10 slides. It has nothing to do
with NAKSHA. `INVIDIA-CORE-Slides.pdf` and `INVIDIA-CORE-Executive-Summary.pdf` belong to it too.
**Do not use any of it. Do not let it contaminate the NAKSHA material.**

## 10.3 What the one minute demo should show

From the user directly: "1. Great mesmerising UI, when i open the app it asks me question firstly
about my name then my house details like load and etc then it moves forward to asking few more
relevent questions like how many ac you are planning to put or something and these questions are
made by our llm and answers are fed into that llm to understand my requiment and create a
detailed profile of me."

So: the interview, the scan, the drawing, then the AR overlay. The AR overlay is the main show
even though alignment is imperfect. The controls overlay is hideable so it can be cut cleanly.
Run the server with `NAKSHA_ASBUILT=1` so the real surveyed room is served and the output is
known good.

---

# 11. The user's real room, `asbuilt.py`

Run the server with `NAKSHA_ASBUILT=1` to serve this instead of a live scan. This is what the
demo and the report's section 7 are based on.

**Coordinate frame.** Metres. Origin at the inside corner where Wall 3 meets Wall 4. `x` runs
along Wall 3, `y` runs from Wall 3 towards Wall 1. Heights are above finished floor.

```
                        Wall 1   (y = depth)
        MCB      tube 25W        SB-1        [ Door 2 ]
      +--------------------------------------------------+
      |                                          Door 3  |
 Door 1                                                  |   Wall 2
      |                 (x) fan, centre           Window |   (x = width)
 Wall 4                                                  |
 (x=0) |  cupboard                                    SB |
      +--------------------------------------------------+
              LED 12W          SB
                        Wall 3   (y = 0)
```

`FEET = 0.3048`

| Field | Value |
|---|---|
| name | Ayush's room |
| kind | bedroom |
| width | 15 ft = 4.572 m, along Walls 1 and 3 |
| depth | 12 ft = 3.658 m, Wall 3 to Wall 1 |
| ceiling | 10 ft = 3.048 m |
| sanctioned_load_w | 4500.0 |

**Doors** (`along` is measured from the origin end of that wall to the centre of the opening):

| Wall | along | width | label |
|---|---|---|---|
| 1 | 3.95 | 0.90 | Door 2 |
| 2 | 3.12 | 0.90 | Door 3 |
| 4 | 3.06 | 0.90 | Door 1 (the entry) |

**Window:** wall 2, along 1.80, width 1.20, sill 0.95.

**Fixture:** Cupboard, wall 4, from 0.18 to 2.52, depth 0.60. Not electrical, but the scan sees
it and it belongs on the drawing, because you cannot chase a wall behind a fitted wardrobe.

**Board:** the existing MCB box on Wall 1, x 0.30, y 3.56, h 1.80, label "MCB box".

**The 11 fittings.** Ceiling mounted items leave `h` as None.

| Kind | Label | x | y | h | W | Notes |
|---|---|---|---|---|---|---|
| light | Tubelight 25 W | 1.60 | 3.56 | 2.75 | 25 | Wall 1 |
| switchboard | Switchboard 1 | 2.55 | 3.57 | 1.25 | | Wall 1 |
| socket | 6 A socket, desk | 2.55 | 3.57 | 1.05 | 200 | Wall 1 |
| appliance | Air conditioner | 4.42 | 2.64 | 2.40 | 1500 | Wall 2, `dedicated`, `mcb_amps: 25.0`, category "Air Conditioners" |
| switchboard | AC isolator 25 A | 4.44 | 2.16 | 2.20 | | Wall 2 |
| switchboard | Switchboard 2 | 4.44 | 0.96 | 1.25 | | Wall 2 |
| socket | 6 A socket, bedside | 4.44 | 0.96 | 1.05 | 200 | Wall 2 |
| light | LED 12 W | 2.10 | 0.10 | 2.60 | 12 | Wall 3 |
| switchboard | Switchboard 3 | 2.30 | 0.11 | 1.15 | | Wall 3 |
| socket | 6 A socket, bed | 2.30 | 0.11 | 0.95 | 200 | Wall 3 |
| fan | Ceiling fan 1200 mm | 2.29 | 1.83 | ceiling | 75 | centre |

**Wall 4 carries the cupboard and Door 1 only. Nothing electrical.** This came straight from the
user: "wall four doesn't have any electrcial things just the cuboard and door".

**The AC is forced to 25 A** via `mcb_amps: 25.0` because the isolator actually fitted is 25 A.
Without the override a 1 ton load would get 16 A. The engine then raises the conductor to 4 sq mm
whose ampacity is exactly 25 A. The user was explicit: "only the ac switch will be 25A". This is
the example the report leans on in section 7.

## 11.1 The transposed dimensions, do not "fix" this back

The GLB scan `naksha/28_8_2026.glb` measured an oriented footprint of **4.507 × 3.610 m** and a
height span of **3.098 m**. This revealed that depth and ceiling height had been **transposed**:
the room is **12 ft deep with a 10 ft ceiling**, not 10 ft deep with a 12 ft ceiling. Two
independent 0.56 m errors. Nominal feet are used since the scan agrees to within 1.4%. The
comment in `asbuilt.py` records this.

The user's original verbal figures were "celling hight will be 12 feets, room length is 10 feet,
room width is 15 feet", which is what produced the error. The scan is the authority.

## 11.2 Derivation helpers

`_rectangle(width, depth)`, `_on_wall(wall, along, width, depth)`, `_against_wall(wall, start,
end, depth, ...)`, `floor_plan(survey=None)`, `device_points(survey=None)`,
`requirements(survey=None, ...)`. Point ids are `A001` upward, sorted by kind in the order
switchboard, light, fan, socket, then others.

---

# 12. Hard rules. Do not undo these.

1. **Never put the cable saving numbers in the report.** `benchmark.py` measures that shared tree
   routing saves a mean of 45.8% of cable length, with a further 7.7% from board siting. It was
   in the report and the user had it removed: telling a wire manufacturer the product makes every
   house buy less wire argues against the proposal. The commercial case is which brand gets
   specified, not how much is consumed. A note at the top of `report_content.py` says so.
   Keeping it as feasibility proof was explicitly considered and rejected.
2. **The Berger line is "To this day my father still curses Berger paint".** An earlier agent
   wrote "My father still complains about the price", which the user never said and called out:
   "dude you are halucinating a lot when did i say My father still complains about the price".
   Do not add any detail to that first person account that is not in the source note.
3. **The fire statistic is the Mumbai Fire Brigade figure**, nearly three in four of 26,855
   incidents over five years, from The Hindu 2026, with Delhi Fire Service at over 80% alongside
   it. A previous "42% of building fires" claim was unsourceable and was removed. NCRB 2024 puts
   electrical causes near 17.5% nationally, so 42% matches neither end. Do not reintroduce it.
   **It is still present in `NAKSHA-VIDEO-SCRIPT.md` and must be removed there too.**
4. **No em dashes, and no hyphens used as sentence punctuation, in deliverables.** User
   preference.
5. **The LLM never engineers.** Conversation to profile only. The rule engine does all sizing,
   placement and protection.
6. **Story time is a small bordered box after section 5**, not the opening of the report. User:
   "keep the story time thing small in a box after what does this means for the user section".
7. **Keep content in points and concise.** User: "keep things in points and consise not all" and
   "its really not well written keep the content consise no need to write a lot of referces".
8. **Do not put the "Or design it straight away" button back.** It was removed because it sat
   under the questions link and every tester tapped it, skipping `RoomBriefView` entirely.
9. **Verify before claiming.** The user caught unverified push claims twice. Before saying
   anything is pushed or merged:
   ```bash
   git ls-remote origin <branch>
   gh api repos/AyushIsOn/img/pulls/<N> --jq '.state, .merged'
   ```
10. **`gh pr create` and every `gh pr` / `gh issue` subcommand fail in this sandbox**, they are
    GraphQL backed. Use REST:
    ```bash
    gh api repos/AyushIsOn/img/pulls -f title="..." -f body="..." \
       -f head="<branch>" -f base="main"
    ```
11. **Always push to a new branch and open a new PR.** If a branch's PR is already merged, later
    commits on it are orphaned. This happened: PR #29 merged, then a commit landed on
    `report-docx` with no open PR, needing branch `report-template-exact` and PR #30.
12. **Pull before editing.** A branch cut from `main` before a PR merged will silently give you
    the old `report_content.py`. This happened while writing this document: the stale file still
    had `TEAM = "D38N"`, the 42% claim, and the fabricated Berger line, and was nearly used as
    the source of truth. Always `git fetch && git rebase origin/main` first, then grep for
    `TEAM = "TI3405_D38N"` to confirm you have the corrected file.
13. **Never write the Groq key into a tracked file, including notes and docs.** GitHub push
    protection scans for it and rejects the push. This document originally carried the key in its
    command list and had to be redacted before it could be committed. The key lives only in
    `naksha/solver/.naksha-key`, ignored by `naksha/.gitignore` line 10. The user has it in their
    own records.
14. **Do not add tests unless asked.** Do not run dev servers or watch mode in the sandbox; use
    `--run` style single execution flags.
15. **Add a two or three line brief of what you actually did** to the end of every response.
    Standing user instruction: "ALSO FROM NOW ON REMEMBER TO ADD A SHORT TWO THREE LINE BRIEF
    ABOUT WHAT YOU DID".

## 12.1 Rejected alternatives, so they are not re-proposed

| Rejected | Why |
|---|---|
| Anchoring AR to the room centre with a heading slider | Nobody can tap the centre of a furnished room's floor; it is under the bed |
| Snap to wall / grid alignment in AR | User: "no snap thing this defeats the whole purpose and illusion" |
| Sourcing different exhibit images from the web | Wrong subject matter and unclear licensing |
| Fixing the first interview question by prompt alone | Model kept reverting to "What is the name of the homeowner?" |
| `openai/gpt-oss-20b` as a fallback model | 403, blocked at org level |
| LLM generating the wiring design | A hallucinated cable size is a fire |
| Keeping the 45.8% saving as feasibility proof | Argues against the proposal to a wire manufacturer |
| Using a template docx as a base | It arrived as unreadable compressed bytes |

## 12.2 Fixed build errors, for recognition

- **`Axis has no member 'dx'`, 34 occurrences.** A `wallAxes` rewrite deleted the local `Axis`
  struct, so `SwiftUI.Axis` resolved instead. Fixed by renaming it `PlanAxis` and moving it to
  file scope. It now lives at `PlanCanvasView.swift:9`, used at lines 191, 218 and 219.
- `MeshResource.generateText` takes `alignment:`, not `alignmentMode:`.
- `visualBounds(relativeTo: nil)` was wrong for centring text; use `mesh.bounds.center`.
- `ParagraphStyle(**base, fontSize=...)` duplicate keyword; use the `make()` helper.
- Front page `line()` helper takes 3 arguments, not 2.

---

# 13. What is left

**Before submission**
1. Swap the 3 placeholder exhibit images in Word, right click, Change Picture, then re save the
   PDF.
2. Rewrite the video script for one minute against the working app, removing the 42% claim and
   the architect's plan framing. Keep the loyalty points channel insight as the closing line.
3. Confirm the Drive link and that the video is uploaded with link sharing enabled.
4. Check the front page against the user's template image.

**Optional app work, only if asked.** The user's stated priority order was **D, C, B, A**, and D
(LLM) and C (AR) are done.
- **B**: circuit legibility. Rename `C1`/`C2`/`C3` to plain language and add tap for detail.
- **A**: furniture aware placement using RoomPlan `room.objects`, so a socket is not specified
  behind a wardrobe. `asbuilt.py` already models the cupboard as a `Fixture`, so the drawing side
  has a precedent.
- PDF export of the drawing sheets from the phone.
- AR alignment, if the user reopens it.

**Never**
- Re-add the saving figures.
- Re-add the 42% fire claim.
- Let INVIDIA CORE material into NAKSHA deliverables.

---

# 14. How the user works

- **Time pressured and direct.** "don't think on your own and waste time which we don't have
  listen to me". Answer the question asked, then act. Do not deliberate in the reply.
- **Wants points, not prose.** Concise output.
- **Says when something is good enough and expects that to stick.** For example the AR overlay:
  "lets go with it".
- **Checks claims.** Two unverified push claims were caught. Verify against the remote, then
  report.
- **Catches fabrication.** The Berger line and the 42% statistic were both caught. Do not invent
  detail in first person accounts, and do not state a statistic you cannot source.
- **Discusses before coding when the problem is unclear**, and says so: "lets discuss first then
  code", "but first sit tight and understand the issue then code".
- **Cannot see the terminal or the filesystem.** They are in a browser with a read only file
  explorer. Surface file contents, command output and errors in the reply, and prefer pushing a
  branch or PR so they can read results on GitHub.
- Repo is private, no payment method attached, personal project. The user has said not to lecture
  about API key security.
