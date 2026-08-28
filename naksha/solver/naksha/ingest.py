"""Turn scanned or sketched rooms into a FloorPlan the solver can use.

The honest problem this solves, and its limit:

RoomPlan captures one room per scan, and each scan carries its own ARKit world
origin. Two scans are therefore not in a shared coordinate frame, and nothing in
the captured data says how the rooms adjoin. Pretending to stitch them would
produce a confidently wrong plan.

So this module keeps what the scan genuinely measures, the floor area and the
room type, and approximates what it cannot know, the relative arrangement. Rooms
are reduced to rectangles of the measured area and shelf packed into a connected
layout, with doorways inferred wherever two rooms end up sharing a wall.

That trade is acceptable because the electrical design is driven by area and room
type: area sets the lighting count through the lumen method, type sets the socket
rule and whether a fan belongs there. Absolute geometry matters for the AR
overlay, not for the schedule, so the schedule and the quantities are sound even
while the arrangement is approximate.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from .model import (Appliance, Door, FloorPlan, H_SOCKET_AC,
                    H_SOCKET_COUNTER, H_SOCKET_GENERAL, Point, Requirements,
                    Room, RoomRequirement, polygon_area)

WALL_TOUCH_TOL = 0.05      # metres, two walls this close are treated as shared
MIN_SHARED_WALL = 0.7      # a doorway needs at least this much shared wall


# --------------------------------------------------------------- geometry in
def _bbox_of(polygon: Sequence[Sequence[float]]) -> Tuple[float, float]:
    """Width and depth of a room, from its traced or scanned outline."""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return max(xs) - min(xs), max(ys) - min(ys)


def _rect(x0: float, y0: float, w: float, h: float) -> List[Point]:
    return [(round(x0, 3), round(y0, 3)), (round(x0 + w, 3), round(y0, 3)),
            (round(x0 + w, 3), round(y0 + h, 3)), (round(x0, 3), round(y0 + h, 3))]


def _outline(entry: Dict, label: str = "a room"
             ) -> Tuple[List[Point], float, float]:
    """Recover one room's outline, moved to its own origin, plus its extent.

    The measured polygon is preferred and preserved. Earlier versions reduced
    every room to a width and a depth, which meant a scanned outline was
    rebuilt as a rectangle and all of the shape was thrown away.

    A room whose size cannot be established raises instead of falling back to
    an arbitrary default. Floor area drives the lighting count through the
    lumen method and feeds the socket rules, so inventing a size would produce
    a schedule that looks authoritative and is wrong.
    """
    polygon = entry.get("polygon") or []
    if len(polygon) >= 3:
        pts = [(float(p[0]), float(p[1])) for p in polygon]
        if abs(polygon_area(pts)) > 0.5:
            x0 = min(p[0] for p in pts)
            y0 = min(p[1] for p in pts)
            moved = [(round(p[0] - x0, 3), round(p[1] - y0, 3)) for p in pts]
            w, h = _bbox_of(moved)
            if w > 0 and h > 0:
                return moved, round(w, 2), round(h, 2)

    # No usable outline. Accept an explicit size if one was supplied, which is
    # how a sketched or manually entered room arrives.
    width = entry.get("width") or entry.get("widthM")
    depth = entry.get("depth") or entry.get("depthM") or entry.get("length")
    if width and depth and float(width) > 0 and float(depth) > 0:
        w, h = round(float(width), 2), round(float(depth), 2)
        return _rect(0, 0, w, h), w, h

    area = entry.get("area") or entry.get("areaM2") or entry.get("floor_area")
    if area and float(area) > 0:
        side = round(math.sqrt(float(area)), 2)   # square is the least wrong
        return _rect(0, 0, side, side), side, side

    raise ValueError(
        f"cannot establish the size of {label}: the scan produced no usable "
        f"outline and no area or dimensions were given. Rescan that room.")


# ------------------------------------------------------------- shelf packing
def _pack(rooms: List[Tuple[str, str, List[Point], float, float]]
          ) -> List[Tuple[str, str, List[Point]]]:
    """Lay rooms out in rows so they tile compactly, keeping each room's shape.

    Only the arrangement is invented here. The outline itself is the measured
    one and is carried through untouched apart from a translation, so a room
    that was scanned with a bay or an angled corner still has it.

    Rows are closed once they reach roughly the width of a square floor of the
    same total area, because a single long row inflates every conduit run.
    """
    total_area = sum(w * h for _, _, _, w, h in rooms)
    target_width = max(math.sqrt(total_area) * 1.25,
                       max((w for _, _, _, w, _ in rooms), default=3.0))

    placed: List[Tuple[str, str, List[Point]]] = []
    x = y = 0.0
    row_depth = 0.0
    for name, kind, poly, w, h in rooms:
        if x > 0 and x + w > target_width:
            y += row_depth          # close the row
            x = 0.0
            row_depth = 0.0
        moved = [(round(px + x, 3), round(py + y, 3)) for px, py in poly]
        placed.append((name, kind, moved))
        x += w
        row_depth = max(row_depth, h)
    return placed


# ------------------------------------------------------------- door recovery
def _shared_wall(a: List[Point], b: List[Point]) -> Optional[Point]:
    """Midpoint of the wall two rectangles share, if any.

    Rooms are axis aligned after packing, so this reduces to checking whether
    one room's right edge meets another's left edge, or a top edge meets a
    bottom edge, with enough overlap for a doorway.
    """
    ax0, ay0 = a[0]
    ax1, ay1 = a[2]
    bx0, by0 = b[0]
    bx1, by1 = b[2]

    # vertical wall between them
    for xa, xb in ((ax1, bx0), (bx1, ax0)):
        if abs(xa - xb) <= WALL_TOUCH_TOL:
            lo, hi = max(ay0, by0), min(ay1, by1)
            if hi - lo >= MIN_SHARED_WALL:
                return (round(xa, 3), round((lo + hi) / 2, 3))

    # horizontal wall between them
    for ya, yb in ((ay1, by0), (by1, ay0)):
        if abs(ya - yb) <= WALL_TOUCH_TOL:
            lo, hi = max(ax0, bx0), min(ax1, bx1)
            if hi - lo >= MIN_SHARED_WALL:
                return (round((lo + hi) / 2, 3), round(ya, 3))
    return None


def _connect(rooms: List[Room]) -> List[Door]:
    """A doorway for every shared wall, then a check that the plan is walkable.

    A disconnected plan would leave circuits that cannot be routed, so any room
    left unreachable is joined to the nearest reachable one.
    """
    doors: List[Door] = []
    for i, a in enumerate(rooms):
        for b in rooms[i + 1:]:
            p = _shared_wall(a.polygon, b.polygon)
            if p is not None:
                doors.append(Door(p, a.name, b.name, 0.9))

    # front door on the outer wall of the first room
    first = rooms[0]
    x0, y0 = first.polygon[0]
    x1, _ = first.polygon[2]
    doors.insert(0, Door((round((x0 + x1) / 2, 3), round(y0, 3)),
                         first.name, None, 1.0, is_entry=True))

    # reachability
    adj: Dict[str, set] = {r.name: set() for r in rooms}
    for d in doors:
        if d.room_b:
            adj[d.room_a].add(d.room_b)
            adj[d.room_b].add(d.room_a)
    seen = {rooms[0].name}
    queue = [rooms[0].name]
    while queue:
        cur = queue.pop()
        for nb in adj[cur]:
            if nb not in seen:
                seen.add(nb)
                queue.append(nb)

    for r in rooms:
        if r.name in seen:
            continue
        # join it to whichever reachable room is closest
        target = min((q for q in rooms if q.name in seen),
                     key=lambda q: math.dist(r.center, q.center))
        mid = ((r.center[0] + target.center[0]) / 2,
               (r.center[1] + target.center[1]) / 2)
        doors.append(Door((round(mid[0], 3), round(mid[1], 3)),
                          target.name, r.name, 0.9))
        seen.add(r.name)
    return doors


# ----------------------------------------------------------------- public API
def floorplan_from_scans(scanned: List[Dict],
                         name: str = "Scanned floor",
                         ceiling_height: float = 3.0) -> FloorPlan:
    """Build a FloorPlan from the app's ScannedRoom payloads."""
    if not scanned:
        raise ValueError("no rooms supplied")

    prepared: List[Tuple[str, str, float, float]] = []
    used: Dict[str, int] = {}
    for i, entry in enumerate(scanned):
        raw = (entry.get("name") or f"Room {i + 1}").strip()
        # room names become dictionary keys downstream, so they must be unique
        used[raw] = used.get(raw, 0) + 1
        label = raw if used[raw] == 1 else f"{raw} {used[raw]}"
        kind = (entry.get("kind") or "bedroom").lower()
        poly, w, h = _outline(entry, label)
        prepared.append((label, kind, poly, max(w, 1.0), max(h, 1.0)))

    # living space first, so the front door lands somewhere sensible
    order = {"living": 0, "dining": 1, "passage": 2, "kitchen": 3}
    prepared.sort(key=lambda r: (order.get(r[1], 5), -r[3] * r[4]))

    rooms = [Room(n, k, poly) for n, k, poly in _pack(prepared)]
    return FloorPlan(name, rooms, _connect(rooms), ceiling_height)


_MOUNT = {"ac": H_SOCKET_AC, "geyser": H_SOCKET_AC, "chimney": H_SOCKET_AC,
          "ro": H_SOCKET_COUNTER, "stove": H_SOCKET_COUNTER,
          "ev": H_SOCKET_GENERAL}


def requirements_from_payload(payload: Dict, plan: FloorPlan) -> Requirements:
    """Map the app's RequirementSet onto solver requirements.

    Room names are matched case insensitively and anything referring to a room
    that is not in the plan is dropped rather than silently attached elsewhere.
    """
    by_lower = {r.name.lower(): r.name for r in plan.rooms}

    def resolve(room: Optional[str]) -> Optional[str]:
        if not room:
            return None
        return by_lower.get(room.strip().lower())

    appliances: List[Appliance] = []
    for a in payload.get("appliances", []) or []:
        room = resolve(a.get("room"))
        if room is None:
            continue
        kind = (a.get("kind") or "other").lower()
        watts = float(a.get("watts") or 0)
        appliances.append(Appliance(
            name=a.get("name") or "Appliance",
            watts=watts,
            room=room,
            kind=kind,
            dedicated=bool(a.get("dedicated")),
            mount_height=_MOUNT.get(kind, H_SOCKET_GENERAL),
            vguard_category=a.get("vguardCategory")
                            or a.get("vguard_category")))

    room_reqs: List[RoomRequirement] = []
    for key, answers in (payload.get("perRoom")
                         or payload.get("per_room") or {}).items():
        room = resolve(key)
        if room is None or not isinstance(answers, dict):
            continue
        room_reqs.append(RoomRequirement(
            room=room,
            lights=answers.get("lights"),
            fan=answers.get("fan"),
            sockets=answers.get("sockets")))

    sanctioned = float(payload.get("sanctionedLoadW")
                       or payload.get("sanctioned_load_w") or 5000)
    return Requirements(appliances=appliances, rooms=room_reqs,
                        sanctioned_load_w=sanctioned)


def design_from_request(body: Dict):
    """Full path from the app's POST body to a finished design."""
    from .design import design_floor

    plan = floorplan_from_scans(body.get("rooms") or [])
    reqs = requirements_from_payload(body.get("requirements") or {}, plan)
    return design_floor(plan, reqs)
