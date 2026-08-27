"""Drawing generation.

Produces the sheets an electrician or contractor would actually work from:
    sheet 1  layout plan with every device point
    sheet 2  circuit and conduit routing plan
    sheet 3  distribution board schedule and single line diagram
"""

from __future__ import annotations

from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from .design import Design, bill_of_quantities, maximum_demand, validate
from .model import Circuit, DevicePoint, FloorPlan

INK = "#1b1b1b"
MUTED = "#8a8a8a"
WALL = "#1b1b1b"
ROOMFILL = "#f7f6f4"
ACCENT = "#1f6e5a"
CYCLE = ["#1f6e5a", "#b8472a", "#2f5d8a", "#8a6d1f", "#6b3f8a",
         "#3f8a7d", "#a8443f", "#4a6f2f", "#8a5a2f", "#2f6f8a",
         "#7a2f5a", "#5a7a2f", "#2f4a7a", "#7a5a2f", "#4a2f7a"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7.5,
    "axes.linewidth": 0.6,
})


# ------------------------------------------------------------------ helpers
def _draw_shell(ax, plan: FloorPlan, label_rooms: bool = True) -> None:
    for r in plan.rooms:
        xs = [p[0] for p in r.polygon] + [r.polygon[0][0]]
        ys = [p[1] for p in r.polygon] + [r.polygon[0][1]]
        ax.fill(xs, ys, color=ROOMFILL, zorder=0)
        ax.plot(xs, ys, color=WALL, lw=1.6, zorder=2, solid_joinstyle="miter")
        if label_rooms:
            c = r.center
            ax.text(c[0], c[1] + 0.42, r.name.upper(), ha="center",
                    va="center", fontsize=6.4, color=INK, weight="bold",
                    zorder=6)
            ax.text(c[0], c[1] + 0.06, f"{r.area:.1f} m\u00b2", ha="center",
                    va="center", fontsize=5.6, color=MUTED, zorder=6)
    # doorways drawn as white gaps with a swing arc
    for d in plan.doors:
        ax.plot([d.position[0]], [d.position[1]], marker="s", ms=3.2,
                color="white", mec=MUTED, mew=0.6, zorder=4)
    ax.set_aspect("equal")
    ax.axis("off")


def _sym_light(ax, p, colr=INK):
    ax.add_patch(plt.Circle(p, 0.16, fill=True, fc="white", ec=colr,
                            lw=0.8, zorder=7))
    r = 0.113
    ax.plot([p[0] - r, p[0] + r], [p[1] - r, p[1] + r], color=colr, lw=0.7,
            zorder=8)
    ax.plot([p[0] - r, p[0] + r], [p[1] + r, p[1] - r], color=colr, lw=0.7,
            zorder=8)


def _sym_fan(ax, p, colr=INK):
    ax.add_patch(plt.Circle(p, 0.2, fill=True, fc="white", ec=colr, lw=0.8,
                            zorder=7))
    for dx, dy in ((0.19, 0), (0, 0.19), (-0.19, 0), (0, -0.19)):
        ax.plot([p[0], p[0] + dx], [p[1], p[1] + dy], color=colr, lw=0.8,
                zorder=8)


def _sym_switch(ax, p, colr=INK):
    ax.add_patch(mpatches.Rectangle((p[0] - 0.11, p[1] - 0.11), 0.22, 0.22,
                                    fc=colr, ec=colr, lw=0.6, zorder=7))


def _sym_socket(ax, p, colr=INK):
    ax.add_patch(mpatches.Wedge(p, 0.17, 0, 180, fc="white", ec=colr,
                                lw=0.8, zorder=7))
    ax.plot([p[0] - 0.17, p[0] + 0.17], [p[1], p[1]], color=colr, lw=0.8,
            zorder=8)


def _sym_appliance(ax, p, colr=INK):
    ax.add_patch(mpatches.Rectangle((p[0] - 0.15, p[1] - 0.15), 0.30, 0.30,
                                    fc="white", ec=colr, lw=0.9, zorder=7))
    ax.plot([p[0] - 0.15, p[0] + 0.15], [p[1] - 0.15, p[1] + 0.15],
            color=colr, lw=0.6, zorder=8)


def _sym_board(ax, p):
    ax.add_patch(mpatches.Rectangle((p[0] - 0.28, p[1] - 0.20), 0.56, 0.40,
                                    fc=ACCENT, ec=ACCENT, lw=1.0, zorder=9))
    ax.text(p[0], p[1], "DB", ha="center", va="center", color="white",
            fontsize=6.2, weight="bold", zorder=10)


DRAW = {"light": _sym_light, "fan": _sym_fan, "switchboard": _sym_switch,
        "socket": _sym_socket, "appliance": _sym_appliance}


def _title(fig, plan: FloorPlan, sheet: str, subtitle: str) -> None:
    fig.text(0.06, 0.965, "NAKSHA", fontsize=13, weight="bold", color=INK)
    fig.text(0.06, 0.941, plan.name, fontsize=8, color=ACCENT)
    fig.text(0.94, 0.965, sheet, fontsize=9, weight="bold", color=INK,
             ha="right")
    fig.text(0.94, 0.943, subtitle, fontsize=7, color=MUTED, ha="right")
    fig.add_artist(Line2D([0.06, 0.94], [0.928, 0.928], color="#d4d4d4",
                          lw=0.8, transform=fig.transFigure))


# ------------------------------------------------------------ sheet 1: plan
def sheet_layout(d: Design, path: str) -> str:
    fig, ax = plt.subplots(figsize=(11.0, 8.0))
    fig.subplots_adjust(left=0.05, right=0.78, top=0.90, bottom=0.05)
    _draw_shell(ax, d.plan)

    for p in d.points:
        DRAW.get(p.kind, _sym_appliance)(ax, p.xy)
    _sym_board(ax, d.board)

    for p in d.points:
        if p.kind == "appliance":
            ax.annotate(p.label, xy=p.xy, xytext=(p.xy[0], p.xy[1] - 0.34),
                        ha="center", fontsize=5.0, color=MUTED, zorder=9)

    counts: Dict[str, int] = {}
    for p in d.points:
        counts[p.kind] = counts.get(p.kind, 0) + 1
    md = maximum_demand(d)

    lines = ["LEGEND", ""]
    fig.text(0.80, 0.885, "LEGEND", fontsize=7.5, weight="bold", color=INK)
    y = 0.855
    for kind, label in (("light", "Lighting point"), ("fan", "Fan point"),
                        ("switchboard", "Switch plate"),
                        ("socket", "6 A socket"),
                        ("appliance", "Appliance point")):
        sub = fig.add_axes([0.802, y - 0.012, 0.022, 0.024])
        sub.set_xlim(-0.35, 0.35)
        sub.set_ylim(-0.35, 0.35)
        sub.axis("off")
        sub.set_aspect("equal")
        DRAW[kind](sub, (0, 0))
        fig.text(0.833, y, f"{label}  ({counts.get(kind, 0)})", fontsize=6.4,
                 color=INK, va="center")
        y -= 0.036
    sub = fig.add_axes([0.800, y - 0.014, 0.026, 0.026])
    sub.set_xlim(-0.45, 0.45)
    sub.set_ylim(-0.45, 0.45)
    sub.axis("off")
    sub.set_aspect("equal")
    _sym_board(sub, (0, 0))
    fig.text(0.833, y, "Distribution board", fontsize=6.4, color=INK,
             va="center")
    y -= 0.055

    fig.text(0.80, y, "SUMMARY", fontsize=7.5, weight="bold", color=INK)
    y -= 0.030
    rows = [
        ("Floor area", f"{d.plan.area:.1f} m\u00b2"),
        ("Device points", f"{len(d.points)}"),
        ("Final circuits", f"{len(d.circuits)}"),
        ("Connected load", f"{d.connected_load:.0f} W"),
        ("Maximum demand", f"{md['total']:.0f} W"),
        ("Sanctioned load", f"{d.reqs.sanctioned_load_w:.0f} W"),
        ("Conduit run", f"{d.total_route_length:.1f} m"),
    ]
    for k, v in rows:
        fig.text(0.80, y, k, fontsize=6.4, color=MUTED)
        fig.text(0.975, y, v, fontsize=6.4, color=INK, ha="right",
                 weight="bold")
        y -= 0.026

    _title(fig, d.plan, "SHEET 1", "Layout plan, device points")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


# --------------------------------------------------------- sheet 2: circuits
def sheet_circuits(d: Design, path: str) -> str:
    fig, ax = plt.subplots(figsize=(11.0, 8.0))
    fig.subplots_adjust(left=0.05, right=0.76, top=0.90, bottom=0.05)
    _draw_shell(ax, d.plan, label_rooms=True)

    for i, c in enumerate(d.circuits):
        colr = CYCLE[i % len(CYCLE)]
        for (u, v) in c.route_edges:
            ax.plot([u[0], v[0]], [u[1], v[1]], color=colr, lw=1.5,
                    alpha=0.75, zorder=5, solid_capstyle="round")
        for p in c.points:
            DRAW.get(p.kind, _sym_appliance)(ax, p.xy, colr)
    _sym_board(ax, d.board)

    fig.text(0.775, 0.885, "CIRCUIT SCHEDULE", fontsize=7.5, weight="bold",
             color=INK)
    hdr = ("Ckt", "Type", "Pts", "W", "MCB", "mm\u00b2", "m", "%V")
    xs = (0.775, 0.812, 0.858, 0.878, 0.912, 0.940, 0.962, 0.985)
    y = 0.858
    for x, h in zip(xs, hdr):
        fig.text(x, y, h, fontsize=5.8, color=MUTED, weight="bold",
                 ha="right" if h in ("Pts", "W", "MCB", "mm\u00b2", "m",
                                     "%V") else "left")
    y -= 0.020
    for i, c in enumerate(d.circuits):
        colr = CYCLE[i % len(CYCLE)]
        vals = (c.id, c.kind.capitalize(), str(len([p for p in c.points if p.is_load])),
                f"{c.connected_watts:.0f}", f"{c.mcb_amps:.0f}",
                f"{c.cable_mm2:g}", f"{c.route_length:.0f}",
                f"{c.vdrop_percent:.1f}")
        for j, (x, v) in enumerate(zip(xs, vals)):
            fig.text(x, y, v, fontsize=5.6,
                     color=colr if j == 0 else INK,
                     weight="bold" if j == 0 else "normal",
                     ha="right" if j >= 2 else "left")
        y -= 0.0185

    y -= 0.014
    fig.text(0.775, y, "TOTALS", fontsize=6.4, weight="bold", color=INK)
    y -= 0.020
    boq = bill_of_quantities(d)
    for k, v in (("Conduit", f"{boq['conduit_m']:.0f} m"),
                 ("Cable (3 core, 10% waste)",
                  ", ".join(f"{m:.0f} m of {s:g}"
                            for s, m in sorted(boq["wire_by_size"].items())))):
        fig.text(0.775, y, k, fontsize=5.8, color=MUTED)
        y -= 0.016
        fig.text(0.785, y, v, fontsize=5.8, color=INK, weight="bold")
        y -= 0.020

    _title(fig, d.plan, "SHEET 2", "Circuit grouping and conduit routing")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


# ------------------------------------------------------- sheet 3: schematic
def sheet_schematic(d: Design, path: str) -> str:
    fig = plt.figure(figsize=(11.0, 8.0))
    ax = fig.add_axes([0.06, 0.06, 0.56, 0.82])
    ax.axis("off")
    n = len(d.circuits)
    top = n * 0.9
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.6, top + 1.4)

    # incoming supply
    ax.plot([0.6, 0.6], [top + 1.0, top + 0.2], color=INK, lw=1.4)
    ax.text(0.6, top + 1.15, "SUPPLY  230 V, 1 ph, 50 Hz", fontsize=6.6,
            weight="bold", color=INK, ha="left")
    db_bottom = top - 0.45 - 0.55 - (n - 1) * 0.78 - 0.45
    ax.add_patch(mpatches.Rectangle((0.25, db_bottom), 1.45,
                                    (top + 0.2) - db_bottom, fc="none",
                                    ec=ACCENT, lw=1.2, ls="--"))
    ax.text(0.97, db_bottom - 0.30, "DISTRIBUTION BOARD", fontsize=6.6,
            weight="bold", color=ACCENT, ha="center")

    # main switch + RCCB
    ax.add_patch(mpatches.Rectangle((0.35, top - 0.15), 0.5, 0.32, fc="white",
                                    ec=INK, lw=0.9))
    ax.text(1.05, top + 0.02, "Main isolator + RCCB 30 mA", fontsize=6.2,
            color=INK, va="center")

    busbar_y = top - 0.45
    ax.plot([0.6, 9.4], [busbar_y, busbar_y], color=INK, lw=1.6)

    for i, c in enumerate(d.circuits):
        colr = CYCLE[i % len(CYCLE)]
        y = busbar_y - 0.55 - i * 0.78
        x = 1.4 + (i % 2) * 0.0
        ax.plot([x, x], [busbar_y, y + 0.16], color=INK, lw=0.8)
        # MCB symbol
        ax.add_patch(mpatches.Rectangle((x - 0.16, y - 0.02), 0.32, 0.22,
                                        fc="white", ec=INK, lw=0.9))
        ax.text(x, y + 0.09, f"{c.mcb_amps:.0f}", fontsize=5.2, ha="center",
                va="center", color=INK)
        ax.plot([x, x], [y - 0.02, y - 0.28], color=colr, lw=1.6)
        ax.plot([x, x + 0.55], [y - 0.28, y - 0.28], color=colr, lw=1.6)
        loads = ", ".join(sorted({p.label for p in c.points if p.is_load}))
        rooms = ", ".join(sorted({p.room for p in c.points}))
        ax.text(x + 0.68, y - 0.28,
                f"{c.id}   {c.cable_mm2:g} sq mm   "
                f"{c.connected_watts:.0f} W   {c.route_length:.0f} m   "
                f"{c.vdrop_percent:.1f}% drop",
                fontsize=5.8, va="center", color=INK, weight="bold")
        ax.text(x + 0.68, y - 0.52, f"{rooms}  |  {loads}"[:96],
                fontsize=5.0, va="center", color=MUTED)

    # right hand panel: BoQ and checks
    boq = bill_of_quantities(d)
    md = maximum_demand(d)
    issues = validate(d)

    fig.text(0.655, 0.885, "BILL OF QUANTITIES", fontsize=7.5, weight="bold",
             color=INK)
    y = 0.858
    fig.text(0.655, y, "Item", fontsize=5.8, color=MUTED, weight="bold")
    fig.text(0.878, y, "Qty", fontsize=5.8, color=MUTED, weight="bold",
             ha="right")
    fig.text(0.965, y, "Amount", fontsize=5.8, color=MUTED, weight="bold",
             ha="right")
    y -= 0.019
    for ln in boq["lines"]:
        fig.text(0.655, y, ln["item"][:30], fontsize=5.6, color=INK)
        fig.text(0.878, y, f"{ln['qty']:g} {ln['unit']}", fontsize=5.6,
                 color=INK, ha="right")
        fig.text(0.965, y, f"{ln['amount']:,.0f}", fontsize=5.6, color=INK,
                 ha="right")
        y -= 0.0175
    y -= 0.006
    fig.add_artist(Line2D([0.655, 0.965], [y + 0.008, y + 0.008],
                          color="#d4d4d4", lw=0.7,
                          transform=fig.transFigure))
    fig.text(0.655, y - 0.010, "Material total", fontsize=6.4, weight="bold",
             color=INK)
    fig.text(0.965, y - 0.010, f"Rs {boq['total']:,.0f}", fontsize=6.4,
             weight="bold", color=ACCENT, ha="right")
    y -= 0.048

    fig.text(0.655, y, "LOAD SUMMARY", fontsize=7.5, weight="bold", color=INK)
    y -= 0.024
    for k in sorted(k for k in md if k != "total"):
        fig.text(0.655, y, f"{k} (after diversity)", fontsize=5.8,
                 color=MUTED)
        fig.text(0.965, y, f"{md[k]:.0f} W", fontsize=5.8, color=INK,
                 ha="right")
        y -= 0.017
    fig.text(0.655, y, "Maximum demand", fontsize=6.2, weight="bold",
             color=INK)
    fig.text(0.965, y, f"{md['total']:.0f} W", fontsize=6.2, weight="bold",
             color=INK, ha="right")
    y -= 0.020
    fig.text(0.655, y, "Sanctioned load", fontsize=6.2, color=MUTED)
    fig.text(0.965, y, f"{d.reqs.sanctioned_load_w:.0f} W", fontsize=6.2,
             color=INK, ha="right")
    y -= 0.040

    fig.text(0.655, y, "DESIGN CHECKS", fontsize=7.5, weight="bold",
             color=INK)
    y -= 0.024
    if not issues:
        fig.text(0.655, y, "All checks passed.", fontsize=6.0, color=ACCENT)
    else:
        import textwrap
        for msg in issues[:6]:
            wrapped = textwrap.wrap(msg, width=58)
            for k, seg in enumerate(wrapped):
                fig.text(0.655 if k == 0 else 0.664, y,
                         ("\u2022 " + seg) if k == 0 else seg,
                         fontsize=5.4, color="#b8472a")
                y -= 0.014
            y -= 0.004

    _title(fig, d.plan, "SHEET 3",
           "Single line diagram, quantities and checks")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def all_sheets(d: Design, stem: str) -> List[str]:
    return [sheet_layout(d, f"{stem}-sheet1-layout.png"),
            sheet_circuits(d, f"{stem}-sheet2-circuits.png"),
            sheet_schematic(d, f"{stem}-sheet3-schematic.png")]
