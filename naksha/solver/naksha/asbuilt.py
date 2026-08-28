"""A surveyed room, with the fittings that are physically in it.

Why this exists, stated plainly.

The generative path guesses where a light or a socket should go, because in an
unbuilt house nothing is there yet. This module is the opposite case: a room that
is already built and already wired, where the positions are not a matter of
opinion. They are measured.

That is not a lesser mode. It is the as-built half of the product, and it is the
half that produces a permanent record. The owner or electrician states where the
existing switchboards, lights, fan and appliance points are, and the engine does
the part that still requires judgement: grouping them into final circuits, siting
the board, routing the conduit as a Steiner tree, sizing cable against the MCB,
and checking voltage drop and maximum demand.

So nothing here fakes the engineering. It replaces a guess with a measurement.

Coordinates
-----------
Metres, with the origin at the inside face of the bottom left corner as the room
is drawn. x runs right along the door wall, y runs away from it. Heights are
above finished floor level.

    y
    ^
    |   +-------------------+  <- far wall
    |   |                   |
    |   |                   |
    |   +------[ door ]-----+  <- door wall, y = 0
    +---------------------------> x
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .model import (Door, DevicePoint, FloorPlan, Requirements, Room,
                    RoomRequirement)

# ---------------------------------------------------------------------------
# THE SURVEY.
#
# Replace these with the measurements from the paper drawing. Everything else
# in the file is derived, so this is the only block that changes.
#
# Scanned area was 14.6 m2, and 4.30 x 3.40 gives 14.62, so these are a
# placeholder consistent with the scan until the real dimensions arrive.
# ---------------------------------------------------------------------------

ROOM: Dict = {
    "name": "Ayush's room",
    "kind": "bedroom",
    "width": 4.30,          # along the door wall
    "depth": 3.40,          # away from the door wall
    "ceiling": 2.83,        # measured on site with the AR slider

    # Distance from the left corner to the centre of the door, and its width.
    "door": {"along": 0.95, "width": 0.90},

    # Windows suppress sockets beneath them. Same convention as the door.
    "windows": [
        {"wall": "far", "along": 2.10, "width": 1.20},
    ],

    # The fittings actually on the walls and ceiling.
    #
    #   kind        light | fan | switchboard | socket | appliance
    #   x, y        metres from the bottom left corner
    #   h           height above floor, ceiling fittings use the ceiling height
    #   watts       nameplate rating, 0 for a switch plate
    "points": [
        {"kind": "switchboard", "label": "Main switch plate",
         "x": 0.45, "y": 0.12, "h": 1.25, "watts": 0},

        {"kind": "light", "label": "Tubelight 25 W",
         "x": 2.15, "y": 2.55, "h": None, "watts": 25},
        {"kind": "light", "label": "LED panel 12 W",
         "x": 1.20, "y": 1.10, "h": None, "watts": 12},

        {"kind": "fan", "label": "Ceiling fan 1200 mm",
         "x": 2.15, "y": 1.70, "h": None, "watts": 75},

        {"kind": "socket", "label": "6 A socket",
         "x": 0.45, "y": 1.90, "h": 0.30, "watts": 200},
        {"kind": "socket", "label": "6 A socket, desk",
         "x": 3.85, "y": 2.60, "h": 0.90, "watts": 200},

        {"kind": "appliance", "label": "Air conditioner 1 T",
         "x": 3.30, "y": 3.28, "h": 2.20, "watts": 1500,
         "dedicated": True, "category": "Air Conditioners"},
    ],

    "sanctioned_load_w": 4500.0,
}


# ---------------------------------------------------------------------------
# Derivation. Nothing below needs editing when the survey changes.
# ---------------------------------------------------------------------------

def _rectangle(width: float, depth: float) -> List:
    return [(0.0, 0.0), (round(width, 3), 0.0),
            (round(width, 3), round(depth, 3)), (0.0, round(depth, 3))]


def floor_plan(survey: Optional[Dict] = None) -> FloorPlan:
    s = survey or ROOM
    room = Room(name=s["name"], kind=s["kind"],
                polygon=_rectangle(s["width"], s["depth"]))
    door = Door(position=(round(float(s["door"]["along"]), 3), 0.0),
                room_a=s["name"], room_b=None,
                width=float(s["door"]["width"]), is_entry=True)
    return FloorPlan(name="Scanned floor", rooms=[room], doors=[door],
                     ceiling_height=float(s["ceiling"]))


def device_points(survey: Optional[Dict] = None) -> List[DevicePoint]:
    """The surveyed fittings, in the order the schedule should read."""
    s = survey or ROOM
    ceiling = float(s["ceiling"])
    order = {"switchboard": 0, "light": 1, "fan": 2, "socket": 3,
             "appliance": 4}
    entries = sorted(s["points"], key=lambda p: order.get(p["kind"], 9))

    points: List[DevicePoint] = []
    for i, p in enumerate(entries, start=1):
        height = p.get("h")
        points.append(DevicePoint(
            id=f"A{i:03d}",
            kind=p["kind"],
            room=s["name"],
            xy=(round(float(p["x"]), 3), round(float(p["y"]), 3)),
            height=ceiling if height is None else float(height),
            watts=float(p.get("watts") or 0),
            label=p.get("label") or p["kind"].title(),
            dedicated=bool(p.get("dedicated")),
            vguard_category=p.get("category")))
    return points


def requirements(survey: Optional[Dict] = None,
                 overrides: Optional[Dict] = None) -> Requirements:
    """Requirements consistent with what was surveyed.

    Counts come from the survey rather than the lumen method, because the
    fittings are already installed. The per-room answers still arrive so the
    schedule reflects what the owner said, and any extra appliance they asked
    for is added on top.
    """
    s = survey or ROOM
    lights = sum(1 for p in s["points"] if p["kind"] == "light")
    fans = sum(1 for p in s["points"] if p["kind"] == "fan")
    sockets = sum(1 for p in s["points"] if p["kind"] == "socket")

    answers = (overrides or {}).get("perRoom", {}) or {}
    mine = answers.get(s["name"]) or {}

    return Requirements(
        rooms=[RoomRequirement(room=s["name"],
                                 lights=int(mine.get("lights") or lights),
                                 fan=bool(mine.get("fan", fans > 0)),
                                 sockets=int(mine.get("sockets") or sockets))],
        appliances=[],
        sanctioned_load_w=float(
            (overrides or {}).get("sanctionedLoadW")
            or s.get("sanctioned_load_w") or 5000))
