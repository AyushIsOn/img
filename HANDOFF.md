# NAKSHA, agent handoff

Everything a fresh agent needs to continue this project. Written 28 August 2026 because the
session that built it is ending. Read sections 1, 2 and 9 before touching anything.

---

## 1. The one paragraph version

**NAKSHA** is an entry for the **V-Guard Big Idea Tech Design Competition 2026, Track 4**.
Team **TI3405_D38N**, sole member **AYUSH GUPTA**. It is an iOS app plus a Python solver that
designs a home's electrical wiring: you scan a room with the iPhone's LiDAR, answer a few
questions, and it produces device placement, circuit grouping, a distribution board location,
conduit routing, cable and MCB sizing, and a bill of quantities. It then overlays the conduit
runs in augmented reality so you can see where the wires will go before a wall is chased.

**What is being submitted right now is a Detailed Report plus a one minute demo video.**
Not code. The report is built and verified. The video is recorded by the user from the running
app. Do not start refactoring the app unless the user asks.

---

## 2. Current state, honestly

| Piece | State |
|---|---|
| Python solver, full pipeline | Working |
| iOS app, scan to drawing to AR | Working, builds clean |
| LLM interview on Groq | Working, live |
| Detailed Report, DOCX and PDF | Built and verified |
| AR overlay alignment | **Visibly off. User said "lets go with it".** |
| 3 exhibit images in the report | **Placeholders. Only the user can fix.** |

**Open PR: https://github.com/AyushIsOn/img/pull/30** (branch `report-template-exact`,
base `main`, 7 files, mergeable clean). Everything before it is merged into `main`.

### The two known holes

**Exhibit images.** `vguard-bigidea/exhibits/berger-express-painting.jpg`,
`laser-projector.jpg` and `dusty-robotics.jpg` are **generated placeholders at the correct
aspect ratio**, not real photographs. The user pasted the real images into chat and an agent
cannot write chat attachments to disk. Guessing source URLs was tried and failed. The fix is
manual: open the DOCX in Word, right click each image, **Change Picture**, then re save as PDF.
The layout holds because the placeholders match the real aspect ratios.
**Do not substitute different images found on the web.** That was considered and rejected: wrong
pictures and unclear licensing.

**AR alignment.** See section 6.3. The user accepted it as is for the demo. Do not spend the
next session on it unless asked.

---

## 3. Where things live

Repo `https://github.com/AyushIsOn/img` (private). User's clone `/Users/izhu/Documents/img`.

```
naksha/
  28_8_2026.glb                  LiDAR scan of the user's real room, ground truth for dimensions
  solver/
    serve.py                     HTTP server, the only thing the phone talks to
    run.py                       CLI, renders sheets and BoQ to naksha/docs/examples
    benchmark.py                 measures routing savings. DO NOT put its numbers in the report
    requirements.txt
    naksha/
      model.py       360 ln      dataclasses, geometry helpers, CABLE_TABLE, MCB selection
      design.py      752 ln      THE ENGINE. placement, circuits, board siting, routing, sizing
      interview.py   585 ln      LLM interview, provider detection, key storage, rule fallback
      asbuilt.py     286 ln      the user's real surveyed room, hardcoded
      ingest.py      293 ln      RoomPlan JSON to FloorPlan
      draw.py        371 ln      three drawing sheets
      plans.py       166 ln      sample 1/2/3 BHK plans
  ios/
    project.yml                  XcodeGen spec. There is no .xcodeproj in git, generate it
    Naksha/
      NakshaApp.swift
      DesignSystem/  VGuardTheme.swift, LiquidGlass.swift
      Models/        Design.swift, Interview.swift
      Services/      DesignStore.swift, QuestionEngine.swift, ProductCatalogue.swift,
                     AsBuiltRecord.swift
      Views/         HomeView, InterviewView, RoomScanView, RoomBriefView, PlanCanvasView,
                     ARWiringView, DesignTabsView, RequirementsView, ProfileSummaryView,
                     PlanImportView, SolverSettingsView
vguard-bigidea/
  report_content.py              ALL report text. Single source for both builders
  build_docx.py                  writes NAKSHA-Detailed-Report.docx, then verifies it
  build_report.py                writes NAKSHA-Detailed-Report.pdf, then verifies it
  make_diagram.py                writes exhibits/flow-diagram.png
  exhibits/                      flow-diagram.png (real) + 3 placeholders
  NAKSHA-Detailed-Report.docx    the deliverable
  NAKSHA-Detailed-Report.pdf     the deliverable
  VIDEO-SCRIPT.md, NAKSHA-VIDEO-SCRIPT.md, SOURCE-full-draft.md
  build_pdf.py, build_slides.py, build_naksha_final.py   older, superseded, ignore
```

`build_pdf.py`, `build_slides.py` and `build_naksha_final.py` are from an earlier direction
(there are stray `INVIDIA-CORE-*.pdf` outputs too). The live report path is
`report_content.py` plus `build_docx.py` plus `build_report.py` only.

---

## 4. Commands

```bash
# get current
cd /Users/izhu/Documents/img && git checkout main && git pull

# iOS. There is no committed .xcodeproj, it is generated
cd naksha/ios && xcodegen generate && open Naksha.xcodeproj
#   Signing: set your own team. Needs a LiDAR device, iPhone 12 Pro or later.
#   RoomPlan and ARKit do not run in the simulator.

# solver, on the Mac, phone on the same wifi
cd naksha/solver && pip3 install -r requirements.txt
NAKSHA_ASBUILT=1 python3 serve.py       # serves the user's real room, use this for the demo
python3 serve.py                        # normal mode, designs whatever the phone scanned
#   It prints http://<lan-ip>:8000. Type that into the app's Solver Settings.

# Groq key, stored once, never on the phone.
# The real key is NOT in this repo and must not be committed, see rule 13.
# It is already saved on the user's Mac at naksha/solver/.naksha-key
python3 serve.py --set-key <groq-key>
python3 serve.py --check-llm            # confirms the model answers

# report, all three, in order
cd vguard-bigidea && python3 make_diagram.py && python3 build_docx.py && python3 build_report.py

# solver CLI, renders sheets + BoQ without the phone
cd naksha/solver && python3 run.py
```

Server endpoints, from `serve.py`:

- `GET /health` returns `{status, addresses, plans, interview: "llm"|"rules", model}`
- `GET /sample/<1bhk|2bhk|3bhk>` a full design without scanning
- `POST /design` body `{rooms: [...], ...}` returns the design payload. 400 if `rooms` empty
- `POST /interview` body `{answers: [], profile: {}}` returns the next question

---

## 5. How the solver works

`design_floor(plan, reqs)` in `design.py` runs six stages in order. Each stage's output is the
next one's input, so a bug shows up downstream.

1. **`place_points`** decides what goes where. `lumen_method_count` sizes lighting from room
   area against a lux target. `_wall_slots` puts switchboards on walls while avoiding door
   swings, `_primary_door` finds the entry, `_inset_from_wall` holds a 0.28 m offset, and
   `_perimeter_ring` distributes sockets. Fans and ceiling lights go to a grid.
2. **`group_circuits`** clusters points into circuits via `_cluster`, bounded by max watts and
   max points per circuit. Anything marked `dedicated` gets its own circuit.
3. **`choose_board`** sites the distribution board. It evaluates candidate positions by
   `_mst_cost`, the minimum spanning tree cost from that board to every circuit.
4. **`build_route_graph`** builds a graph of legal conduit paths, walls and ceiling, and
   `route_circuits` runs a Steiner tree approximation over it so circuits **share trunk runs**
   instead of each getting its own cable back to the board.
5. **`size_circuits`** computes design current, picks cable from `CABLE_TABLE` via
   `select_cable`, picks the MCB via `select_mcb`, and checks `voltage_drop_percent`.
6. **`bill_of_quantities`** totals it. `maximum_demand` applies diversity, `validate` returns
   a list of violations.

The point of stage 4 is that shared trunking uses much less cable than one run per point.
**There is a measured figure for this in `benchmark.py`. It must not go in the report.** See
section 9.

---

## 6. The iOS app

### 6.1 Flow

Home to Interview (LLM) to Room scan (RoomPlan) to Room brief (3 questions) to Drawing
(PlanCanvasView) to AR (ARWiringView), with Design tabs for circuits and BoQ.

### 6.2 Real room shapes

`RoomConverter` reads `room.floors[].polygonCorners` from RoomPlan, not bounding boxes, so an
L shaped room stays L shaped. On the solver side `_outline()` preserves the polygon through
`_pack()`. If rooms ever start coming out rectangular, that pair is where it broke.

### 6.3 AR, and why it is misaligned

`ARWiringView.swift`, 699 lines. The relevant types:

- `RoomCorner` enum, four corners, `planPoint(in:)` maps a corner to plan coordinates
- `Placement` holds the two corners the user tapped
- `PlanTransform` built from `Placement` plus `Room`, its `world(_ p: CGPoint, _ height: Float)`
  turns a plan point plus height into a world position
- `ARContainer.Coordinator.render(placement:visibleCircuit:)` builds the entities

**Alignment method: the user taps two floor corners of the real room, and the plan is fitted to
those two points.** This was chosen deliberately. The rejected alternative was anchoring to the
room centre with a heading slider, which fails because in a furnished room nobody can tap the
centre of the floor, it is under the bed.

Conduit is drawn at 40 mm thickness (`thickness: Float = 0.040`). Materials are `UnlitMaterial`
so the runs stay bright and readable on camera. Captions are 3D text. The controls overlay can
be hidden, which exists specifically so the user can record the demo without UI in frame.

It is still visibly off. Two tap corner fitting is sensitive to tap precision and to ARKit's
floor plane estimate. The user accepted it.

### 6.4 The user's real room, `asbuilt.py`

Run the server with `NAKSHA_ASBUILT=1` to serve this instead of a scan. Origin is the inside
corner where Wall 3 meets Wall 4, x along Wall 3, y from Wall 3 towards Wall 1, heights above
finished floor.

- **15 ft wide, 12 ft deep, 10 ft ceiling** (4.572 x 3.658 x 3.048 m)
- 3 doors (walls 1, 2, 4), 1 window (wall 2), cupboard on wall 4
- Board is the existing MCB box on Wall 1 at x 0.30, y 3.56, h 1.80
- 11 fittings: tubelight 25 W and LED 12 W, 1200 mm fan 75 W, 3 switchboards, 3 sockets,
  AC 1500 W, AC isolator
- AC is `dedicated: True` with `mcb_amps: 25.0`, forced because the isolator actually fitted is
  25 A, so it overrides the 16 A a 1 ton load would otherwise get
- Sanctioned load 4500 W
- Wall 4 has no electrical points, only the cupboard and Door 1

**Dimension warning.** The GLB scan measured an oriented footprint of 4.507 x 3.610 m and a
height span of 3.098 m. This revealed that depth and ceiling height had been **transposed**: the
room is 12 ft deep with a 10 ft ceiling, not 10 ft deep with a 12 ft ceiling. Two independent
0.56 m errors. The comment in `asbuilt.py` records this. Do not "correct" it back.

---

## 7. The LLM interview

`interview.py`. Provider is auto detected, Groq is what is in use, model
**`openai/gpt-oss-120b`**. The key lives in `naksha/solver/.naksha-key`, which is git ignored,
written by `--set-key`. The key never reaches the phone; the phone posts to `/interview` and the
Mac calls Groq.

The LLM **only turns conversation into a profile**. It never sizes a cable, picks an MCB, or
places a device. Every decision that could hurt somebody is made by the rule engine. This is a
deliberate architectural boundary and the report makes a point of it. `next_turn` falls back to
`_scripted` if the provider is unavailable, `_fold` merges answers into the profile, and
`requirements_from_profile` converts the profile into solver `Requirements`.

**The first question is hardcoded to "What's your name?"** because the model kept producing
"What is the name of the homeowner?". Prompt only fixes were tried and did not hold.

`RoomBriefView` asks **3 hardcoded per room questions** (how many lights, how many fans, AC and
what capacity) with lumen method advice computed from the scanned area shown under the lighting
question. Hardcoded on purpose, for demo reliability.

### Groq gotchas, each one cost real time

- **Cloudflare 403, body `error code: 1010`.** Cause: no `User-Agent` header. Python's urllib
  default is fingerprinted and blocked. Send one.
- **`response_format: {"type": "json_object"}` is rejected unless the messages contain the
  literal lowercase word "json".** The prompt says "Reply with one json object" for this reason.
- **gpt-oss returns its thinking in `reasoning`, not `reasoning_content`.** Only `content` is
  the answer. Reading the wrong field yields thinking text instead of JSON.
- **8000 tokens per minute limit**, and reasoning bills against it, so
  `MAX_OUTPUT_TOKENS = 900` and `reasoning_effort` is `"low"`.
- **`openai/gpt-oss-20b` returns 403, blocked at the org level.** It is not a usable fallback.
- **GitHub push protection rejects any commit containing the Groq key.** Keep it out of tracked
  files. `.naksha-key` is ignored for this reason.

---

## 8. The report

Built and verified. `report_content.py` holds every word; `build_docx.py` and `build_report.py`
each write their format and then **read their own output back** and assert margins, font,
spacing, embedded image count and size, every required heading, and the absence of any
institution name.

### Brief requirements

PDF, 1.5 line spacing, 3 cm margins, Times New Roman 11 pt, 4000 to 5000 words maximum
excluding exhibits and summary. Synopsis 300 words maximum, must precede the report. Table of
contents required. References at the end, cited inline by serial number.
**No college or university name anywhere.** The user targeted ~2500 words rather than the cap.

### Verified output

| | |
|---|---|
| Synopsis | 292 words |
| Body | 1,681 words |
| References | 10, all cited inline, no orphans either direction |
| Exhibits | 4 of 4 embedded |
| Format | Times New Roman 11 pt, 1.5 spacing, 3 cm margins |
| PDF | 11 pages |
| Checked absent | Manipal, University, College, Institute, School, the saving claim |

### Structure

Front page reproduces the user's template exactly: black `DETAILED REPORT`, competition line in
red, bordered box with team name and three numbered member slots, word count and submission
date, `(First Page)` at the foot. Then synopsis, with the **Google Drive link to the demo video
directly under it**, then table of contents, then:

1. The problem
2. What NAKSHA does
3. How it works (3.1 The conversation, 3.2 The design engine, 3.3 The augmented reality view)
   with the flow diagram as Exhibit 1
4. NAKSHA as a service (laser projector exhibit, Dusty Robotics exhibit)
5. What this means for the user (Berger exhibit, and the Story time box)
6. What V-Guard gets from this
7. Does it actually work?
8. What it does not do yet

Drive link currently in `report_content.py`:
`https://drive.google.com/file/d/1eBcNDpe4yKDJRv7YKbVwHbuWcS2VZ9WY/view?usp=sharing`
**Confirm this with the user before submission.**

The flow diagram is drawn in three bands: what the owner provides, the rule engine, what comes
out. The bands exist to make the LLM boundary from section 7 visible at a glance.

### Report gotchas

- `ParagraphStyle(**base, fontSize=...)` raises duplicate keyword. Use the `make()` helper that
  does `spec.update(over)`.
- The front page `line()` helper takes 3 arguments, not 2.
- The user's template arrived as unreadable compressed bytes, so the front page was rebuilt from
  the rendered image rather than parsed.

---

## 9. Hard rules. Do not undo these.

1. **Never put the cable saving numbers in the report.** The measured benchmark says shared tree
   routing saves a mean of 45.8% of cable length with a further 7.7% from board siting. It was
   in the report and the user had it removed: telling a wire manufacturer that the product makes
   every house buy less wire argues against the proposal. A note in `report_content.py` says so.
   Keeping it as feasibility proof was explicitly considered and rejected.
2. **The Berger line is "still curses Berger paint".** An earlier agent wrote "my father still
   complains about the price", which the user never said. Do not embellish a first person
   account.
3. **The fire statistic is the Mumbai Fire Brigade figure**, nearly three in four of 26,855
   incidents over five years, from The Hindu 2026, with Delhi Fire Service at over 80% alongside
   it. A previous "42% of building fires" claim was unsourceable and was removed. NCRB 2024 puts
   electrical causes near 17.5% nationally, so 42% sits between the two and matches neither.
   Do not reintroduce it.
4. **No em dashes and no hyphens as sentence punctuation in deliverables.** User preference.
5. **The LLM never engineers.** Conversation to profile only. The rule engine does all sizing.
6. **Story time is a small bordered box after section 5**, not the opening of the report.
7. **Do not remove the "Or design it straight away" button back in.** It was removed because it
   sat under the questions link and every tester tapped it, skipping `RoomBriefView` entirely.
8. **Verify before claiming.** The user caught unverified push claims twice. Before saying
   anything is pushed or merged:
   ```bash
   git ls-remote origin <branch>
   gh api repos/AyushIsOn/img/pulls/<N> --jq '.state, .merged'
   ```
9. **`gh pr create` and every `gh pr` / `gh issue` subcommand fail in this sandbox**, they are
   GraphQL backed. Use REST:
   ```bash
   gh api repos/AyushIsOn/img/pulls -f title="..." -f body="..." -f head="<branch>" -f base="main"
   ```
10. **Always push to a new branch and open a new PR.** If a branch's PR is already merged, its
    later commits are orphaned. This exact thing happened: PR #29 merged, then a commit landed
    on `report-docx` with no open PR, and it needed branch `report-template-exact` and PR #30.
11. **Add a two or three line brief about what you did** to every response. Standing user
    instruction.
12. Do not add tests unless asked. Do not run dev servers or watch mode in this sandbox.
13. **Never write the Groq key into a tracked file, including notes and docs.** GitHub push
    protection scans for it and rejects the push. This document originally carried the key in
    its command list and had to be redacted before it could be committed. The key lives only in
    `naksha/solver/.naksha-key`, which is ignored by `naksha/.gitignore` line 10. The user has it
    in their own records.

### Fixed build errors, for recognition

- **`Axis has no member 'dx'`, 34 occurrences.** A `wallAxes` rewrite deleted the local `Axis`
  struct, so `SwiftUI.Axis` resolved instead. Fixed by renaming to `PlanAxis` and moving it to
  file scope in `PlanCanvasView.swift`.
- `MeshResource.generateText` takes `alignment:`, not `alignmentMode:`.
- `visualBounds(relativeTo: nil)` was wrong for centring text, use `mesh.bounds.center`.

---

## 10. What is left

**Before submission**
1. Merge PR #30.
2. Swap the 3 placeholder images in Word, right click, Change Picture, then re save the PDF.
3. Check the front page against the user's template image.
4. Confirm the Drive link and that the video is uploaded and shareable.

**Optional app work, only if asked.** The user's stated priority order was D, C, B, A, and D
(LLM) and C (AR) are done.
- **B**: circuit legibility. Rename `C1`/`C2`/`C3` to plain language, add tap for detail.
- **A**: furniture aware placement using RoomPlan `room.objects`, so a socket is not specified
  behind a wardrobe. `asbuilt.py` already models the cupboard as a `Fixture`, so the drawing
  side has a precedent.
- PDF export of the drawing sheets from the phone.
- AR alignment, if the user reopens it.

---

## 11. User working style

- Time pressured and direct. "don't think on your own and waste time which we don't have."
  Answer the question asked, then act. Do not deliberate in the reply.
- Wants concise output in points, not prose.
- Will say when something is good enough and expects that to stick, for example the AR overlay.
- Checks claims. Two unverified push claims were caught. Verify, then report.
- Cannot see the terminal or the filesystem. They are in a browser with a read only file
  explorer. Surface file contents, command output and errors in the reply, and prefer pushing a
  branch or PR so they can read the result on GitHub.
