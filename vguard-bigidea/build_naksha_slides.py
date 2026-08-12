#!/usr/bin/env python3
"""16:9 slide deck for the NAKSHA pitch video."""

from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdfcanvas

W, H = 960, 540
INK = colors.HexColor("#161616")
MUTED = colors.HexColor("#7A7A7A")
ACCENT = colors.HexColor("#1F6E5A")
FILL = colors.HexColor("#EEF1F0")
M = 62

c = pdfcanvas.Canvas("NAKSHA-Slides.pdf", pagesize=(W, H))
c.setTitle("NAKSHA - Pitch Slides")


def bg(n=None):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if n:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 11)
        c.drawRightString(W - M, 26, str(n))
        c.setStrokeColor(colors.HexColor("#E4E1DD"))
        c.setLineWidth(0.8)
        c.line(M, 44, W - M, 44)


def kicker(t, y=H - 78, colr=ACCENT):
    c.setFillColor(colr)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(M, y, t.upper())


def head(lines, y=H - 140, size=36, lead=44, colr=INK):
    c.setFillColor(colr)
    c.setFont("Helvetica-Bold", size)
    for i, ln in enumerate(lines):
        c.drawString(M, y - i * lead, ln)


def body(lines, y, size=17, lead=25, colr=MUTED, x=M, font="Helvetica"):
    c.setFillColor(colr)
    c.setFont(font, size)
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * lead, ln)


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


def tag(x, y, t, colr=MUTED, size=12, anchor="l", font="Helvetica"):
    c.setFillColor(colr)
    c.setFont(font, size)
    if anchor == "c":
        c.drawCentredString(x, y, t)
    elif anchor == "r":
        c.drawRightString(x, y, t)
    else:
        c.drawString(x, y, t)


# 1 -------------------------------------------------------------- title
bg()
c.setFillColor(ACCENT)
c.rect(0, 0, 10, H, stroke=0, fill=1)
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 66)
c.drawString(M, H - 210, "NAKSHA")
c.setFillColor(ACCENT)
c.setFont("Helvetica", 24)
c.drawString(M, H - 250, "V-Guard designs the wiring, then sells the wire")
c.setStrokeColor(colors.HexColor("#E4E1DD"))
c.line(M, H - 285, W - M, H - 285)
body(["Track 4  \u00b7  Reimagining V-Guard for an AI Powered Era",
      "V-Guard Big Idea Tech Design Contest 2026"], H - 315, 15, 24)
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 20)
c.drawString(M, 96, "Wire is the most commoditised thing V-Guard sells.")
c.showPage()

# 2 -------------------------------------------------------------- problem
bg(2)
kicker("the problem")
head(["Indian homes are wired", "from memory."])
body(["No drawing. Improvised conduit routes. No record left behind."],
     H - 232, 18, 26, INK)
box(M, 150, 300, 96, "42%", "of building fires in India", fill=ACCENT,
    stroke=ACCENT, size=52)
tag(M + 330, 214, "attributed to electrical short circuits", INK, 18,
    font="Helvetica-Bold")
body(["And \u201cshort circuit\u201d hides the real causes, ageing",
      "wiring, overloaded circuits, substandard material,",
      "quietly accumulating behind the plaster."], 188, 15, 22, MUTED,
     M + 330)
c.showPage()

# 3 -------------------------------------------------------------- standards
bg(3)
kicker("the frustrating part")
head(["The rules already exist."])
y = 300
for code, desc in [("WIRING CODE", "national code of practice for wiring installation"),
                   ("EARTHING CODE", "national code of practice for earthing"),
                   ("REGULATION", "work must be done by a licensed contractor")]:
    box(M, y, 168, 34, code, fill=FILL, size=13)
    tag(M + 184, y + 11, desc, MUTED, 14)
    y -= 50
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 21)
c.drawString(M, 122, "The gap isn't the code.")
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 21)
c.drawString(M, 92, "Nothing turns it into a drawing anyone will use.")
c.showPage()

# 4 -------------------------------------------------------------- pipeline
bg(4)
kicker("what naksha does")
head(["One upload. Three outputs."], H - 132, 32, 40)
box(M, 236, 150, 66, "ARCHITECT'S PLAN", "PDF or DWG", fill=FILL, size=13)
arrow(M + 158, 269, M + 190)
box(M + 198, 226, 180, 86, "NAKSHA ENGINE", "national wiring codes", fill=ACCENT,
    stroke=ACCENT, size=16)
tag(M + 288, 210, "circuits \u00b7 DB siting \u00b7 routing", MUTED, 12,
    anchor="c")
outs = [("WIRE SCHEDULE", "exact metres, by size", 322, "a purchase order"),
        ("SITE MARKING", "phone AR or assisted", 252, "built correctly"),
        ("AS-BUILT RECORD", "permanent digital map", 182, "lifetime lock-in")]
bx = M + 424
for label, sub, y, note in outs:
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    c.line(M + 386, 269, M + 406, 269)
    c.line(M + 406, 269, M + 406, y + 22)
    c.line(M + 406, y + 22, bx, y + 22)
    c.restoreState()
    box(bx, y, 190, 44, label, sub, fill=None, stroke=ACCENT, size=12,
        tc=INK)
    tag(bx + 200, y + 18, "\u2192 " + note, ACCENT, 12,
        font="Helvetica-Bold")
tag(M, 120, "The first output is a purchase order.", INK, 19,
    font="Helvetica-Bold")
tag(M, 94, "The third one never leaves the house.", INK, 19,
    font="Helvetica-Bold")
c.showPage()

# 5 -------------------------------------------------------------- channel
bg(5)
kicker("the insight that convinced us")
head(["The channel is already built."], H - 130, 32, 40)
half = (W - 2 * M - 30) / 2
tag(M, 316, "WHAT EVERY COMPETITOR SHIPS", MUTED, 12,
    font="Helvetica-Bold")
box(M, 232, half, 72, "LOYALTY POINTS", "scan QR \u00b7 earn \u00b7 redeem",
    fill=FILL, size=17)
body(["RR Connect  \u00b7  Finolex Samruddhi",
      "Polycab Experts  \u00b7  Havells",
      "",
      "Polycab reaches ~2.5 lakh electricians."], 210, 14, 21, MUTED)
x2 = M + half + 30
tag(x2, 316, "WHAT NAKSHA SHIPS", ACCENT, 12, font="Helvetica-Bold")
box(x2, 232, half, 72, "A TOOL THAT DOES THE WORK",
    "designs the job \u00b7 sizes the wire", fill=ACCENT, stroke=ACCENT,
    size=15)
body(["Same channel. Same phones.", "Something actually useful in it."], 210,
     14, 21, INK, x2, "Helvetica-Bold")
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 21)
c.drawString(M, 108, "Nobody has put a tool in that channel")
c.drawString(M, 80, "that does any actual work.")
c.showPage()

# 6 -------------------------------------------------------------- wants
bg(6)
kicker("the user we design for")
head(["An electrician", "doesn't want points."], H - 150, 44, 54)
y = 250
for t in ["the load calculation done",
          "the wire sizes decided",
          "the material list totalled",
          "a defensible answer when the owner asks why it costs that much"]:
    c.setFillColor(ACCENT)
    c.circle(M + 6, y + 5, 4.5, stroke=0, fill=1)
    tag(M + 24, y, t, INK, 19)
    y -= 40
c.showPage()

# 7 -------------------------------------------------------------- prior art
bg(7)
kicker("honest about prior art")
head(["None of it is built for India."], H - 130, 32, 40)
rows = [("drawer.ai", "PDF drawings in \u2192 wire lengths + routing out"),
        ("ISARC 2026", "automated outlet-to-circuit assignment in BIM"),
        ("Dusty Robotics", "layouts printed on 300M+ sq ft of slab")]
y = 306
for name, what in rows:
    box(M, y, 150, 34, name, fill=FILL, size=14)
    tag(M + 166, y + 11, what, MUTED, 14)
    y -= 48
body(["All of it serves Western commercial contractors bidding large projects."],
     150, 17, 24, INK)
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 18)
c.drawString(M, 112, "None encodes Indian standards.")
c.drawString(M, 86, "None is distributed by the company that sells the wire.")
c.showPage()

# 8 -------------------------------------------------------------- business
bg(8)
kicker("why it is a better business")
head(["Every design is", "a purchase order."], H - 140, 38, 46)
body(["The output is a wire schedule in metres, by size.",
      "Specifying the material beats advertising to whoever walks into a shop."],
     280, 17, 26, INK)
box(M, 176, W - 2 * M, 72, "THE ASIAN PAINTS MOVE",
    "escape commodity competition by selling the service, not the tin",
    fill=ACCENT, stroke=ACCENT, size=19)
body(["Wiring is decided during construction, before the owner has a "
      "brand opinion.",
      "Nobody re-shops it. You cannot rewire a finished house."], 148, 17, 25,
     INK)
c.showPage()

# 9 -------------------------------------------------------------- scale
bg(9)
kicker("on scale")
head(["We don't propose a", "national service business."], H - 132, 32, 40)
body(["The design engine scales at software cost. Only the marking needs "
      "people, so we separate them."], H - 218, 16, 24, MUTED)
rows = [("TIER 1  \u00b7  APP", "Free, all-India",
         "phone AR marking \u00b7 zero hardware \u00b7 infinitely scalable",
         FILL, INK),
        ("TIER 2  \u00b7  ASSISTED", "Metro cities",
         "trained V-Guard marking partner \u00b7 paid service", FILL, INK),
        ("TIER 3  \u00b7  FLAGSHIP", "Showcase only",
         "robotic or laser layout, built for marketing, not margin",
         ACCENT, colors.white)]
y = 216
for name, scope, note, fill, tc in rows:
    box(M, y, 210, 44, name, fill=fill,
        stroke=INK if fill is FILL else ACCENT, size=13, tc=tc)
    tag(M + 228, y + 26, scope, INK, 15, font="Helvetica-Bold")
    tag(M + 228, y + 9, note, MUTED, 13)
    y -= 60
tag(M, 66, "Tier 1 carries the strategy. Tier 3 exists to be photographed.",
    INK, 16, font="Helvetica-Bold")
c.showPage()

# 10 ------------------------------------------------------------- risk
bg(10)
kicker("what we would test first")
head(["The risk isn't the technology.", "It's adoption."], H - 132, 32, 40)
body(["Experienced electricians may read this as a challenge to their "
      "judgment."], 300, 18, 26, MUTED)
box(M, 190, W - 2 * M, 86, "IT MUST SAVE HIM TIME ON DAY ONE",
    "load calculation and estimating, visibly faster, or it gets ignored",
    fill=ACCENT, stroke=ACCENT, size=20)
body(["Also honest: Indian residential plans are often scanned, hand-marked or "
      "dimensionally unreliable,",
      "so the first release assumes human confirmation of every inferred room."],
     150, 14, 21, MUTED)
c.showPage()

c.save()
print("NAKSHA slides written.")
