"""The deterministic design engine.

Nothing in this module is probabilistic. Every decision traces to a rule or
a formula, which is what makes the output auditable and safe to act on.

Pipeline:
    1. place_points      lumen method plus placement rules
    2. group_circuits    capacitated grouping under load and count limits
    3. choose_board      facility location, minimises routed conduit
    4. build_route_graph ceiling grid clipped to rooms, linked at doorways
    5. route_circuits    Steiner tree per circuit on that graph
    6. size_circuits     MCB and conductor selection, voltage drop check
    7. bill_of_quantities
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import networkx as nx

from .model import (CABLE_TABLE, COEFF_UTILISATION, DEDICATED_THRESHOLD_W, DIVERSITY,
                    MIN_CABLE_LIGHTING, MIN_CABLE_POWER,
                    FAN_ROOMS, FAN_WATTS, H_CEILING_POINT, H_SOCKET_GENERAL,
                    H_SWITCH, LIGHT_CIRCUIT_MAX_POINTS, LIGHT_CIRCUIT_MAX_W,
                    LIGHT_LOSS_FACTOR, LUMINAIRE_LUMENS, LUMINAIRE_WATTS,
                    POWER_CIRCUIT_MAX_POINTS, POWER_CIRCUIT_MAX_W,
                    SOCKET_RULE, SUPPLY_VOLTAGE, TARGET_LUX,
                    VDROP_LIMIT_LIGHTING, VDROP_LIMIT_POWER, Circuit,
                    DevicePoint, FloorPlan, Point, Requirements, Room,
                    current_for, dist, manhattan, project_to_segment,
                    select_mcb, voltage_drop_percent)

GRID = 0.5          # ceiling routing grid pitch, metres
DOOR_LINK_R = 0.75  # a grid node this close to a door can cross rooms


# ============================================================ 1. placement
def lumen_method_count(room: Room) -> int:
    """N = (E x A) / (lumens x CU x LLF), rounded up, at least one."""
    target = TARGET_LUX.get(room.kind, 150)
    denom = LUMINAIRE_LUMENS * COEFF_UTILISATION * LIGHT_LOSS_FACTOR
    n = math.ceil((target * room.area) / denom)
    return max(1, n)


def _grid_positions(room: Room, n: int,
                    avoid: Optional[Point] = None) -> List[Point]:
    """Spread n ceiling points over the room in a near square grid.

    If `avoid` is given (normally the fan position) any point landing on it is
    pushed radially outward so the two symbols never sit on top of each other.
    """
    xs = [p[0] for p in room.polygon]
    ys = [p[1] for p in room.polygon]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = x1 - x0, y1 - y0
    if n == 1:
        return [room.center]
    # pick rows/cols proportional to the room aspect ratio
    best = None
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        if rows * cols < n:
            continue
        cell_w, cell_h = w / cols, h / rows
        score = abs(cell_w - cell_h)
        if best is None or score < best[0]:
            best = (score, rows, cols)
    _, rows, cols = best
    pts: List[Point] = []
    for r in range(rows):
        for c in range(cols):
            if len(pts) >= n:
                break
            x = x0 + w * (c + 0.5) / cols
            y = y0 + h * (r + 0.5) / rows
            p = (round(x, 3), round(y, 3))
            if room.contains(p):
                pts.append(p)
    # if concave geometry rejected some, fall back to the centre
    while len(pts) < n:
        pts.append(room.center)
    pts = pts[:n]
    if avoid is not None:
        out = []
        for p in pts:
            if dist(p, avoid) < 0.55:
                c = room.center
                vx, vy = p[0] - c[0], p[1] - c[1]
                nrm = math.hypot(vx, vy)
                if nrm < 1e-6:
                    vx, vy, nrm = 1.0, 0.0, 1.0
                cand = (round(p[0] + vx / nrm * 0.85, 3),
                        round(p[1] + vy / nrm * 0.85, 3))
                p = cand if room.contains(cand) else p
            out.append(p)
        pts = out
    return pts


def _primary_door(plan: FloorPlan, room: Room):
    cands = [d for d in plan.doors
             if d.room_a == room.name or d.room_b == room.name]
    if not cands:
        return None
    return min(cands, key=lambda d: dist(d.position, room.center))


def _inset_from_wall(room: Room, p: Point, inset: float = 0.28) -> Point:
    """Nudge a wall point slightly into the room so it renders cleanly."""
    c = room.center
    d = dist(p, c)
    if d == 0:
        return p
    ux, uy = (c[0] - p[0]) / d, (c[1] - p[1]) / d
    return (round(p[0] + ux * inset, 3), round(p[1] + uy * inset, 3))


def _perimeter_ring(room: Room, n: int) -> List[Point]:
    """n evenly spaced points around the room perimeter, inset inward."""
    walls = room.walls()
    perim = sum(dist(a, b) for a, b in walls)
    if perim == 0 or n <= 0:
        return []
    out: List[Point] = []
    step = perim / n
    for k in range(n):
        target = step * (k + 0.5)
        travelled = 0.0
        for a, b in walls:
            seg = dist(a, b)
            if target <= travelled + seg:
                t = (target - travelled) / max(seg, 1e-9)
                p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                q = _inset_from_wall(room, p)
                out.append(q if room.contains(q) else room.center)
                break
            travelled += seg
    return out


def _wall_slots(room: Room, count: int, avoid: List[Point],
                min_gap: float = 0.7) -> List[Point]:
    """Pick `count` perimeter positions that clear everything in `avoid`.

    Oversamples the ring then greedily selects well separated candidates, so
    two appliances in one room never land on the same spot.
    """
    if count <= 0:
        return []
    ring = _perimeter_ring(room, max(count * 4, 8))
    chosen: List[Point] = []
    for p in ring:
        if len(chosen) >= count:
            break
        if all(dist(p, q) > min_gap for q in avoid) and \
           all(dist(p, q) > min_gap for q in chosen):
            chosen.append(p)
    # relax the gap if the room is too small to satisfy it
    i = 0
    while len(chosen) < count and i < len(ring):
        p = ring[i]
        if all(dist(p, q) > 0.3 for q in chosen):
            chosen.append(p)
        i += 1
    while len(chosen) < count:
        chosen.append(room.center)
    return chosen[:count]


def place_points(plan: FloorPlan, reqs: Requirements) -> List[DevicePoint]:
    """Turn geometry plus requirements into physical device points."""
    pts: List[DevicePoint] = []
    seq = 0

    def nid(prefix: str) -> str:
        nonlocal seq
        seq += 1
        return f"{prefix}{seq:03d}"

    for room in plan.rooms:
        rq = reqs.for_room(room.name)
        door = _primary_door(plan, room)
        door_pos = [door.position] if door else []
        switch_xy: Optional[Point] = None

        # ---- fan first, so lighting can be kept clear of it
        want_fan = rq.fan if rq.fan is not None else (room.kind in FAN_ROOMS)
        fan_xy = room.center if want_fan else None
        if want_fan:
            pts.append(DevicePoint(nid("F"), "fan", room.name, room.center,
                                   H_CEILING_POINT, FAN_WATTS,
                                   "BLDC ceiling fan",
                                   vguard_category="Fans"))

        # ---- lights
        n_lights = rq.lights if rq.lights is not None \
            else lumen_method_count(room)
        for p in _grid_positions(room, n_lights, avoid=fan_xy):
            pts.append(DevicePoint(nid("L"), "light", room.name, p,
                                   H_CEILING_POINT, LUMINAIRE_WATTS,
                                   f"LED panel {LUMINAIRE_WATTS:.0f}W",
                                   vguard_category="Lighting"))

        # ---- switchboard beside the primary door
        if door:
            walls = room.walls()
            best = min((project_to_segment(door.position, a, b)
                        for a, b in walls), key=lambda t: t[1])[0]
            # slide along the wall to clear the door opening
            c = room.center
            vx, vy = c[0] - best[0], c[1] - best[1]
            nrm = math.hypot(vx, vy) or 1.0
            side = (-vy / nrm, vx / nrm)
            sw = (best[0] + side[0] * (door.width * 0.5 + 0.2),
                  best[1] + side[1] * (door.width * 0.5 + 0.2))
            if not room.contains(sw):
                sw = (best[0] - side[0] * (door.width * 0.5 + 0.2),
                      best[1] - side[1] * (door.width * 0.5 + 0.2))
            switch_xy = _inset_from_wall(room, sw)
            pts.append(DevicePoint(nid("S"), "switchboard", room.name,
                                   switch_xy, H_SWITCH,
                                   0.0, "Switch plate",
                                   vguard_category="Switchgear"))

        # ---- sockets and appliances share the perimeter, allocated once so
        #      that no two wall devices ever land on the same position
        if rq.sockets is not None:
            n_sock = rq.sockets
        else:
            per, lo, hi = SOCKET_RULE.get(room.kind, (8.0, 1, 4))
            n_sock = 0 if per == 0 else int(room.area / per)
            n_sock = max(lo, min(hi, n_sock))
        appl = reqs.appliances_in(room.name)
        taken: List[Point] = list(door_pos)
        if switch_xy is not None:
            taken.append(switch_xy)
        slots = _wall_slots(room, n_sock + len(appl), taken)

        for p in slots[:n_sock]:
            pts.append(DevicePoint(nid("K"), "socket", room.name, p,
                                   H_SOCKET_GENERAL, 200.0, "6A socket",
                                   vguard_category="Switchgear"))
        for ap, p in zip(appl, slots[n_sock:]):
            pts.append(DevicePoint(
                nid("A"), "appliance", room.name, p, ap.mount_height,
                ap.watts, ap.name,
                dedicated=ap.dedicated or ap.watts >= DEDICATED_THRESHOLD_W,
                vguard_category=ap.vguard_category))

    return pts


# ============================================================= 2. circuits
def room_order(plan: FloorPlan) -> List[str]:
    """Rooms in walking order from the entry, following doorways.

    Circuits are then packed along this order, which keeps each circuit inside
    one room or a run of adjacent rooms, the way an installation is actually
    designed and the way a fault is actually traced.
    """
    adj: Dict[str, List[str]] = {r.name: [] for r in plan.rooms}
    for d in plan.doors:
        if d.room_b and d.room_a in adj and d.room_b in adj:
            adj[d.room_a].append(d.room_b)
            adj[d.room_b].append(d.room_a)
    entry = plan.entry_door()
    start = entry.room_a if entry else plan.rooms[0].name
    seen, order, queue = {start}, [start], [start]
    while queue:
        cur = queue.pop(0)
        for nb in adj.get(cur, []):
            if nb not in seen:
                seen.add(nb)
                order.append(nb)
                queue.append(nb)
    for r in plan.rooms:                       # anything unreachable
        if r.name not in seen:
            order.append(r.name)
    return order


def _cluster(points: List[DevicePoint], max_w: float, max_n: int,
             plan: Optional[FloorPlan] = None) -> List[List[DevicePoint]]:
    """Capacitated grouping that respects room boundaries.

    Points are visited room by room in walking order and packed into circuits
    until a load or count limit is reached. A single room whose own load
    exceeds a limit is split, but circuits never interleave distant rooms.
    """
    if not points:
        return []
    by_room: Dict[str, List[DevicePoint]] = {}
    for p in points:
        by_room.setdefault(p.room, []).append(p)

    order = room_order(plan) if plan else sorted(by_room)
    order = [r for r in order if r in by_room] + \
            [r for r in by_room if r not in order]

    ordered: List[DevicePoint] = []
    for rname in order:
        ordered.extend(sorted(by_room[rname], key=lambda p: (p.xy[1], p.xy[0])))

    # Decide how many circuits are needed, then spread the points evenly over
    # that many. Filling each circuit to its limit and leaving a remainder
    # strands single loads on their own way, which wastes a board position.
    total_w = sum(p.watts for p in ordered)
    n_by_load = math.ceil(total_w / max_w) if max_w > 0 else 1
    n_by_count = math.ceil(len(ordered) / max_n) if max_n > 0 else 1
    n_circuits = max(1, n_by_load, n_by_count)

    groups: List[List[DevicePoint]] = [[] for _ in range(n_circuits)]
    loads = [0.0] * n_circuits
    target = len(ordered) / n_circuits
    idx = 0
    for k, p in enumerate(ordered):
        # advance to the next circuit once this one has taken its share, or if
        # adding the point would break a limit
        while idx < n_circuits - 1 and (
                len(groups[idx]) >= math.ceil(target * (idx + 1)) - sum(
                    len(g) for g in groups[:idx])
                or loads[idx] + p.watts > max_w
                or len(groups[idx]) + 1 > max_n):
            idx += 1
        groups[idx].append(p)
        loads[idx] += p.watts
    groups = [g for g in groups if g]

    # Fold undersized circuits away. A way in the board costs money and a
    # circuit carrying one 18 W lamp is a design smell, so merge any small
    # group into whichever other group shares the most rooms and has capacity.
    def rooms_of(grp):
        return {q.room for q in grp}

    changed = True
    while changed and len(groups) > 1:
        changed = False
        groups.sort(key=len)
        for i, small in enumerate(groups):
            if len(small) > max(2, max_n // 4):
                continue
            w_small = sum(q.watts for q in small)
            best_j, best_overlap = None, -1
            for j, other in enumerate(groups):
                if i == j:
                    continue
                if sum(q.watts for q in other) + w_small > max_w:
                    continue
                if len(other) + len(small) > max_n:
                    continue
                ov = len(rooms_of(small) & rooms_of(other))
                if ov > best_overlap:
                    best_j, best_overlap = j, ov
            if best_j is not None:
                groups[best_j].extend(small)
                groups.pop(i)
                changed = True
                break
    return groups


def group_circuits(points: List[DevicePoint],
                   plan: Optional[FloorPlan] = None) -> List[Circuit]:
    """Split points into lighting, power and dedicated circuits."""
    lighting = [p for p in points
                if p.kind in ("light", "fan") or p.kind == "switchboard"]
    dedicated = [p for p in points if p.dedicated]
    power = [p for p in points
             if p.kind in ("socket", "appliance") and not p.dedicated]

    circuits: List[Circuit] = []
    n = 0

    light_groups = _cluster([p for p in lighting if p.is_load],
                            LIGHT_CIRCUIT_MAX_W, LIGHT_CIRCUIT_MAX_POINTS,
                            plan)

    # A switch plate is fed from exactly one circuit. Where a room's lighting
    # is split across circuits, the plate goes with whichever circuit owns the
    # most points in that room, so it is never energised from two ways.
    boards = [p for p in lighting if p.kind == "switchboard"]
    board_owner: Dict[str, int] = {}
    for b in boards:
        best_i, best_count = 0, -1
        for i, grp in enumerate(light_groups):
            count = sum(1 for q in grp if q.room == b.room)
            if count > best_count:
                best_i, best_count = i, count
        board_owner[b.id] = best_i

    for i, grp in enumerate(light_groups):
        n += 1
        mine = [b for b in boards if board_owner[b.id] == i]
        circuits.append(Circuit(f"C{n}", "lighting", grp + mine))
    for grp in _cluster(power, POWER_CIRCUIT_MAX_W,
                        POWER_CIRCUIT_MAX_POINTS, plan):
        n += 1
        circuits.append(Circuit(f"C{n}", "power", grp))
    for p in dedicated:
        n += 1
        circuits.append(Circuit(f"C{n}", "dedicated", [p]))
    return circuits


# ======================================================== 4. routing graph
def build_route_graph(plan: FloorPlan) -> Tuple[nx.Graph, Dict[Point, str]]:
    """A ceiling grid clipped to the rooms, joined across doorways.

    Conduit is assumed to run on the ceiling plane and drop down walls, which
    is how Indian concealed installations are actually chased. Edges are
    orthogonal, so path lengths are Manhattan by construction.
    """
    g = nx.Graph()
    owner: Dict[Point, str] = {}
    x0, y0, x1, y1 = plan.bounds()
    nx_steps = int((x1 - x0) / GRID) + 2
    ny_steps = int((y1 - y0) / GRID) + 2

    nodes: Dict[Tuple[int, int], Point] = {}
    for i in range(nx_steps):
        for j in range(ny_steps):
            p = (round(x0 + i * GRID, 3), round(y0 + j * GRID, 3))
            for r in plan.rooms:
                if r.contains(p):
                    nodes[(i, j)] = p
                    owner[p] = r.name
                    g.add_node(p)
                    break

    for (i, j), p in nodes.items():
        for di, dj in ((1, 0), (0, 1)):
            q = nodes.get((i + di, j + dj))
            if q is None:
                continue
            same = owner[p] == owner[q]
            near_door = any(dist(p, d.position) < DOOR_LINK_R and
                            dist(q, d.position) < DOOR_LINK_R
                            for d in plan.doors)
            if same or near_door:
                g.add_edge(p, q, weight=GRID)

    # stitch rooms that the grid failed to link, via their doorways
    for d in plan.doors:
        if d.room_b is None:
            continue
        near = sorted((p for p in g.nodes),
                      key=lambda p: dist(p, d.position))[:12]
        a_side = [p for p in near if owner[p] == d.room_a]
        b_side = [p for p in near if owner[p] == d.room_b]
        if a_side and b_side:
            pa = min(a_side, key=lambda p: dist(p, d.position))
            pb = min(b_side, key=lambda p: dist(p, d.position))
            if not g.has_edge(pa, pb):
                g.add_edge(pa, pb, weight=manhattan(pa, pb) or GRID)
    return g, owner


def _snap(g: nx.Graph, p: Point) -> Point:
    return min(g.nodes, key=lambda q: dist(q, p))


# =========================================================== 3. board site
def _mst_cost(nodes: List[Point], root: Point,
              d_root: Dict[Point, float],
              d_pair: Dict[Point, Dict[Point, float]]) -> float:
    """Prim on the metric closure. This is the KMB lower structure and is a
    2-approximation of the Steiner cost, cheap enough to evaluate many
    candidate board positions."""
    if not nodes:
        return 0.0
    INF = float("inf")
    inside = {root}
    best = {n: d_root.get(n, INF) for n in nodes}
    total = 0.0
    todo = set(nodes)
    while todo:
        nxt = min(todo, key=lambda n: best[n])
        w = best[nxt]
        if w == INF:
            todo.discard(nxt)
            continue
        total += w
        todo.remove(nxt)
        inside.add(nxt)
        row = d_pair.get(nxt, {})
        for m in todo:
            cand = row.get(m, INF)
            if cand < best[m]:
                best[m] = cand
    return total


def choose_board(plan: FloorPlan, circuits: List[Circuit],
                 g: nx.Graph, points: Optional[List[DevicePoint]] = None,
                 clearance: float = 0.55) -> Point:
    """Facility location. Pick the site that minimises total routed conduit.

    Candidates are grid nodes in circulation space near the entry door, which
    is where a distribution board is permitted to sit.
    """
    circuit_terms = [sorted({_snap(g, p.xy) for p in c.points})
                     for c in circuits]
    terminals = sorted({t for terms in circuit_terms for t in terms})
    d_pair = {t: nx.single_source_dijkstra_path_length(g, t, weight="weight")
              for t in terminals}

    entry = plan.entry_door()
    prefer = {"passage", "living", "dining", "utility"}
    cands = [p for p in g.nodes
             if any(r.kind in prefer and r.contains(p) for r in plan.rooms)]
    if not cands:
        cands = list(g.nodes)
    # a board cannot be mounted on top of another device
    if points:
        cands = [p for p in cands
                 if all(dist(p, q.xy) > clearance for q in points)] or cands
    if entry:
        cands.sort(key=lambda p: dist(p, entry.position))
    cands = cands[:12]

    best, best_cost = cands[0], float("inf")
    for cand in cands:
        d_cand = nx.single_source_dijkstra_path_length(g, cand,
                                                      weight="weight")
        total = sum(_mst_cost(terms, cand, d_cand, d_pair)
                    for terms in circuit_terms)
        if total < best_cost:
            best, best_cost = cand, total
    return best


# ============================================================== 5. routing
def route_circuits(g: nx.Graph, board: Point,
                   circuits: List[Circuit], plan: FloorPlan) -> None:
    """Steiner tree per circuit, plus the vertical drop to each device."""
    bnode = _snap(g, board)
    for c in circuits:
        terms = {_snap(g, p.xy) for p in c.points} | {bnode}
        horiz = 0.0
        edges: List[Tuple[Point, Point]] = []
        if len(terms) >= 2:
            tree = nx.algorithms.approximation.steiner_tree(
                g, list(terms), weight="weight", method="mehlhorn")
            horiz = tree.size(weight="weight")
            edges = [(u, v) for u, v in tree.edges()]
        drops = sum(plan.ceiling_height - p.height for p in c.points)
        drops += plan.ceiling_height - 1.5      # board itself
        c.route_length = round(horiz + drops, 2)
        c.route_edges = edges


# =============================================================== 6. sizing
def size_circuits(circuits: List[Circuit]) -> None:
    """Select MCB first, then a conductor whose ampacity covers the MCB.

    Protecting a cable with a device rated above the cable's capacity is a
    protection violation, so the ordering matters.
    """
    for c in circuits:
        i_design = c.design_current
        floor_a = 6.0 if c.kind == "lighting" else 16.0
        mcb = max(floor_a, select_mcb(i_design))
        floor_mm2 = MIN_CABLE_LIGHTING if c.kind == "lighting" \
            else MIN_CABLE_POWER
        cable = next((mm2 for mm2, amps in CABLE_TABLE
                      if amps >= mcb and mm2 >= floor_mm2),
                     CABLE_TABLE[-1][0])
        limit = VDROP_LIMIT_LIGHTING if c.kind == "lighting" \
            else VDROP_LIMIT_POWER
        # upsize until the drop is inside budget
        while True:
            vd = voltage_drop_percent(max(i_design, 0.1), c.route_length,
                                      cable)
            if vd <= limit:
                break
            bigger = [mm2 for mm2, _ in CABLE_TABLE if mm2 > cable]
            if not bigger:
                break
            cable = bigger[0]
        c.mcb_amps = mcb
        c.cable_mm2 = cable
        c.vdrop_percent = round(
            voltage_drop_percent(max(i_design, 0.1), c.route_length, cable), 2)


# ================================================================== 7. BoQ
VGUARD_PRICES = {          # indicative unit rates, rupees
    "wire_per_m": {1.5: 14.0, 2.5: 22.0, 4.0: 34.0, 6.0: 49.0, 10.0: 82.0},
    "conduit_per_m": 18.0,
    "switch_plate": 260.0,
    "socket_6a": 95.0,
    "socket_16a": 165.0,
    "led_panel": 420.0,
    "fan_bldc": 3100.0,
    "mcb": 210.0,
    "db_way": 120.0,
    "rccb": 1850.0,
}


@dataclass
class Design:
    plan: FloorPlan
    reqs: Requirements
    points: List[DevicePoint]
    circuits: List[Circuit]
    board: Point
    graph: nx.Graph = field(repr=False, default=None)

    @property
    def connected_load(self) -> float:
        return sum(p.watts for p in self.points)

    @property
    def total_route_length(self) -> float:
        return round(sum(c.route_length for c in self.circuits), 2)


def bill_of_quantities(d: Design) -> Dict:
    wire: Dict[float, float] = {}
    for c in d.circuits:
        wire[c.cable_mm2] = wire.get(c.cable_mm2, 0.0) + c.route_length
    # three cores per circuit run: line, neutral, earth. 10% waste.
    wire = {k: round(v * 3 * 1.10, 1) for k, v in wire.items()}

    counts = {
        "led_panel": sum(1 for p in d.points if p.kind == "light"),
        "fan_bldc": sum(1 for p in d.points if p.kind == "fan"),
        "switch_plate": sum(1 for p in d.points if p.kind == "switchboard"),
        "socket_6a": sum(1 for p in d.points if p.kind == "socket"),
        "socket_16a": sum(1 for p in d.points if p.kind == "appliance"),
        "mcb": len(d.circuits),
        "db_way": len(d.circuits) + 2,
        "rccb": 1,
    }
    conduit_m = round(sum(c.route_length for c in d.circuits) * 1.05, 1)

    cost = 0.0
    lines = []
    for mm2, m in sorted(wire.items()):
        rate = VGUARD_PRICES["wire_per_m"].get(mm2, 25.0)
        amt = m * rate
        cost += amt
        lines.append({"item": f"Cable {mm2} sq mm", "qty": m, "unit": "m",
                      "rate": rate, "amount": round(amt, 2)})
    amt = conduit_m * VGUARD_PRICES["conduit_per_m"]
    cost += amt
    lines.append({"item": "Conduit 20 mm", "qty": conduit_m, "unit": "m",
                  "rate": VGUARD_PRICES["conduit_per_m"],
                  "amount": round(amt, 2)})
    labels = {"led_panel": f"LED panel {LUMINAIRE_WATTS:.0f} W",
              "fan_bldc": "BLDC ceiling fan",
              "switch_plate": "Switch plate", "socket_6a": "6 A socket",
              "socket_16a": "16 A socket", "mcb": "MCB",
              "db_way": "DB way", "rccb": "RCCB 30 mA"}
    for key, qty in counts.items():
        if qty <= 0:
            continue
        rate = VGUARD_PRICES[key]
        amt = qty * rate
        cost += amt
        lines.append({"item": labels[key], "qty": qty, "unit": "no",
                      "rate": rate, "amount": round(amt, 2)})
    return {"lines": lines, "total": round(cost, 2),
            "wire_by_size": wire, "conduit_m": conduit_m}


# ============================================================ orchestration
def design_floor(plan: FloorPlan, reqs: Requirements,
                 points: Optional[List[DevicePoint]] = None) -> Design:
    """Design an installation.

    `points` lets already-measured fittings be supplied instead of generated.
    Everything after placement is unchanged, so a surveyed room still gets real
    circuit grouping, board siting, Steiner routing, cable sizing and checks.
    """
    points = points if points is not None else place_points(plan, reqs)
    circuits = group_circuits(points, plan)
    g, _ = build_route_graph(plan)
    board = choose_board(plan, circuits, g, points)
    route_circuits(g, board, circuits, plan)
    size_circuits(circuits)
    return Design(plan, reqs, points, circuits, board, g)


# ================================================== maximum demand & checks
def _bucket(p: DevicePoint) -> str:
    if p.kind in ("light", "fan"):
        return "lighting"
    if p.kind == "socket":
        return "sockets"
    lbl = (p.label or "").lower()
    if "heater" in lbl or "geyser" in lbl:
        return "geyser"
    if "air conditioner" in lbl or lbl.startswith("ac"):
        return "ac"
    return "fixed"


def maximum_demand(d: "Design") -> Dict[str, float]:
    """Connected load is not demand. Apply diversity per load category:
    the largest item in a category at full value, the rest at its factor."""
    groups: Dict[str, List[float]] = {}
    for p in d.points:
        if p.watts <= 0:
            continue
        groups.setdefault(_bucket(p), []).append(p.watts)
    out: Dict[str, float] = {}
    for cat, ws in groups.items():
        ws.sort(reverse=True)
        first, rest = DIVERSITY.get(cat, (1.0, 0.75))
        out[cat] = round(ws[0] * first + sum(ws[1:]) * rest, 1)
    out["total"] = round(sum(v for k, v in out.items() if k != "total"), 1)
    return out


def validate(d: "Design") -> List[str]:
    """Every check a reviewer would run by hand."""
    issues: List[str] = []
    for c in d.circuits:
        limit = VDROP_LIMIT_LIGHTING if c.kind == "lighting" \
            else VDROP_LIMIT_POWER
        if c.vdrop_percent > limit:
            issues.append(
                f"{c.id}: voltage drop {c.vdrop_percent}% exceeds {limit}%")
        amp = next((a for mm2, a in CABLE_TABLE if mm2 == c.cable_mm2), 0.0)
        if c.mcb_amps > amp:
            issues.append(
                f"{c.id}: MCB {c.mcb_amps:.0f}A exceeds cable capacity "
                f"{amp:.0f}A for {c.cable_mm2} sq mm")
        if c.kind == "lighting" and len(
                [p for p in c.points if p.is_load]) > LIGHT_CIRCUIT_MAX_POINTS:
            issues.append(f"{c.id}: too many points on a lighting circuit")
        if c.kind == "lighting" and c.connected_watts > LIGHT_CIRCUIT_MAX_W:
            issues.append(f"{c.id}: lighting circuit load "
                          f"{c.connected_watts:.0f}W over limit")
        if c.kind == "power" and c.connected_watts > POWER_CIRCUIT_MAX_W:
            issues.append(f"{c.id}: power circuit load "
                          f"{c.connected_watts:.0f}W over limit")
    md = maximum_demand(d)
    if md["total"] > d.reqs.sanctioned_load_w:
        issues.append(
            f"maximum demand {md['total']:.0f}W exceeds sanctioned load "
            f"{d.reqs.sanctioned_load_w:.0f}W, load management needed")
    for r in d.plan.rooms:
        if not any(p.room == r.name and p.kind == "light" for p in d.points):
            issues.append(f"{r.name}: no lighting point")
    return issues
