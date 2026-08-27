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

### Connecting to a live solver

`DesignStore.solverEndpoint` is nil by default, which keeps everything on the
bundled sample. Point it at an HTTP endpoint that accepts a `DesignRequest` and
returns the same JSON, and scanned geometry gets designed for real. There is no
server in this repo yet.

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
- **RoomPlan captures one room at a time.** Stitching several scans into one
  coordinate frame is handled crudely and needs real work.
- **Traced and scanned rooms become axis aligned rectangles.** Fine for the
  rectilinear rooms this targets, wrong for curved or slanted walls.
- **AR registration accuracy on a live site is unproven.** Promise dimensioned
  guidance, not millimetre placement.
- **Routing is modelled on a 0.5 m ceiling grid.** Real chasing follows
  structural constraints the model does not know about.
- **Prices are indicative placeholders**, not a catalogue feed.
