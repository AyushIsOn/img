"""Sample Indian residential floor plans used for testing and benchmarking.

Coordinates are in metres. Each plan tiles without overlap so the routing
grid can be built directly from the room polygons.
"""

from __future__ import annotations

from typing import List

from .model import (Appliance, Door, FloorPlan, H_SOCKET_AC, H_SOCKET_COUNTER,
                    H_SOCKET_GENERAL, Requirements, Room, RoomRequirement)


def _rect(x0: float, y0: float, x1: float, y1: float):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ------------------------------------------------------------------ 2 BHK
def plan_2bhk() -> FloorPlan:
    """About 84 m2, roughly a 900 sq ft two bedroom flat."""
    rooms = [
        Room("Living",   "living",  _rect(0.0, 0.0, 5.0, 4.5)),
        Room("Kitchen",  "kitchen", _rect(5.0, 0.0, 8.0, 3.2)),
        Room("Bath 1",   "bath",    _rect(8.0, 0.0, 10.5, 3.2)),
        Room("Passage",  "passage", _rect(5.0, 3.2, 10.5, 4.5)),
        Room("Bedroom 1", "bedroom", _rect(0.0, 4.5, 5.0, 8.0)),
        Room("Bedroom 2", "bedroom", _rect(5.0, 4.5, 8.0, 8.0)),
        Room("Bath 2",   "bath",    _rect(8.0, 4.5, 10.5, 8.0)),
    ]
    doors = [
        Door((2.0, 0.0), "Living", None, 1.0, is_entry=True),
        Door((5.0, 1.6), "Living", "Kitchen", 0.9),
        Door((5.0, 3.85), "Living", "Passage", 1.0),
        Door((2.0, 4.5), "Living", "Bedroom 1", 0.9),
        Door((6.5, 4.5), "Passage", "Bedroom 2", 0.9),
        Door((9.2, 4.5), "Passage", "Bath 2", 0.75),
        Door((9.2, 3.2), "Passage", "Bath 1", 0.75),
    ]
    return FloorPlan("2 BHK, 84 sq m", rooms, doors, ceiling_height=3.0)


def reqs_2bhk() -> Requirements:
    """What the conversational stage would have collected from the user."""
    ap = [
        Appliance("Air conditioner 1.5 T", 1800, "Living", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
        Appliance("Television", 150, "Living", "other", False,
                  H_SOCKET_COUNTER, None),
        Appliance("Chimney", 250, "Kitchen", "chimney", False,
                  H_SOCKET_AC, "Kitchen Appliances"),
        Appliance("RO purifier", 60, "Kitchen", "ro", False,
                  H_SOCKET_COUNTER, "Water Purifiers"),
        Appliance("Refrigerator", 200, "Kitchen", "fridge", False,
                  H_SOCKET_GENERAL, None),
        Appliance("Water heater 15 L", 2000, "Bath 1", "geyser", True,
                  H_SOCKET_AC, "Water Heaters"),
        Appliance("Water heater 15 L", 2000, "Bath 2", "geyser", True,
                  H_SOCKET_AC, "Water Heaters"),
        Appliance("Air conditioner 1 T", 1500, "Bedroom 1", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
        Appliance("Air conditioner 1 T", 1500, "Bedroom 2", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
    ]
    rooms = [RoomRequirement("Kitchen", sockets=5)]
    return Requirements(appliances=ap, rooms=rooms, sanctioned_load_w=5000)


# ------------------------------------------------------------------ 1 BHK
def plan_1bhk() -> FloorPlan:
    rooms = [
        Room("Living",   "living",  _rect(0.0, 0.0, 4.2, 4.0)),
        Room("Kitchen",  "kitchen", _rect(4.2, 0.0, 6.8, 2.4)),
        Room("Bath",     "bath",    _rect(4.2, 2.4, 6.8, 4.0)),
        Room("Bedroom",  "bedroom", _rect(0.0, 4.0, 6.8, 7.0)),
    ]
    doors = [
        Door((1.5, 0.0), "Living", None, 1.0, is_entry=True),
        Door((4.2, 1.2), "Living", "Kitchen", 0.9),
        Door((4.2, 3.2), "Living", "Bath", 0.75),
        Door((2.0, 4.0), "Living", "Bedroom", 0.9),
    ]
    return FloorPlan("1 BHK, 45 sq m", rooms, doors, ceiling_height=3.0)


def reqs_1bhk() -> Requirements:
    ap = [
        Appliance("Television", 150, "Living", "other", False,
                  H_SOCKET_COUNTER, None),
        Appliance("Chimney", 250, "Kitchen", "chimney", False,
                  H_SOCKET_AC, "Kitchen Appliances"),
        Appliance("Refrigerator", 200, "Kitchen", "fridge", False,
                  H_SOCKET_GENERAL, None),
        Appliance("Water heater 10 L", 2000, "Bath", "geyser", True,
                  H_SOCKET_AC, "Water Heaters"),
        Appliance("Air conditioner 1 T", 1500, "Bedroom", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
    ]
    return Requirements(appliances=ap, sanctioned_load_w=3000)


# ------------------------------------------------------------------ 3 BHK
def plan_3bhk() -> FloorPlan:
    rooms = [
        Room("Living",    "living",  _rect(0.0, 0.0, 6.0, 5.0)),
        Room("Dining",    "dining",  _rect(6.0, 0.0, 9.5, 3.0)),
        Room("Kitchen",   "kitchen", _rect(9.5, 0.0, 12.5, 3.0)),
        Room("Passage",   "passage", _rect(6.0, 3.0, 12.5, 5.0)),
        Room("Bedroom 1", "bedroom", _rect(0.0, 5.0, 4.5, 9.0)),
        Room("Bedroom 2", "bedroom", _rect(4.5, 5.0, 8.5, 9.0)),
        Room("Bedroom 3", "bedroom", _rect(8.5, 5.0, 12.5, 9.0)),
        Room("Bath 1",    "bath",    _rect(0.0, 9.0, 3.0, 11.0)),
        Room("Bath 2",    "bath",    _rect(3.0, 9.0, 6.0, 11.0)),
        Room("Utility",   "utility", _rect(6.0, 9.0, 8.5, 11.0)),
    ]
    doors = [
        Door((2.0, 0.0), "Living", None, 1.0, is_entry=True),
        Door((6.0, 1.5), "Living", "Dining", 1.2),
        Door((9.5, 1.5), "Dining", "Kitchen", 0.9),
        Door((6.0, 4.0), "Living", "Passage", 1.0),
        Door((7.0, 3.0), "Dining", "Passage", 1.0),
        Door((2.0, 5.0), "Living", "Bedroom 1", 0.9),
        Door((6.5, 5.0), "Passage", "Bedroom 2", 0.9),
        Door((10.5, 5.0), "Passage", "Bedroom 3", 0.9),
        Door((2.0, 9.0), "Bedroom 1", "Bath 1", 0.75),
        Door((4.5, 9.0), "Bedroom 2", "Bath 2", 0.75),
        Door((7.0, 9.0), "Bedroom 2", "Utility", 0.8),
    ]
    return FloorPlan("3 BHK, 128 sq m", rooms, doors, ceiling_height=3.0)


def reqs_3bhk() -> Requirements:
    ap = [
        Appliance("Air conditioner 1.5 T", 1800, "Living", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
        Appliance("Television", 150, "Living", "other", False,
                  H_SOCKET_COUNTER, None),
        Appliance("Chimney", 250, "Kitchen", "chimney", False,
                  H_SOCKET_AC, "Kitchen Appliances"),
        Appliance("RO purifier", 60, "Kitchen", "ro", False,
                  H_SOCKET_COUNTER, "Water Purifiers"),
        Appliance("Refrigerator", 220, "Kitchen", "fridge", False,
                  H_SOCKET_GENERAL, None),
        Appliance("Air conditioner 1 T", 1500, "Bedroom 1", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
        Appliance("Air conditioner 1 T", 1500, "Bedroom 2", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
        Appliance("Air conditioner 1 T", 1500, "Bedroom 3", "ac", True,
                  H_SOCKET_AC, "Air Conditioners"),
        Appliance("Water heater 15 L", 2000, "Bath 1", "geyser", True,
                  H_SOCKET_AC, "Water Heaters"),
        Appliance("Water heater 15 L", 2000, "Bath 2", "geyser", True,
                  H_SOCKET_AC, "Water Heaters"),
        Appliance("Washing machine", 500, "Utility", "other", False,
                  H_SOCKET_GENERAL, None),
        Appliance("Water pump", 750, "Utility", "pump", False,
                  H_SOCKET_GENERAL, "Pumps"),
    ]
    return Requirements(appliances=ap, sanctioned_load_w=7000)


CATALOGUE = {
    "1bhk": (plan_1bhk, reqs_1bhk),
    "2bhk": (plan_2bhk, reqs_2bhk),
    "3bhk": (plan_3bhk, reqs_3bhk),
}
