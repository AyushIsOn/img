"""Geometry, requirements and code constants for the NAKSHA design engine.

All dimensions are in metres, all power in watts, all voltages in volts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Point = Tuple[float, float]


# ----------------------------------------------------------------- geometry
def dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def manhattan(a: Point, b: Point) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def polygon_area(poly: List[Point]) -> float:
    """Shoelace area, always positive."""
    s = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def centroid(poly: List[Point]) -> Point:
    a = polygon_area(poly)
    if a == 0:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    cx = cy = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    signed = 0.0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        signed += x1 * y2 - x2 * y1
    signed /= 2.0
    return (cx / (6 * signed), cy / (6 * signed))


def point_in_polygon(p: Point, poly: List[Point]) -> bool:
    """Ray casting."""
    x, y = p
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and \
           (x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi):
            inside = not inside
        j = i
    return inside


def edges_of(poly: List[Point]) -> List[Tuple[Point, Point]]:
    return [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]


def project_to_segment(p: Point, a: Point, b: Point) -> Tuple[Point, float]:
    """Closest point on segment ab to p, plus the distance."""
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return a, dist(p, a)
    t = ((px - ax) * dx + (py - ay) * dy) / L2
    t = max(0.0, min(1.0, t))
    q = (ax + t * dx, ay + t * dy)
    return q, dist(p, q)


# ------------------------------------------------------------------- rooms
ROOM_KINDS = ("living", "bedroom", "kitchen", "bath", "utility", "passage",
              "dining", "study", "balcony")


@dataclass
class Door:
    """A doorway linking two rooms, or a room to the outside."""
    position: Point
    room_a: str
    room_b: Optional[str] = None          # None means external
    width: float = 0.9
    is_entry: bool = False


@dataclass
class Room:
    name: str
    kind: str
    polygon: List[Point]

    @property
    def area(self) -> float:
        return polygon_area(self.polygon)

    @property
    def center(self) -> Point:
        return centroid(self.polygon)

    def walls(self) -> List[Tuple[Point, Point]]:
        return edges_of(self.polygon)

    def contains(self, p: Point) -> bool:
        return point_in_polygon(p, self.polygon)


@dataclass
@dataclass
class Window:
    """An opening that admits light. Suppresses sockets beneath it."""
    position: Point
    room: str
    width: float = 1.2
    sill: float = 0.9


@dataclass
class Fixture:
    """Built-in joinery. Not electrical, but the scan sees it and an
    electrician needs it on the drawing: you cannot chase a wall behind a
    fitted wardrobe."""
    name: str
    polygon: List[Point]


@dataclass
class FloorPlan:
    name: str
    rooms: List[Room]
    doors: List[Door] = field(default_factory=list)
    windows: List["Window"] = field(default_factory=list)
    fixtures: List["Fixture"] = field(default_factory=list)
    ceiling_height: float = 3.0

    def room(self, name: str) -> Room:
        for r in self.rooms:
            if r.name == name:
                return r
        raise KeyError(name)

    @property
    def area(self) -> float:
        return sum(r.area for r in self.rooms)

    def entry_door(self) -> Optional[Door]:
        for d in self.doors:
            if d.is_entry:
                return d
        return self.doors[0] if self.doors else None

    def bounds(self) -> Tuple[float, float, float, float]:
        xs = [p[0] for r in self.rooms for p in r.polygon]
        ys = [p[1] for r in self.rooms for p in r.polygon]
        return min(xs), min(ys), max(xs), max(ys)


# ------------------------------------------------------- design code inputs
# Target maintained illuminance by room type, lux.
# Indian interior illumination practice, IS 3646 family.
TARGET_LUX: Dict[str, float] = {
    "living": 150, "bedroom": 120, "kitchen": 200, "bath": 100,
    "utility": 100, "passage": 75, "dining": 150, "study": 300,
    "balcony": 75,
}

# Representative LED luminaire used for the lumen method.
# A common Indian domestic LED panel. Using an under-sized luminaire in the
# lumen method inflates the fixture count, so this reflects what is actually
# bought and fitted.
LUMINAIRE_LUMENS = 1800.0      # 18 W LED panel / batten
LUMINAIRE_WATTS = 18.0
COEFF_UTILISATION = 0.55       # CU, light reaching the working plane
LIGHT_LOSS_FACTOR = 0.80       # LLF, dirt and lamp depreciation

FAN_WATTS = 55.0               # BLDC ceiling fan
FAN_ROOMS = ("living", "bedroom", "dining", "study")

# General purpose socket allowance per room type: one 6 A socket per N m2,
# with a floor and a ceiling on the count.
SOCKET_RULE: Dict[str, Tuple[float, int, int]] = {
    # (m2 per socket, minimum, maximum)
    "living": (6.0, 3, 8), "bedroom": (7.0, 3, 6), "kitchen": (4.0, 3, 8),
    "bath": (0.0, 1, 1), "utility": (8.0, 1, 3), "passage": (0.0, 1, 1),
    "dining": (8.0, 2, 4), "study": (5.0, 3, 6), "balcony": (0.0, 1, 2),
}

SUPPLY_VOLTAGE = 230.0
POWER_FACTOR = 0.95

# Circuit limits. Indian domestic practice: 6 A light/fan circuits and
# 16 A power circuits, with dedicated ways for heavy fixed appliances.
LIGHT_CIRCUIT_MAX_W = 800.0
LIGHT_CIRCUIT_MAX_POINTS = 10
POWER_CIRCUIT_MAX_W = 2500.0
POWER_CIRCUIT_MAX_POINTS = 6
DEDICATED_THRESHOLD_W = 1500.0     # above this a load gets its own way

# Voltage drop budget as a percentage of nominal supply.
VDROP_LIMIT_LIGHTING = 3.0
VDROP_LIMIT_POWER = 5.0

COPPER_RHO = 0.0172               # ohm mm2 per m at 20 C

# Cross section, current carrying capacity in a conduit (conservative).
CABLE_TABLE: List[Tuple[float, float]] = [
    (1.0, 11.0), (1.5, 14.0), (2.5, 18.5), (4.0, 25.0),
    (6.0, 32.0), (10.0, 43.0), (16.0, 57.0),
]

# Minimum conductor size by circuit type. Indian domestic practice does not
# use 1.0 sq mm for final circuits even where ampacity would allow it.
MIN_CABLE_LIGHTING = 1.5
MIN_CABLE_POWER = 2.5

# Diversity factors used to turn connected load into maximum demand.
# Applied as (factor on the largest load, factor on the remainder).
DIVERSITY = {
    "lighting": (1.00, 0.66),
    "sockets": (1.00, 0.40),
    "geyser": (1.00, 0.50),
    "ac": (1.00, 0.75),
    "fixed": (1.00, 0.75),
}

# Mounting heights, metres above floor.
H_SWITCH = 1.25
H_SOCKET_GENERAL = 0.30
H_SOCKET_COUNTER = 1.10
H_SOCKET_AC = 2.10
H_CEILING_POINT = 3.0


# ------------------------------------------------------------- requirements
@dataclass
class Appliance:
    """A fixed appliance the user asked for, mapped to a load."""
    name: str
    watts: float
    room: str
    kind: str                     # 'ac','geyser','chimney','ro','stove','fridge','pump','other'
    dedicated: bool = False
    mount_height: float = H_SOCKET_GENERAL
    vguard_category: Optional[str] = None


@dataclass
class RoomRequirement:
    room: str
    lights: Optional[int] = None      # None means compute by lumen method
    fan: Optional[bool] = None        # None means decide by room kind
    sockets: Optional[int] = None      # None means apply the spacing rule


@dataclass
class Requirements:
    """Structured output of the conversational stage. The language model
    fills this in; it never touches the engineering that follows."""
    appliances: List[Appliance] = field(default_factory=list)
    rooms: List[RoomRequirement] = field(default_factory=list)
    sanctioned_load_w: float = 5000.0

    def for_room(self, name: str) -> RoomRequirement:
        for r in self.rooms:
            if r.room == name:
                return r
        return RoomRequirement(room=name)

    def appliances_in(self, room: str) -> List[Appliance]:
        return [a for a in self.appliances if a.room == room]


# --------------------------------------------------------------- electrical
POINT_KINDS = ("light", "fan", "switchboard", "socket", "appliance")


@dataclass
class DevicePoint:
    """A physical point in the installation."""
    id: str
    kind: str                     # see POINT_KINDS
    room: str
    xy: Point
    height: float
    watts: float = 0.0
    label: str = ""
    dedicated: bool = False
    vguard_category: Optional[str] = None

    @property
    def is_load(self) -> bool:
        return self.kind in ("light", "fan", "socket", "appliance")


@dataclass
class Circuit:
    id: str
    kind: str                     # 'lighting' | 'power' | 'dedicated'
    points: List[DevicePoint]
    mcb_amps: float = 6.0
    cable_mm2: float = 1.5
    route_length: float = 0.0
    vdrop_percent: float = 0.0
    route_edges: List[Tuple[Point, Point]] = field(default_factory=list)

    @property
    def connected_watts(self) -> float:
        return sum(p.watts for p in self.points)

    @property
    def design_current(self) -> float:
        return self.connected_watts / (SUPPLY_VOLTAGE * POWER_FACTOR)


def current_for(watts: float) -> float:
    return watts / (SUPPLY_VOLTAGE * POWER_FACTOR)


def select_cable(design_current: float) -> Tuple[float, float]:
    """Smallest cross section whose ampacity covers the current."""
    for mm2, amps in CABLE_TABLE:
        if amps >= design_current:
            return mm2, amps
    return CABLE_TABLE[-1]


def select_mcb(design_current: float) -> float:
    for a in (6, 10, 16, 20, 25, 32, 40):
        if a >= design_current * 1.25:
            return float(a)
    return 63.0


def voltage_drop_percent(current: float, length_m: float,
                         mm2: float) -> float:
    """Single phase, go and return, resistive approximation."""
    r = COPPER_RHO / mm2                      # ohm per metre
    dv = 2.0 * current * length_m * r
    return 100.0 * dv / SUPPLY_VOLTAGE
