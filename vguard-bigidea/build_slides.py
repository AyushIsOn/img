#!/usr/bin/env python3
"""16:9 slide deck for the INVIDIA CORE pitch video."""

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import Paragraph, Frame

W, H = 960, 540                      # 16:9
INK = colors.HexColor("#161616")
MUTED = colors.HexColor("#7A7A7A")
ACCENT = colors.HexColor("#B8472A")
FILL = colors.HexColor("#F1EFEC")
BG = colors.white
M = 62

c = pdfcanvas.Canvas("INVIDIA-CORE-Slides.pdf", pagesize=(W, H))
c.setTitle("INVIDIA CORE - Pitch Slides")


# --------------------------------------------------------------- helpers
def bg(n=None):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if n:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 11)
        c.drawRightString(W - M, 26, str(n))
        c.setStrokeColor(colors.HexColor("#E4E1DD"))
        c.setLineWidth(0.8)
        c.line(M, 44, W - M, 44)


def kicker(txt, y=H - 78, colr=ACCENT):
    c.setFillColor(colr)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(M, y, txt.upper())


def head(lines, y=H - 140, size=38, lead=45, colr=INK):
    c.setFillColor(colr)
    c.setFont("Helvetica-Bold", size)
    for i, ln in enumerate(lines):
        c.drawString(M, y - i * lead, ln)
    return y - len(lines) * lead


def body(lines, y, size=17, lead=25, colr=MUTED, x=M):
    c.setFillColor(colr)
    c.setFont("Helvetica", size)
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * lead, ln)
    return y - len(lines) * lead


def box(x, y, w, h, label, sub=None, fill=FILL, stroke=INK, size=14,
        dash=None, tc=None):
    c.saveState()
    c.setStrokeColor(stroke)
    c.setLineWidth(1.6)
    if dash:
        c.setDash(dash, 3)
    if fill is not None:
        c.setFillColor(fill)
        c.roundRect(x, y, w, h, 5, stroke=1, fill=1)
    else:
        c.roundRect(x, y, w, h, 5, stroke=1, fill=0)
    c.setDash()
    c.setFillColor(tc or (colors.white if fill == ACCENT else INK))
    c.setFont("Helvetica-Bold", size)
    if sub:
        c.drawCentredString(x + w / 2, y + h / 2 + 4, label)
        c.setFont("Helvetica", size - 3)
        c.setFillColor(tc or (colors.white if fill == ACCENT else MUTED))
        c.drawCentredString(x + w / 2, y + h / 2 - 14, sub)
    else:
        c.drawCentredString(x + w / 2, y + h / 2 - size / 2 + 2, label)
    c.restoreState()


def arrow(x1, y, x2, colr=INK, lw=1.6):
    c.saveState()
    c.setStrokeColor(colr)
    c.setFillColor(colr)
    c.setLineWidth(lw)
    c.line(x1, y, x2 - 6, y)
    p = c.beginPath()
    p.moveTo(x2, y)
    p.lineTo(x2 - 8, y + 4.5)
    p.lineTo(x2 - 8, y - 4.5)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def tag(x, y, txt, colr=MUTED, size=12, anchor="l", font="Helvetica"):
    c.setFillColor(colr)
    c.setFont(font, size)
    if anchor == "c":
        c.drawCentredString(x, y, txt)
    elif anchor == "r":
        c.drawRightString(x, y, txt)
    else:
        c.drawString(x, y, txt)


# --------------------------------------------------------------- 1 title
bg()
c.setFillColor(ACCENT)
c.rect(0, 0, 10, H, stroke=0, fill=1)
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 62)
c.drawString(M, H - 210, "INVIDIA CORE")
c.setFillColor(ACCENT)
c.setFont("Helvetica", 24)
c.drawString(M, H - 250, "Power protection that disappears into the wall")
c.setStrokeColor(colors.HexColor("#E4E1DD"))
c.setLineWidth(1)
c.line(M, H - 285, W - M, H - 285)
body(["Track 1  \u00b7  Reimagining the Stabilizer for the Next Decade",
      "V-Guard Big Idea Tech Design Contest 2026"], H - 315, 15, 24)
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 19)
c.drawString(M, 96, "Every Indian home with a stabilizer has two boxes")
c.drawString(M, 70, "doing one job, in the same place.")
c.showPage()

# --------------------------------------------------------------- 2 two boxes
bg(2)
kicker("today")
head(["Two boxes. One job.", "Same wall."], H - 132, 34, 42)
by, bh = 190, 92
box(M, by, 230, bh, "DISTRIBUTION BOARD", "MCB  /  RCCB  /  screen")
arrow(M + 240, by + bh / 2, M + 288)
box(M + 298, by, 200, bh, "STABILIZER", "the correction")
tag(M, by - 34, "It shows you the voltage is bad. It cannot fix it.", INK, 15,
    font="Helvetica-Bold")
tag(M, by - 60, "V-Guard already manufactures both halves \u2014 Invidia+ "
                "and VMT 500/1000 Plus.", MUTED, 14)
c.showPage()

# --------------------------------------------------------------- 3 proposal
bg(3)
kicker("the proposal")
head(["Put the fixing", "inside the board."], H - 140, 44, 52)
box(M, 150, W - 2 * M, 104, "MCB   +   RCCB   +   SPD   +   VOLTAGE CORRECTION",
    "one enclosure  \u00b7  one DIN rail", fill=ACCENT, stroke=ACCENT, size=21)
tag(M, 118, "Power protection stops being an appliance you buy, and becomes "
            "infrastructure the building already has.", MUTED, 14)
c.showPage()

# --------------------------------------------------------------- 4 why not
bg(4)
kicker("why nobody has done it")
head(["A whole-house transformer", "will not fit in a sealed box."], H - 132,
     32, 40)
box(M, 208, 300, 96, "8,000 W", "of iron and copper", fill=FILL, size=34)
tag(M + 330, 272, "Several kilograms. Runs hot.", INK, 17,
    font="Helvetica-Bold")
tag(M + 330, 246, "Put that beside your MCBs and they overheat", MUTED, 15)
tag(M + 330, 224, "and start tripping for no reason.", MUTED, 15)
tag(M, 150, "So the idea only works if the correction gets much smaller.",
    INK, 19, font="Helvetica-Bold")
tag(M, 122, "There are two ways. They stack.", ACCENT, 17,
    font="Helvetica-Bold")
c.showPage()

# --------------------------------------------------------------- 5 shrink 1
bg(5)
kicker("shrink one")
head(["Fix circuits, not homes."], H - 132, 36, 44)
rows = [("Air conditioner", True, "compressor"),
        ("Refrigerator", True, "compressor"),
        ("Lights & fans", False, "LED + BLDC \u2014 runs at 100\u2013280 V"),
        ("Sockets", False, "wide-range power supplies")]
y = 300
for name, need, note in rows:
    colr = ACCENT if need else MUTED
    box(M, y, 26, 26, "\u2713" if need else "\u2013",
        fill=ACCENT if need else None, stroke=colr, size=15,
        tc=colors.white if need else MUTED)
    tag(M + 40, y + 8, name, INK if need else MUTED, 17,
        font="Helvetica-Bold" if need else "Helvetica")
    tag(M + 230, y + 8, note, MUTED, 14)
    y -= 44
tag(M, 108, "One AC circuit is 3,000 W \u2014 not 8,000 W.", INK, 21,
    font="Helvetica-Bold")
tag(M, 78, "Only the distribution board can pick and choose. A plug-in unit "
           "does one appliance; a mainline unit must do everything.", MUTED, 14)
c.showPage()

# --------------------------------------------------------------- 6 shrink 2
bg(6)
kicker("shrink two")
head(["Don't rebuild the voltage.", "Top it up."], H - 128, 34, 42)
# old way
tag(M, 300, "OLD WAY", MUTED, 12, font="Helvetica-Bold")
box(M, 246, 96, 44, "180 V", fill=FILL, size=17)
arrow(M + 104, 268, M + 128)
box(M + 136, 246, 150, 44, "TRANSFORMER", "all the power", fill=FILL, size=13)
arrow(M + 294, 268, M + 318)
box(M + 326, 246, 96, 44, "230 V", fill=FILL, size=17)
# new way
tag(M, 196, "SERIES INJECTION", ACCENT, 12, font="Helvetica-Bold")
box(M, 142, 96, 44, "180 V", fill=FILL, size=17)
tag(M + 112, 158, "+", INK, 26, font="Helvetica-Bold")
box(M + 136, 142, 150, 44, "+ 50 V", "only the shortfall", fill=ACCENT,
    stroke=ACCENT, size=17)
arrow(M + 294, 164, M + 318, ACCENT)
box(M + 326, 142, 96, 44, "230 V", fill=FILL, size=17)
# analogy
c.setStrokeColor(colors.HexColor("#E4E1DD"))
c.setLineWidth(1)
c.line(M + 470, 120, M + 470, 320)
tag(M + 500, 292, "Like water pressure.", INK, 18, font="Helvetica-Bold")
body(["A full pumping station takes all",
      "the water and re-pressurises it.",
      "",
      "A booster pump in the pipe just",
      "adds the missing pressure.",
      "",
      "Same result at the tap.",
      "Far smaller machine."], 264, 15, 22, MUTED, M + 500)
tag(M, 92, "Fifty volts instead of two-thirty \u2014 so about a fifth of the "
           "power.", INK, 19, font="Helvetica-Bold")
c.showPage()

# --------------------------------------------------------------- 7 cascade
bg(7)
kicker("put them together")
head(["Ten times smaller."], H - 130, 38, 46)
rows = [("Whole house, old method", "8,000 W", 8.0, FILL, INK,
         "kilograms of hot iron"),
        ("Only the circuits that need it", "3,000 W", 3.0, FILL, INK,
         "less than half"),
        ("Only the shortfall", "~700 W", 0.75, ACCENT, colors.white,
         "fits on a DIN rail")]
maxw = 470
y = 292
for label, val, mag, fill, tc, note in rows:
    tag(M, y + 40, label, INK, 16, font="Helvetica-Bold")
    bw = max(maxw * (mag / 8.0), 120)
    c.saveState()
    c.setStrokeColor(INK if fill is FILL else ACCENT)
    c.setLineWidth(1.4)
    c.setFillColor(fill)
    c.roundRect(M, y, bw, 32, 4, stroke=1, fill=1)
    c.setFillColor(tc)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(M + 12, y + 9, val)
    c.restoreState()
    tag(M + bw + 16, y + 10, note, MUTED, 14)
    y -= 92
tag(M, 80, "700 W with a small heatsink fits next to the MCBs. "
           "8,000 W of iron never could.", INK, 17, font="Helvetica-Bold")
c.showPage()

# --------------------------------------------------------------- 8 the board
bg(8)
kicker("inside the enclosure")
head(["Only the ways that need it."], H - 122, 30, 38)
ex, ey, ew, eh = 236, 150, 660, 262
c.saveState()
c.setStrokeColor(MUTED)
c.setLineWidth(1.1)
c.setDash([4, 4], 0)
c.roundRect(ex, ey, ew, eh, 7, stroke=1, fill=0)
c.setDash()
c.restoreState()
tag(ex + ew, ey + eh + 10, "SINGLE ENCLOSURE", MUTED, 11, anchor="r",
    font="Helvetica-Bold")
tag(M, ey + eh / 2 + 4, "MAINS", INK, 15, font="Helvetica-Bold")
tag(M, ey + eh / 2 - 14, "+ solar", MUTED, 12)
arrow(M + 62, ey + eh / 2 + 8, ex + 6)
box(ex + 14, ey + eh / 2 - 15, 74, 46, "RCCB", "+ SPD", fill=FILL, size=13)
bus = ex + 112
c.saveState()
c.setStrokeColor(MUTED)
c.setLineWidth(1.1)
c.line(ex + 88, ey + eh / 2 + 8, bus, ey + eh / 2 + 8)
c.line(bus, ey + 20, bus, ey + eh - 24)
c.restoreState()
ways = [("Air conditioner 1", 1), ("Air conditioner 2", 1),
        ("Refrigerator", 1), ("Lights & fans", 0), ("Sockets", 0),
        ("Spare way", 2)]
top, step = ey + eh - 50, 41
for i, (name, kind) in enumerate(ways):
    y = top - i * step
    c.saveState()
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.9)
    c.line(bus, y + 13, bus + 14, y + 13)
    c.restoreState()
    box(bus + 14, y, 46, 26, "MCB", fill=FILL, size=11)
    if kind == 1:
        arrow(bus + 62, y + 13, bus + 78, ACCENT)
        box(bus + 86, y, 118, 26, "REGULATOR", fill=ACCENT, stroke=ACCENT,
            size=11)
        arrow(bus + 206, y + 13, bus + 222, ACCENT)
        tag(bus + 230, y + 8, name, INK, 14, font="Helvetica-Bold")
    elif kind == 2:
        box(bus + 86, y, 118, 26, "add later", fill=None, stroke=MUTED,
            size=11, dash=[3, 3], tc=MUTED)
        tag(bus + 230, y + 8, name + "  \u2192 clip on a module", MUTED, 13)
    else:
        arrow(bus + 62, y + 13, bus + 222, MUTED, 0.9)
        tag(bus + 230, y + 8, name, MUTED, 13)
        tag(bus + 356, y + 8, "no need", MUTED, 12)
tag(M, 108, "Each module is sized to its own MCB \u2014 a 16 A MCB is a 16 A "
            "ceiling, so nothing you plug in can overload it.", INK, 15,
    font="Helvetica-Bold")
tag(M, 80, "If a module fails or overheats, a relay bypasses it: you lose the "
           "correction, never the power.", ACCENT, 15, font="Helvetica-Bold")
c.showPage()

# --------------------------------------------------------------- 9 business
bg(9)
kicker("why it is a better business")
head(["It stops being a purchase.", "It becomes a specification."], H - 132,
     31, 39)
box(M, 190, 360, 118, "", fill=FILL, stroke=FILL)
tag(M + 22, 282, "TODAY", MUTED, 12, font="Helvetica-Bold")
body(["Buy an AC \u2192 remember the stabilizer",
      "\u2192 compare five brands in a shop.",
      "Low margin. You might buy a rival's."], 258, 14.5, 22, INK, M + 22)
arrow(M + 380, 249, M + 424, ACCENT, 2.2)
box(M + 440, 190, 360, 118, "", fill=ACCENT, stroke=ACCENT)
tag(M + 462, 282, "WITH INVIDIA CORE", colors.white, 12,
    font="Helvetica-Bold")
c.setFillColor(colors.white)
c.setFont("Helvetica", 14.5)
for i, ln in enumerate(["The electrician fits it while the house",
                        "is being wired. You were never in that",
                        "decision \u2014 and never compared price."]):
    c.drawString(M + 462, 258 - i * 22, ln)
tag(M, 138, "Nobody removes a distribution board to save Rs 1,500.", INK, 20,
    font="Helvetica-Bold")
tag(M, 110, "A channel V-Guard already owns through switchgear and wire. "
            "Revenue grew 7.0%; profit fell 1.7% \u2014 the problem is "
            "margin, not volume.", MUTED, 14)
c.showPage()

# --------------------------------------------------------------- 10 risk
bg(10)
kicker("what we will not overclaim")
head(["The heat must be proven,", "not asserted."], H - 132, 34, 42)
body(["The arithmetic says 700 W is manageable where 8,000 W was not.",
      "But \u201cshould be\u201d is not \u201cis.\u201d"], 300, 18, 28, INK)
box(M, 168, W - 2 * M, 92, "TEST ONE",
    "thermocouples inside a real enclosure, fully loaded, confirming the "
    "MCBs stay within rated temperature", fill=ACCENT, stroke=ACCENT, size=20)
tag(M, 136, "If that test fails, the idea fails. That is why it is first.",
    INK, 18, font="Helvetica-Bold")
tag(M, 96, "Also honest: a board cannot see inside a circuit. If an AC shares "
           "a way with lights, it needs its own way \u2014", MUTED, 13)
tag(M, 78, "standard practice for heavy loads anyway. New construction and "
           "rewiring first; retrofit second.", MUTED, 13)
c.showPage()

c.save()
print("Slides written.")
