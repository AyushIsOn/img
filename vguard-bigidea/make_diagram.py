"""Draws the NAKSHA flow diagram.

    python3 make_diagram.py

The point the diagram has to make is the boundary: the language model handles the
conversation and nothing else, and every decision that could hurt somebody
happens in the rule engine. That is why the two are drawn in separate bands
rather than as one pipeline.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

AMBER = "#E8891C"
GOLD = "#F4B942"
INK = "#1A1A1A"
GREY = "#6E6E73"
LIGHT = "#F2F2F4"
RULE = "#2E6F5E"

fig, ax = plt.subplots(figsize=(10.6, 6.1))
ax.set_xlim(0, 106)
ax.set_ylim(0, 61)
ax.axis("off")


def band(x, y, w, h, label, colour):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=colour, alpha=0.10,
                           edgecolor=colour, linewidth=1.1, zorder=0))
    ax.text(x + 1.6, y + h - 3.0, label, fontsize=8.4, color=colour,
            weight="bold", family="serif", zorder=1)


def box(x, y, w, h, title, sub=None, edge=INK, fill="white", tw=9.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.35,rounding_size=1.2",
                                facecolor=fill, edgecolor=edge,
                                linewidth=1.25, zorder=3))
    cy = y + h / 2 + (1.7 if sub else 0)
    ax.text(x + w / 2, cy, title, ha="center", va="center", fontsize=tw,
            color=INK, weight="bold", family="serif", zorder=4)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 2.6, sub, ha="center", va="center",
                fontsize=7.3, color=GREY, family="serif", zorder=4)


def arrow(x1, y1, x2, y2, colour=INK, style="-|>", lw=1.3, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle=style, mutation_scale=11,
                                 linewidth=lw, color=colour, zorder=2,
                                 connectionstyle=f"arc3,rad={rad}"))


# ----------------------------------------------------------- band 1, input
band(1, 44, 104, 16, "1.  WHAT THE OWNER PROVIDES", AMBER)

box(4, 48, 22, 9, "Conversation", "about 8 questions, LLM", edge=AMBER,
    fill="#FDF6EC")
box(32, 48, 22, 9, "LiDAR scan", "each room, no typing", edge=AMBER,
    fill="#FDF6EC")
box(60, 48, 20, 9, "Household profile", "load, rooms, appliances",
    edge=GREY, fill=LIGHT)
box(84, 48, 18, 9, "Room geometry", "outline, doors, windows",
    edge=GREY, fill=LIGHT)

arrow(26, 52.5, 60, 52.5, AMBER)
arrow(54, 52.5, 84, 52.5, AMBER, rad=-0.18)

# ------------------------------------------------------ band 2, rule engine
band(1, 20, 104, 21, "2.  RULE ENGINE   every decision traceable, no model here",
     RULE)

steps = [
    (4,  "Placement", "lumen method,\nsocket rules"),
    (24, "Circuits", "lighting, power,\ndedicated"),
    (44, "Board siting", "minimise\ntotal cable"),
    (64, "Routing", "rectilinear\nSteiner tree"),
    (84, "Sizing", "breaker first,\nthen cable"),
]
for x, title, sub in steps:
    ax.add_patch(FancyBboxPatch((x, 24.5), 18, 11,
                                boxstyle="round,pad=0.35,rounding_size=1.2",
                                facecolor="#EEF5F2", edgecolor=RULE,
                                linewidth=1.25, zorder=3))
    ax.text(x + 9, 32.0, title, ha="center", va="center", fontsize=8.8,
            color=INK, weight="bold", family="serif", zorder=4)
    ax.text(x + 9, 28.2, sub, ha="center", va="center", fontsize=6.9,
            color=GREY, family="serif", linespacing=1.35, zorder=4)
for x in (22, 42, 62, 82):
    arrow(x, 30, x + 2, 30, RULE)

# the model is kept out of this band, said explicitly
arrow(15, 48, 15, 35.5, AMBER, style="-|>", lw=1.3)
ax.text(16.4, 41.5, "profile only", fontsize=6.9, color=AMBER,
        family="serif", style="italic")
arrow(93, 48, 93, 35.5, AMBER)
ax.text(94.4, 41.5, "geometry", fontsize=6.9, color=AMBER,
        family="serif", style="italic")

# checks feed back
ax.text(53, 21.8, "checks: voltage drop, maximum demand against sanctioned "
                  "load, breaker above cable ampacity refused",
        ha="center", fontsize=7.0, color=RULE, family="serif",
        style="italic")

# ---------------------------------------------------------- band 3, outputs
band(1, 2, 104, 15, "3.  WHAT COMES OUT", GOLD)

box(4, 5.5, 22, 8.5, "Drawing", "plan the trades build from",
    edge=GOLD, fill="#FEF9EE")
box(30, 5.5, 22, 8.5, "Circuit schedule", "breaker, cable, load, drop",
    edge=GOLD, fill="#FEF9EE")
box(56, 5.5, 20, 8.5, "Bill of quantities", "metres and units, priced",
    edge=GOLD, fill="#FEF9EE")
box(80, 5.5, 22, 8.5, "AR overlay", "full size, on the wall",
    edge=GOLD, fill="#FEF9EE")

arrow(53, 24.5, 53, 14.0, RULE)

# ---------------------------------------------------------------- outcomes
ax.annotate("", xy=(103.4, 9.7), xytext=(102, 9.7),
            arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2))
ax.text(53, 0.4, "confirmed on site, point by point, and kept as the "
                 "as-built record  \u2192  a V-Guard material order",
        ha="center", fontsize=7.6, color=INK, family="serif", weight="bold")

fig.savefig("exhibits/flow-diagram.png", dpi=260, bbox_inches="tight",
            facecolor="white")
print("written: exhibits/flow-diagram.png")
