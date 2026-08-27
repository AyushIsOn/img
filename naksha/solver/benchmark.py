#!/usr/bin/env python3
"""Measured comparison of the solver against how the job is done today.

Two effects are isolated, because conflating them would overstate the result:

  A. Routing topology.   Radial (a separate run from the board to every point,
     which is what improvised site wiring produces) versus a shared Steiner
     tree per circuit.
  B. Board siting.       Board dumped at the entry door, which is the usual
     default, versus the facility location chosen by the solver.

Everything is measured on the same placed points and the same circuit grouping,
so the only variable is the thing being tested.
"""

from __future__ import annotations

import sys
import warnings
from typing import Dict, List

warnings.filterwarnings("ignore")

import networkx as nx

from naksha.design import (Design, _snap, build_route_graph, choose_board,
                           design_floor, group_circuits, place_points,
                           route_circuits, size_circuits)
from naksha.model import Circuit, FloorPlan, Point
from naksha.plans import CATALOGUE


def radial_length(g: nx.Graph, board: Point, circuits: List[Circuit],
                  plan: FloorPlan) -> float:
    """Every point fed by its own run back to the board, no shared trunk."""
    b = _snap(g, board)
    d_from_board = nx.single_source_dijkstra_path_length(g, b, weight="weight")
    total = 0.0
    for c in circuits:
        for p in c.points:
            total += d_from_board.get(_snap(g, p.xy), 0.0)
            total += plan.ceiling_height - p.height
    return total


def steiner_length(g: nx.Graph, board: Point, circuits: List[Circuit],
                   plan: FloorPlan) -> float:
    route_circuits(g, board, circuits, plan)
    return sum(c.route_length for c in circuits)


def entry_board(plan: FloorPlan, g: nx.Graph) -> Point:
    """The default: mount the board at the entry, no optimisation."""
    e = plan.entry_door()
    target = e.position if e else plan.rooms[0].center
    return _snap(g, target)


def run(key: str) -> Dict:
    mk_plan, mk_reqs = CATALOGUE[key]
    plan, reqs = mk_plan(), mk_reqs()

    points = place_points(plan, reqs)
    circuits = group_circuits(points, plan)
    g, _ = build_route_graph(plan)

    naive_board = entry_board(plan, g)
    smart_board = choose_board(plan, circuits, g, points)

    radial_naive = radial_length(g, naive_board, circuits, plan)
    steiner_naive = steiner_length(g, naive_board, circuits, plan)
    steiner_smart = steiner_length(g, smart_board, circuits, plan)
    size_circuits(circuits)

    return {
        "plan": plan.name,
        "area": plan.area,
        "points": len(points),
        "circuits": len(circuits),
        "radial_at_entry": radial_naive,
        "steiner_at_entry": steiner_naive,
        "steiner_optimised": steiner_smart,
        "saving_topology_pct": 100.0 * (radial_naive - steiner_naive) /
                               radial_naive,
        "saving_board_pct": 100.0 * (steiner_naive - steiner_smart) /
                            steiner_naive,
        "saving_total_pct": 100.0 * (radial_naive - steiner_smart) /
                            radial_naive,
    }


def main() -> None:
    keys = sys.argv[1:] or ["1bhk", "2bhk", "3bhk"]
    rows = [run(k) for k in keys]

    w = 96
    print("=" * w)
    print("NAKSHA routing benchmark".center(w))
    print("=" * w)
    hdr = (f"{'Plan':<20}{'m2':>7}{'Pts':>5}{'Ckt':>5}"
           f"{'Radial':>10}{'Steiner':>10}{'Steiner+opt':>13}"
           f"{'Topology':>10}{'Board':>8}{'Total':>8}")
    print(hdr)
    print("-" * w)
    for r in rows:
        print(f"{r['plan']:<20}{r['area']:>7.0f}{r['points']:>5}"
              f"{r['circuits']:>5}"
              f"{r['radial_at_entry']:>10.1f}{r['steiner_at_entry']:>10.1f}"
              f"{r['steiner_optimised']:>13.1f}"
              f"{r['saving_topology_pct']:>9.1f}%{r['saving_board_pct']:>7.1f}%"
              f"{r['saving_total_pct']:>7.1f}%")
    print("-" * w)
    n = len(rows)
    print(f"{'MEAN':<20}{'':>7}{'':>5}{'':>5}{'':>10}{'':>10}{'':>13}"
          f"{sum(r['saving_topology_pct'] for r in rows) / n:>9.1f}%"
          f"{sum(r['saving_board_pct'] for r in rows) / n:>7.1f}%"
          f"{sum(r['saving_total_pct'] for r in rows) / n:>7.1f}%")
    print()
    print("Lengths are metres of conduit including vertical drops.")
    print("Topology  = shared Steiner tree instead of one run per point.")
    print("Board     = solver chosen board position instead of the entry door.")
    print("Total     = both effects combined.")
    print()
    print("Caveat, stated because it matters: pure radial is the worst case.")
    print("Experienced electricians loop lighting points in and out, which")
    print("already recovers part of the topology saving. Real practice sits")
    print("between radial and optimal, so the topology figure should be read")
    print("as an upper bound, and the board siting figure as the clean result")
    print("since it holds the topology constant.")


if __name__ == "__main__":
    main()
