#!/usr/bin/env python3
"""NAKSHA command line entry point.

    python3 run.py 2bhk --out out/

Produces the three drawing sheets, a bill of quantities as CSV, and the whole
design as JSON so the iOS client can render the same model in AR.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import warnings

warnings.filterwarnings("ignore")

from naksha.design import (bill_of_quantities, design_floor, maximum_demand,
                           validate)
from naksha.draw import all_sheets
from naksha.plans import CATALOGUE


def export_json(d, path: str) -> str:
    payload = {
        "plan": {
            "name": d.plan.name,
            "ceiling_height": d.plan.ceiling_height,
            "rooms": [{"name": r.name, "kind": r.kind,
                       "polygon": r.polygon, "area": round(r.area, 2)}
                      for r in d.plan.rooms],
            "doors": [{"position": dr.position, "room_a": dr.room_a,
                       "room_b": dr.room_b, "width": dr.width,
                       "is_entry": dr.is_entry} for dr in d.plan.doors],
        },
        "board": d.board,
        "points": [{"id": p.id, "kind": p.kind, "room": p.room, "xy": p.xy,
                    "height": p.height, "watts": p.watts, "label": p.label,
                    "vguard_category": p.vguard_category}
                   for p in d.points],
        "circuits": [{"id": c.id, "kind": c.kind,
                      "mcb_amps": c.mcb_amps, "cable_mm2": c.cable_mm2,
                      "connected_watts": c.connected_watts,
                      "route_length_m": c.route_length,
                      "vdrop_percent": c.vdrop_percent,
                      "point_ids": [p.id for p in c.points],
                      "route_edges": [[list(u), list(v)]
                                      for u, v in c.route_edges]}
                     for c in d.circuits],
        "summary": {
            "floor_area_m2": round(d.plan.area, 2),
            "connected_load_w": d.connected_load,
            "maximum_demand_w": maximum_demand(d)["total"],
            "sanctioned_load_w": d.reqs.sanctioned_load_w,
            "conduit_m": d.total_route_length,
        },
        "checks": validate(d),
        "bill_of_quantities": bill_of_quantities(d),
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path


def export_boq_csv(d, path: str) -> str:
    boq = bill_of_quantities(d)
    with open(path, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["Item", "Quantity", "Unit", "Rate (Rs)", "Amount (Rs)"])
        for ln in boq["lines"]:
            wr.writerow([ln["item"], ln["qty"], ln["unit"], ln["rate"],
                         ln["amount"]])
        wr.writerow([])
        wr.writerow(["Material total", "", "", "", boq["total"]])
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description="NAKSHA design engine")
    ap.add_argument("plan", nargs="?", default="2bhk",
                    choices=sorted(CATALOGUE), help="sample plan to design")
    ap.add_argument("--out", default="out", help="output directory")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    mk_plan, mk_reqs = CATALOGUE[args.plan]
    plan, reqs = mk_plan(), mk_reqs()

    d = design_floor(plan, reqs)
    md = maximum_demand(d)
    boq = bill_of_quantities(d)
    issues = validate(d)

    stem = os.path.join(args.out, args.plan)
    sheets = all_sheets(d, stem)
    js = export_json(d, f"{stem}-design.json")
    csvp = export_boq_csv(d, f"{stem}-boq.csv")

    print(f"\n{plan.name}")
    print("-" * 58)
    print(f"  floor area          {plan.area:>10.1f} m2")
    print(f"  device points       {len(d.points):>10}")
    print(f"  final circuits      {len(d.circuits):>10}")
    print(f"  connected load      {d.connected_load:>10.0f} W")
    print(f"  maximum demand      {md['total']:>10.0f} W")
    print(f"  sanctioned load     {reqs.sanctioned_load_w:>10.0f} W")
    print(f"  conduit run         {d.total_route_length:>10.1f} m")
    print(f"  material cost       {boq['total']:>10,.0f} Rs")
    print("-" * 58)
    if issues:
        print("  design notes:")
        for i in issues:
            print(f"    - {i}")
    else:
        print("  all design checks passed")
    print("-" * 58)
    for p in sheets + [js, csvp]:
        print(f"  wrote {p}")
    print()


if __name__ == "__main__":
    main()
