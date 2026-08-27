# NAKSHA, iOS client

SwiftUI app that scans rooms with RoomPlan, collects requirements through an
adaptive conversation, and shows the resulting installation both as a drawing
and as an AR overlay on the real walls.

> **These sources have not been compiled.** They were written outside Xcode, so
> expect to fix a small number of errors on first build. Everything is plain
> SwiftUI, RoomPlan and RealityKit with no third party dependencies, so the
> fixes should be shallow.

---

## Requirements

| | |
|---|---|
| Xcode | 15 or newer |
| Deployment target | iOS 17 |
| Room scanning | LiDAR device, iPhone 12 Pro or later Pro, or iPad Pro |
| AR overlay | any ARKit device |
| Sample design | works in the Simulator |

The scan and AR screens need a real device. The drawing, circuit schedule and
material list all work in the Simulator from the bundled sample.

---

## Opening it

### Option A, XcodeGen

```bash
brew install xcodegen
cd ios
xcodegen generate
open Naksha.xcodeproj
```

### Option B, by hand, about two minutes

1. Xcode, **File, New, Project, iOS, App**.
2. Product name **Naksha**, interface **SwiftUI**, language **Swift**.
3. Save it inside `ios/`, then delete the `ContentView.swift` and
   `NakshaApp.swift` that Xcode created.
4. Drag the `Naksha/Models`, `Naksha/Services` and `Naksha/Views` folders and
   `Naksha/NakshaApp.swift` into the project. Choose **Create groups**.
5. Drag `Naksha/Resources/sample-2bhk.json` in as well, and confirm it appears
   under **Target, Build Phases, Copy Bundle Resources**.
6. **Target, Info**, add `NSCameraUsageDescription` with a short explanation.
   RoomPlan and ARKit both refuse to start without it.
7. Set the deployment target to iOS 17.
8. Build to a device.

---

## What to look at first

Open the app and tap **Open the sample design**. That loads real output from
the Python engine, so the drawing, the circuit schedule and the material list
are all populated immediately with no device or network needed.

| Screen | File | What it shows |
|---|---|---|
| Home | `Views/HomeView.swift` | Three entry paths, plus a live preview of the loaded design |
| Room scan | `Views/RoomScanView.swift` | `RoomCaptureView`, then naming each room |
| Requirements | `Views/RequirementsView.swift` | One adaptive question at a time |
| Drawing | `Views/PlanCanvasView.swift` | The plan drawn on device, same symbols as the PNG sheets |
| AR overlay | `Views/ARWiringView.swift` | Conduit and devices anchored to the real room |
| Material | `Views/DesignTabsView.swift` | Bill of quantities and product categories |

---

## How the pieces fit

```
RoomPlan scan  ─┐
sketch entry   ─┼─→ ScannedRoom[] ─┐
                │                   ├─→ solver ─→ design.json ─→ drawing + AR
QuestionEngine ─┴─→ RequirementSet ─┘
```

`DesignStore` is the only place that decides where a design comes from. Leave
`solverEndpoint` nil and it uses the bundled sample. Point it at a running
solver and the same JSON contract comes back from the real engine.

### Where intelligence is allowed to live

The conversation is the only place a language model belongs, and even there its
job is narrow: ask a sensible next question and turn an answer into a structured
entry. `QuestionEngine` is deterministic today so the flow is testable offline,
and `LLMQuestionSource` is the seam where a model can take over phrasing
without touching anything downstream.

Illuminance, load grouping, board siting, routing and conductor sizing are all
computed by the solver in `../solver`. **A probabilistic model never makes a
safety decision.**

---

## AR registration, and why it is manual

The plan is authored in metres on a floor plane, so placing it in the world
needs an origin, a heading and a ceiling height. The user taps the floor to set
the origin, then adjusts heading and ceiling with two sliders.

This is deliberate. Automatic alignment drifts on a live building site, and an
overlay that is confidently wrong is worse than one the user positioned. The
app should promise dimensioned guidance and reference marks, not millimetre
placement, and the authoritative output is always the printed drawing.

---

## Known gaps

- RoomPlan captures one room at a time, so a floor is several scans. Stitching
  them into a single coordinate frame is handled crudely in `RoomConverter` and
  needs real work.
- `RoomConverter` reduces each room to an axis aligned rectangle. Fine for the
  rectilinear rooms this targets, wrong for curved or slanted walls.
- The remote solver path is written but there is no server in this repo yet.
- Bill of quantities rates are indicative placeholders.
