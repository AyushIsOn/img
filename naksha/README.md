# NAKSHA

**Design the wiring, then order the wire.**

An iOS app that lets a home owner lay out the electrical services of an
under-construction house in augmented reality, and a deterministic solver that
turns that intent into a code-checked installation design, a set of working
drawings, and a material order.

Built for the V-Guard Big Idea Tech Design Competition 2026, Track 4.
Team **D38N**.

---

## Why this exists

Indian homes are wired from memory. The electrician works without a drawing,
improvises the conduit routes, and leaves no record behind. Roughly 42% of
building fires in India are attributed to electrical short circuits. The codes
already exist and regulations already require a licensed contractor. What is
missing is anything that turns those rules into a drawing someone on site will
actually use, and because there is no drawing, there is no record either.

Wire is also the most commoditised product V-Guard sells. NAKSHA changes what
is being sold: not a coil of wire, but a designed installation that specifies
V-Guard wire.

---

## Repository layout

```
solver/                 the design engine, pure Python, fully testable
  naksha/
    model.py            geometry, requirements schema, code constants
    design.py           placement, grouping, board siting, routing, sizing
    draw.py             the three drawing sheets
    plans.py            sample 1/2/3 BHK plans used for testing
  run.py                CLI: plan in, drawings + BoQ + JSON out
  benchmark.py          measured comparison against current practice
ios/                    SwiftUI + RoomPlan + ARKit client
```

---

## The architecture that matters

The single most important design decision is **where intelligence is allowed
to live**:

> A language model conducts the conversation and nothing else. It fills a
> structured requirements schema. Every engineering decision, illuminance,
> load grouping, board siting, routing and conductor sizing, is made by a
> deterministic, auditable solver, so every output traces back to a rule.
> **A probabilistic model is never permitted to make a safety decision.**

That separation is what makes the output testable, and it is why `design.py`
contains no machine learning at all.

### Pipeline

| Step | Problem | Method |
|---|---|---|
| 1 | How many lights, and where | Lumen method, `N = (E x A) / (lm x CU x LLF)` |
| 2 | Where do switches, sockets and appliances go | Placement rules, perimeter allocation with collision avoidance |
| 3 | Which points share a circuit | Capacitated grouping in room walking order, balanced so no way is wasted |
| 4 | Where does the board go | Facility location, 1-median over the routing graph using a metric-closure MST cost |
| 5 | How does the conduit run | **Obstacle-avoiding rectilinear Steiner tree per circuit**, on a ceiling grid clipped to the rooms and linked at doorways |
| 6 | What size cable and breaker | MCB from design current, conductor sized so its ampacity covers the MCB, then upsized until voltage drop is inside budget |
| 7 | What does it cost | Bill of quantities mapped to product categories |

Step 5 is the interesting one. **House wiring is the same problem as printed
circuit board routing**: place components, group them into nets, and connect
them along right-angle paths using the least total wire. The formal name is the
Rectilinear Steiner Minimum Tree, it is NP-hard in general, and chip designers
have been solving it since the 1970s. A house circuit has 8 to 15 points, so
what is hard at VLSI scale is instant here.

---

## Results

Run on the three sample plans. Two effects are isolated so neither is
overstated.

```
Plan                     m2  Pts  Ckt    Radial   Steiner  Steiner+opt  Topology   Board   Total
1 BHK, 45 sq m           48   32    7     201.3     125.8        114.8     37.5%    8.7%   43.0%
2 BHK, 84 sq m           84   54   12     511.3     280.3        256.3     45.2%    8.6%   49.9%
3 BHK, 128 sq m         130   75   14     834.1     370.0        348.5     55.6%    5.8%   58.2%
MEAN                                                                       46.1%    7.7%   50.4%
```

Lengths are metres of conduit including vertical drops.

- **Topology** replaces one run per point with a shared Steiner tree.
- **Board** replaces the entry-door default with the solver's chosen site.

**Read the topology figure as an upper bound.** Pure radial is the worst case;
an experienced electrician already loops lighting points in and out, which
recovers part of that saving. The board siting figure is the cleaner result,
because it holds topology constant and changes one variable.

### A finding worth calling out

On every sample plan the solver reports that **maximum demand exceeds the
sanctioned load** once diversity is applied. A 2 BHK with three air
conditioners and two water heaters genuinely does exceed a 5 kW sanction.
Nothing in the current process tells a home owner this before the walls are
closed. NAKSHA does.

---

## Running it

```bash
cd solver
pip install -r requirements.txt

python3 run.py 2bhk --out out       # drawings, BoQ CSV, design JSON
python3 benchmark.py                # the table above
```

Outputs per plan:

| File | Contents |
|---|---|
| `*-sheet1-layout.png` | Layout plan, every device point, legend, summary |
| `*-sheet2-circuits.png` | Circuit grouping, conduit routing, circuit schedule |
| `*-sheet3-schematic.png` | Single line diagram, bill of quantities, design checks |
| `*-boq.csv` | Bill of quantities |
| `*-design.json` | Full design, consumed by the iOS client for AR |

---

## Design constants and their sources

Everything a reviewer would want to check is in one place, `model.py`:
target illuminance by room type, luminaire output, coefficient of utilisation
and light loss factor, circuit load and point limits, diversity factors,
conductor ampacity table, minimum conductor sizes, and voltage drop budgets.
Change a constant, rerun, and every drawing updates.

---

## Honest limitations

- **Routing is simplified.** Conduit is modelled on a 0.5 m ceiling grid with
  vertical drops. Real chasing follows structural constraints the model does
  not know about.
- **RoomPlan scans one room at a time**, so a whole floor requires stitching
  several scans. That stitching is a real engineering task, not a detail.
- **AR registration accuracy on a live site is unproven** at the tolerance
  conduit chasing needs. The app should promise dimensioned guidance and
  reference marks, not millimetre placement.
- **A contractor will not use an app.** The deliverable to the trades is a
  printed dimensioned drawing and a material list.
- **Liability.** A licensed contractor is legally responsible for the
  installation, so this is a decision aid he signs off, not the designer of
  record.
- Prices in the bill of quantities are indicative placeholders.
