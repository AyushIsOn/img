"""A surveyed room: the fittings that are physically in it, where they are.

Measured from a hand drawing and photographs of the room, cross checked against
the LiDAR scan. Positions are not generated here, they are transcribed. The
engine still does the part that needs judgement: grouping the points into final
circuits, routing the conduit, sizing cable against the MCB, and checking
voltage drop and maximum demand.

Coordinates
-----------
Metres. Origin at the inside corner where Wall 3 meets Wall 4. x runs along
Wall 3, y runs from Wall 3 towards Wall 1. Heights are above finished floor.

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
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import networkx as nx

from .design import (Design, build_route_graph, group_circuits,
                     route_circuits, size_circuits)
from .model import (CABLE_TABLE, DevicePoint, Door, Fixture, FloorPlan, Point,
                    Requirements, Room, RoomRequirement, Window,
                    voltage_drop_percent)

FEET = 0.3048

# ---------------------------------------------------------------------------
# THE SURVEY
# ---------------------------------------------------------------------------

ROOM: Dict = {
    "name": "Ayush's room",
    "kind": "bedroom",

    "width": round(15 * FEET, 3),      # 4.572 m, along Wall 1 and Wall 3
    "depth": round(10 * FEET, 3),      # 3.048 m, Wall 3 to Wall 1
    "ceiling": round(12 * FEET, 3),    # 3.658 m

    # Doors, by the wall they are in. `along` is measured from the origin end
    # of that wall to the centre of the opening.
    "doors": [
        {"wall": 1, "along": 3.95, "width": 0.90, "label": "Door 2"},
        {"wall": 2, "along": 2.60, "width": 0.90, "label": "Door 3"},
        {"wall": 4, "along": 2.55, "width": 0.90, "label": "Door 1"},
    ],
    "windows": [
        {"wall": 2, "along": 1.50, "width": 1.20, "sill": 0.95},
    ],

    # Built-in joinery. Not electrical, but the scan sees it and it belongs on
    # the drawing: you cannot chase a wall behind a fitted wardrobe.
    "fixtures": [
        {"name": "Cupboard", "wall": 4, "from": 0.15, "to": 2.10,
         "depth": 0.60},
    ],

    # The distribution board is the existing MCB box on Wall 1.
    "board": {"x": 0.30, "y": 2.95, "h": 1.80, "label": "MCB box"},

    # Fittings. Ceiling mounted items leave `h` as None.
    "points": [
        # --- Wall 1, the desk wall -------------------------------------
        {"kind": "light", "label": "Tubelight 25 W",
         "x": 1.60, "y": 2.95, "h": 2.90, "watts": 25},
        {"kind": "switchboard", "label": "Switchboard 1",
         "x": 2.55, "y": 2.96, "h": 1.25},
        {"kind": "socket", "label": "6 A socket, desk",
         "x": 2.55, "y": 2.96, "h": 1.05, "watts": 200},

        # --- Wall 2, the window wall -----------------------------------
        {"kind": "appliance", "label": "Air conditioner",
         "x": 4.42, "y": 2.20, "h": 2.85, "watts": 1500,
         "dedicated": True, "category": "Air Conditioners",
         # The isolator actually fitted is 25 A, so the circuit is recorded
         # at 25 A rather than the 16 A a 1 ton load would otherwise get.
         "mcb_amps": 25.0},
        {"kind": "switchboard", "label": "AC isolator 25 A",
         "x": 4.44, "y": 1.80, "h": 2.55},
        {"kind": "switchboard", "label": "Switchboard 2",
         "x": 4.44, "y": 0.80, "h": 1.25},
        {"kind": "socket", "label": "6 A socket, bedside",
         "x": 4.44, "y": 0.80, "h": 1.05, "watts": 200},

        # --- Wall 3, the bed wall --------------------------------------
        {"kind": "light", "label": "LED 12 W",
         "x": 2.10, "y": 0.10, "h": 2.85, "watts": 12},
        {"kind": "switchboard", "label": "Switchboard 3",
         "x": 2.30, "y": 0.11, "h": 1.15},
        {"kind": "socket", "label": "6 A socket, bed",
         "x": 2.30, "y": 0.11, "h": 0.95, "watts": 200},

        # --- Ceiling ---------------------------------------------------
        {"kind": "fan", "label": "Ceiling fan 1200 mm",
         "x": 2.29, "y": 1.52, "h": None, "watts": 75},
    ],

    # Wall 4 carries the cupboard and Door 1 only, nothing electrical.

    "sanctioned_load_w": 4500.0,
}


# ---------------------------------------------------------------------------
# Derivation
# ---------------------------------------------------------------------------

def _rectangle(width: float, depth: float) -> List[Point]:
    return [(0.0, 0.0), (round(width, 3), 0.0),
            (round(width, 3), round(depth, 3)), (0.0, round(depth, 3))]


def _on_wall(wall: int, along: float, width: float,
             depth: float) -> Point:
    """Turn a wall number and a distance along it into a plan coordinate."""
    if wall == 1:                       # top, y = depth
        return (round(along, 3), round(depth, 3))
    if wall == 2:                       # right, x = width
        return (round(width, 3), round(along, 3))
    if wall == 3:                       # bottom, y = 0
        return (round(along, 3), 0.0)
    return (0.0, round(along, 3))       # wall 4, left, x = 0


def _against_wall(wall: int, start: float, end: float, depth: float,
                  w: float, d: float) -> List[Point]:
    """A rectangle sitting against a wall, running from `start` to `end`."""
    if wall == 1:                       # far wall, grows downward
        return [(start, d), (end, d), (end, d - depth), (start, d - depth)]
    if wall == 2:                       # right wall, grows left
        return [(w, start), (w, end), (w - depth, end), (w - depth, start)]
    if wall == 3:                       # near wall, grows upward
        return [(start, 0.0), (end, 0.0), (end, depth), (start, depth)]
    return [(0.0, start), (0.0, end), (depth, end), (depth, start)]


def floor_plan(survey: Optional[Dict] = None) -> FloorPlan:
    s = survey or ROOM
    w, d = float(s["width"]), float(s["depth"])
    room = Room(name=s["name"], kind=s["kind"], polygon=_rectangle(w, d))
    doors = [
        Door(position=_on_wall(door["wall"], door["along"], w, d),
             room_a=s["name"], room_b=None, width=float(door["width"]),
             # Door 1 on Wall 4 is the way in to the room.
             is_entry=(door.get("label") == "Door 1"))
        for door in s["doors"]
    ]
    windows = [
        Window(position=_on_wall(win["wall"], win["along"], w, d),
               room=s["name"], width=float(win["width"]),
               sill=float(win.get("sill") or 0.9))
        for win in s.get("windows", [])
    ]
    fixtures = [
        Fixture(name=f["name"],
                polygon=_against_wall(f["wall"], float(f["from"]),
                                      float(f["to"]), float(f["depth"]), w, d))
        for f in s.get("fixtures", [])
    ]
    return FloorPlan(name="Scanned floor", rooms=[room], doors=doors,
                     windows=windows, fixtures=fixtures,
                     ceiling_height=float(s["ceiling"]))


def device_points(survey: Optional[Dict] = None) -> List[DevicePoint]:
    """The surveyed fittings, ordered so the schedule reads sensibly."""
    s = survey or ROOM
    ceiling = float(s["ceiling"])
    order = {"switchboard": 0, "light": 1, "fan": 2, "socket": 3,
             "appliance": 4}
    entries = sorted(s["points"], key=lambda p: (order.get(p["kind"], 9),
                                                 p["x"], p["y"]))
    points: List[DevicePoint] = []
    for i, p in enumerate(entries, start=1):
        h = p.get("h")
        points.append(DevicePoint(
            id=f"A{i:03d}", kind=p["kind"], room=s["name"],
            xy=(round(float(p["x"]), 3), round(float(p["y"]), 3)),
            height=ceiling if h is None else float(h),
            watts=float(p.get("watts") or 0),
            label=p.get("label") or p["kind"].title(),
            dedicated=bool(p.get("dedicated")),
            vguard_category=p.get("category")))
    return points


def requirements(survey: Optional[Dict] = None,
                 overrides: Optional[Dict] = None) -> Requirements:
    """Counts come from the survey, because the fittings are already there.

    Answers collected in the app still arrive, so if the owner asks for more
    lights than are installed the schedule says so.
    """
    s = survey or ROOM
    installed = {
        "lights": sum(1 for p in s["points"] if p["kind"] == "light"),
        "fans": sum(1 for p in s["points"] if p["kind"] == "fan"),
        "sockets": sum(1 for p in s["points"] if p["kind"] == "socket"),
    }
    mine = ((overrides or {}).get("perRoom") or {}).get(s["name"]) or {}
    return Requirements(
        rooms=[RoomRequirement(
            room=s["name"],
            lights=int(mine.get("lights") or installed["lights"]),
            fan=bool(mine.get("fan", installed["fans"] > 0)),
            sockets=int(mine.get("sockets") or installed["sockets"]))],
        appliances=[],
        sanctioned_load_w=float((overrides or {}).get("sanctionedLoadW")
                                or s.get("sanctioned_load_w") or 5000))


# ---------------------------------------------------------------------------
# Design
# ---------------------------------------------------------------------------

def _nearest_node(g: nx.Graph, target: Point) -> Point:
    return min(g.nodes, key=lambda n: math.hypot(n[0] - target[0],
                                                 n[1] - target[1]))


def _apply_recorded_mcbs(circuits, survey: Dict) -> None:
    """Honour an MCB that is actually fitted, rather than re-deriving it.

    A 1 ton air conditioner would be given 16 A by the sizing rules. The
    isolator in this room is 25 A, and on an as-built record what is on the wall
    wins. The cable is then re-selected so it still covers the larger device,
    because protecting a conductor with a breaker above its ampacity is the one
    thing that must never happen.
    """
    wanted = {p["label"]: float(p["mcb_amps"])
              for p in survey["points"] if p.get("mcb_amps")}
    if not wanted:
        return
    for c in circuits:
        target = max((wanted[p.label] for p in c.points
                      if p.label in wanted), default=None)
        if target is None or target <= c.mcb_amps:
            continue
        c.mcb_amps = target
        c.cable_mm2 = next((mm2 for mm2, amps in CABLE_TABLE
                            if amps >= target and mm2 >= c.cable_mm2),
                           CABLE_TABLE[-1][0])
        c.vdrop_percent = round(
            voltage_drop_percent(max(c.design_current, 0.1),
                                 c.route_length, c.cable_mm2), 2)


def design(survey: Optional[Dict] = None,
           overrides: Optional[Dict] = None) -> Design:
    """Design the installation for the surveyed room.

    Mirrors `design_floor` except that placement is skipped, because the points
    are measured, and the board is the MCB box that is already on Wall 1 rather
    than a position the solver chooses.
    """
    s = survey or ROOM
    plan = floor_plan(s)
    reqs = requirements(s, overrides)
    points = device_points(s)

    circuits = group_circuits(points, plan)
    g, _ = build_route_graph(plan)
    board = _nearest_node(g, (float(s["board"]["x"]), float(s["board"]["y"])))
    route_circuits(g, board, circuits, plan)
    size_circuits(circuits)
    _apply_recorded_mcbs(circuits, s)
    return Design(plan, reqs, points, circuits, board, g)
