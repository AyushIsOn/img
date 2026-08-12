#!/usr/bin/env python3
"""Builds the INVIDIA CORE executive summary PDF with native vector diagrams."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                               PageTemplate, Paragraph, Spacer)

# ---------------------------------------------------------------- palette
INK = colors.HexColor("#1B1B1B")
MUTED = colors.HexColor("#6E6E6E")
ACCENT = colors.HexColor("#B8472A")
RULE = colors.HexColor("#D4D4D4")
FILL = colors.HexColor("#F2F0ED")

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

# ---------------------------------------------------------------- styles
def style(name, **kw):
    base = dict(name=name, fontName="Helvetica", fontSize=9.2, leading=12.9,
                textColor=INK, spaceAfter=0)
    base.update(kw)
    return ParagraphStyle(**base)

S = {
    "title": style("title", fontName="Helvetica-Bold", fontSize=20, leading=23,
                   spaceAfter=3),
    "sub": style("sub", fontSize=9.6, leading=13, textColor=ACCENT,
                 spaceAfter=2),
    "meta": style("meta", fontSize=8.2, leading=11, textColor=MUTED,
                  spaceAfter=14),
    "h2": style("h2", fontName="Helvetica-Bold", fontSize=11.4, leading=14,
                spaceBefore=8.5, spaceAfter=3.5, keepWithNext=1),
    "h3": style("h3", fontName="Helvetica-BoldOblique", fontSize=9.5,
                leading=12.4, spaceBefore=7, spaceAfter=2.5, keepWithNext=1),
    "body": style("body", alignment=TA_JUSTIFY, spaceAfter=4),
    "lead": style("lead", fontSize=10.2, leading=14.0, spaceAfter=5),
    "bullet": style("bullet", alignment=TA_JUSTIFY, leftIndent=11,
                    bulletIndent=1, spaceAfter=2.9),
    "pull": style("pull", fontName="Helvetica-Bold", fontSize=10.2,
                  leading=14.6, textColor=ACCENT, leftIndent=10,
                  spaceBefore=6, spaceAfter=8),
    "cap": style("cap", fontSize=7.8, leading=10.4, textColor=MUTED,
                 spaceBefore=3, spaceAfter=9),
}


def P(txt, s="body"):
    return Paragraph(txt, S[s])


def B(txt):
    return Paragraph(txt, S["bullet"], bulletText="\u2013")


# ---------------------------------------------------------------- diagrams
class Diagram(Flowable):
    """Base: fixed-height canvas flowable."""

    def __init__(self, height):
        Flowable.__init__(self)
        self.width = CONTENT_W
        self.height = height

    def wrap(self, *_):
        return self.width, self.height

    # helpers -----------------------------------------------------------
    def box(self, x, y, w, h, label, sub=None, fill=None, stroke=INK,
            bold=True, size=7.6, dash=None, tc=None):
        c = self.canv
        c.saveState()
        c.setStrokeColor(stroke)
        c.setLineWidth(0.9)
        if dash:
            c.setDash(dash, 2)
        if fill is not None:
            c.setFillColor(fill)
            c.roundRect(x, y, w, h, 2.5, stroke=1, fill=1)
        else:
            c.roundRect(x, y, w, h, 2.5, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(tc or (colors.white if fill == ACCENT else INK))
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        if sub:
            c.drawCentredString(x + w / 2, y + h / 2 + 1.4, label)
            c.setFont("Helvetica", size - 1.1)
            c.drawCentredString(x + w / 2, y + h / 2 - 6.4, sub)
        else:
            c.drawCentredString(x + w / 2, y + h / 2 - size / 2 + 1.2, label)
        c.restoreState()

    def arrow(self, x1, y, x2, colr=INK, w=0.9):
        c = self.canv
        c.saveState()
        c.setStrokeColor(colr)
        c.setFillColor(colr)
        c.setLineWidth(w)
        c.line(x1, y, x2 - 3, y)
        c.setLineWidth(0)
        p = c.beginPath()
        p.moveTo(x2, y)
        p.lineTo(x2 - 4.2, y + 2.3)
        p.lineTo(x2 - 4.2, y - 2.3)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()

    def tag(self, x, y, txt, colr=MUTED, size=7.2, anchor="l",
            font="Helvetica"):
        c = self.canv
        c.saveState()
        c.setFillColor(colr)
        c.setFont(font, size)
        if anchor == "c":
            c.drawCentredString(x, y, txt)
        elif anchor == "r":
            c.drawRightString(x, y, txt)
        else:
            c.drawString(x, y, txt)
        c.restoreState()


class DiagBeforeAfter(Diagram):
    """Two boxes on the wall today -> one board."""

    def __init__(self):
        Diagram.__init__(self, 96)

    def draw(self):
        w = self.width
        mid = w * 0.52
        bh, by = 42, 26

        # --- today
        self.tag(0, 82, "TODAY  \u2014  TWO BOXES, ONE JOB", INK, 7.6,
                 font="Helvetica-Bold")
        b1w = 92
        self.box(0, by, b1w, bh, "Distribution Board", "MCB / RCCB", fill=FILL)
        self.arrow(b1w + 4, by + bh / 2, b1w + 22)
        self.box(b1w + 26, by, 74, bh, "Stabilizer", "correction", fill=FILL)
        self.tag(b1w + 63, 14, "two enclosures \u00b7 two installs", MUTED, 7)

        # --- arrow between
        cx = mid + 14
        self.arrow(cx - 16, by + bh / 2, cx + 12, ACCENT, 1.4)

        # --- after
        self.tag(cx + 26, 82, "INVIDIA CORE  \u2014  ONE BOARD", ACCENT, 7.6,
                 font="Helvetica-Bold")
        self.box(cx + 26, by, w - (cx + 26), bh,
                 "MCB  +  RCCB  +  SPD  +  REGULATION", "single DIN rail",
                 fill=ACCENT)
        self.tag(cx + 26, 14, "one enclosure \u00b7 specified at wiring stage",
                 MUTED, 7)


class DiagCascade(Diagram):
    """8 kVA -> 3 kVA -> 0.75 kVA."""

    def __init__(self):
        Diagram.__init__(self, 108)

    def draw(self):
        rows = [
            ("Whole-home stabilizer", "8 kVA", 8.0, FILL, INK,
             "kilograms of hot iron"),
            ("Regulate only the circuits that need it", "3 kVA", 3.0, FILL,
             INK, "\u2013 two-thirds removed"),
            ("Series injection: process only the correction", "0.75 kVA",
             0.75, ACCENT, colors.white, "fits on a DIN rail"),
        ]
        maxw = self.width * 0.60
        y = 84
        for label, val, mag, fill, tc, note in rows:
            bw = max(maxw * (mag / 8.0), 46)
            self.tag(0, y + 15, label, INK, 7.6, font="Helvetica-Bold")
            self.canv.saveState()
            self.canv.setStrokeColor(INK if fill is FILL else ACCENT)
            self.canv.setLineWidth(0.9)
            self.canv.setFillColor(fill)
            self.canv.roundRect(0, y, bw, 13, 2, stroke=1, fill=1)
            self.canv.setFillColor(tc)
            self.canv.setFont("Helvetica-Bold", 7.8)
            self.canv.drawString(6, y + 3.6, val)
            self.canv.restoreState()
            self.tag(bw + 7, y + 3.6, note, MUTED, 7)
            y -= 35


class DiagBoard(Diagram):
    """Per-circuit selective regulation inside the enclosure."""

    def __init__(self):
        Diagram.__init__(self, 168)

    def draw(self):
        c = self.canv
        w = self.width

        # enclosure
        encl_r = min(w, 418)
        c.saveState()
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.8)
        c.setDash([2, 2], 0)
        c.roundRect(52, 6, encl_r - 52, 152, 4, stroke=1, fill=0)
        c.setDash()
        c.restoreState()
        self.tag(encl_r, 162, "SINGLE ENCLOSURE", MUTED, 6.8, anchor="r",
                 font="Helvetica-Bold")

        # incoming
        self.tag(0, 104, "MAINS", INK, 7.4, font="Helvetica-Bold")
        self.tag(0, 94, "+ solar", MUTED, 6.8)
        self.arrow(30, 98, 58)
        self.box(60, 84, 40, 28, "RCCB", "+ SPD", fill=FILL, size=7.2)

        ways = [
            ("Air conditioner 1", True, False),
            ("Air conditioner 2", True, False),
            ("Refrigerator", True, False),
            ("Lights & fans", False, False),
            ("Sockets", False, False),
            ("Spare way", False, True),
        ]
        top, step = 142, 23
        mcb_x, reg_x, lbl_x = 116, 154, 224
        c.saveState()
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.8)
        c.line(108, 12, 108, 148)          # busbar
        c.restoreState()
        self.tag(108, 152, "bus", MUTED, 6.4, anchor="c")

        for i, (name, reg, spare) in enumerate(ways):
            y = top - i * step
            c.saveState()
            c.setStrokeColor(MUTED)
            c.setLineWidth(0.7)
            c.line(108, y + 7, mcb_x, y + 7)
            c.restoreState()
            self.box(mcb_x, y, 26, 15, "MCB", fill=FILL, size=6.6)
            if reg:
                self.arrow(mcb_x + 27, y + 7, reg_x - 1, ACCENT)
                self.box(reg_x, y, 62, 15, "REGULATOR", fill=ACCENT, size=6.4)
                self.arrow(reg_x + 63, y + 7, lbl_x - 4, ACCENT)
                self.tag(lbl_x, y + 4, name, INK, 7.4,
                         font="Helvetica-Bold")
            elif spare:
                self.box(reg_x, y, 62, 15, "add later", fill=None,
                         stroke=MUTED, size=6.4, bold=False, dash=[1.6, 1.6],
                         tc=MUTED)
                self.tag(lbl_x, y + 4, name + "  \u2192 clip on a module",
                         MUTED, 7.2)
            else:
                self.arrow(mcb_x + 27, y + 7, lbl_x - 4, MUTED, 0.7)
                self.tag(lbl_x, y + 4, name, MUTED, 7.2)
                self.tag(lbl_x + 74, y + 4, "universal-input \u2014 no need",
                         MUTED, 6.5)

        # legend
        c.saveState()
        c.setFillColor(ACCENT)
        c.rect(52, 0, 8, 5, stroke=0, fill=1)
        c.restoreState()
        self.tag(64, 0.4, "regulated way \u00b7 module sized to its MCB, so the "
                          "circuit can never overload it", MUTED, 6.8)


# ---------------------------------------------------------------- content
BODY = []
A = BODY.append

A(P("INVIDIA CORE", "title"))
A(P("Power protection that disappears into the wall", "sub"))
A(P("Track 1 &nbsp;\u00b7&nbsp; Reimagining the Stabilizer for the Next Decade "
    "&nbsp;\u00b7&nbsp; V-Guard Big Idea Tech Design Contest 2026", "meta"))

A(P("Every Indian home with a stabilizer has <b>two boxes doing one job in the "
    "same place</b> \u2014 a distribution board holding the MCBs and RCCB, and "
    "a stabilizer either plugged in behind the air conditioner or bolted to the "
    "wall beside the board.", "lead"))

A(P("V-Guard already manufactures both halves. <b>Invidia+</b> is their "
    "next-generation smart distribution board: it displays live voltage and "
    "RCCB status. <b>VMT 500/1000 Plus</b> are their mainline stabilizers. The "
    "company sells the box that <i>measures</i> voltage separately from the box "
    "that <i>corrects</i> it \u2014 to the same customer, for the same wall."))

A(P("<b>INVIDIA CORE collapses them into one:</b> MCB, RCCB, surge protection "
    "and solid-state voltage regulation on a single DIN rail inside a single "
    "enclosure. Power protection stops being an appliance the customer buys and "
    "becomes infrastructure the building already has."))

A(Spacer(1, 6))
A(DiagBeforeAfter())

A(P("Why it hasn't been done \u2014 and how to make it work", "h2"))
A(P("The objection is heat and weight. A whole-home relay-tap autotransformer "
    "for an 8\u201310 kVA connection is several kilograms of copper and iron "
    "dissipating real power inside a sealed plastic box. That cannot work, and "
    "we are not proposing it. Two reductions make the concept feasible."))

A(P("Reduction 1 &mdash; regulate circuits, not homes.", "h3"))
A(P("The distribution board is <b>the only location in the home where "
    "selective per-circuit conditioning is physically possible.</b> A board "
    "already splits the supply into separate outgoing ways. So regulate the air "
    "conditioner and refrigerator circuits \u2014 real motors, real compressors "
    "\u2014 and leave lighting, fans and sockets alone, because LED drivers and "
    "BLDC fans are universal-input and do not need it. Roughly two-thirds of "
    "the requirement disappears before any design work begins."))

A(P("Reduction 2 &mdash; process the correction, not the load.", "h3"))
A(P("Rather than passing full load through a transformer, a <b>series "
    "voltage-injection compensator</b> is wired in series and synthesises only "
    "the correction voltage. Correcting \u00b125% on a 3 kVA circuit needs a "
    "converter of roughly 750 VA. This class of direct AC\u2013AC compensator "
    "with step-up and step-down capability is well documented, and field "
    "evaluation of solid-state voltage regulators in low-voltage networks "
    "reports improved voltage profile with about 2.3% lower losses."))

A(Spacer(1, 4))
A(KeepTogether([
    DiagCascade(),
    P("From roughly 8 kVA of hot iron to under 1 kVA of solid-state switching "
      "\u2014 the difference between impossible-in-a-board and "
      "fits-on-a-rail.", "cap"),
]))

A(P("It also delivers what a tap-changer physically cannot: <b>continuous "
    "correction with no voltage steps, no dead-band and no relay "
    "clicking</b> \u2014 and the same silicon can perform surge clamping and "
    "power-factor correction."))

A(Spacer(1, 8))
A(KeepTogether([
    DiagBoard(),
    Spacer(1, 4),
    P("Selective regulation: only the ways that need it carry a module. Spare "
      "ways accept modules later without rewiring.", "cap"),
]))

A(P("Sizing and scalability", "h2"))
A(P("There is deliberately <b>no central stabilizer inside the board</b> "
    "\u2014 only N independent per-way modules. That resolves the three "
    "questions this architecture always attracts."))
A(B("<b>How is capacity guaranteed if a homeowner overloads a circuit?</b> "
    "Each module is rated to <i>the MCB protecting its way</i>, not to expected "
    "load. A 16 A MCB means that circuit physically cannot exceed 16 A. The "
    "protective device already in the enclosure <i>is</i> the capacity "
    "guarantee."))
A(B("<b>What if a regulated circuit also carries lights and minor loads?</b> "
    "Series injection processes only the correction fraction of whatever "
    "current actually flows, so a few hundred watts of incidental load costs "
    "almost nothing. Regulating it is unnecessary, not harmful."))
A(B("<b>What happens when the customer buys another air conditioner?</b> The "
    "electrician clips on another module \u2014 no board replacement, no "
    "rewiring of existing circuits. This requires reserved DIN width and a "
    "pre-wired regulator bus from day one. Because capacity is per-way rather "
    "than pooled, <b>there is no central rating to outgrow.</b>"))
A(B("<b>Overload behaviour.</b> On overcurrent, over-temperature or excess "
    "inrush the module reverts to unregulated pass-through and logs the event. "
    "The circuit keeps working. The regulator must never be the component that "
    "trips the house."))

A(P("Why now", "h2"))
A(P("Two new problems arrive at exactly this location. Rooftop solar under PM "
    "Surya Ghar has crossed <b>50 lakh installations</b>, against 7.94 lakh in "
    "the previous decade, creating reverse power flow and feeder-end voltage "
    "rise that a one-directional appliance stabilizer was never designed for. "
    "And home EV charging is straining household electrical envelopes \u2014 an "
    "AEEE/Kazam study warns residential charging could become the biggest "
    "hurdle to India's EV push, citing inadequate sanctioned loads, poor "
    "earthing and ageing wiring. <b>Both are board-level problems, not "
    "appliance-level ones.</b> And with air-conditioner penetration still around "
    "8% of households, the installed base of vulnerable loads is only "
    "beginning to be built."))

A(P("Novelty, stated honestly", "h2"))
A(P("We invented none of the constituent technologies, and the proposal is "
    "stronger for saying so. Solid-state stabilizers are commercial \u2014 "
    "Sollatek's AVR handles \u221230% to +22% input, correcting at 1250 V/s. "
    "DIN-rail stabilizers exist, but as generic relay-based industrial modules, "
    "not integrated residential consumer units, and not from any mainstream "
    "Indian brand. Series-injection compensation is well published. Smart "
    "Boards exist, including V-Guard's own Invidia+ \u2014 <b>but they measure "
    "and report; none correct.</b>"))
A(P("Our contribution is therefore four specific things: the <b>integration</b> "
    "(no one has combined protection and correction in one certified "
    "residential unit); the <b>per-circuit architecture</b> that makes it "
    "thermally and economically feasible; the <b>channel repositioning</b> "
    "below; and <b>portfolio fit</b> \u2014 V-Guard already makes stabilizers, "
    "switchgear, boards and cable. For almost any competitor this would be an "
    "acquisition. For V-Guard it is an integration."))

A(P("Business value \u2014 the channel argument", "h2"))
A(P("A stabilizer is a <b>retail afterthought.</b> The customer buys an air "
    "conditioner, remembers they need a stabilizer, walks into a shop and "
    "compares prices across brands. Low margin, high competition, "
    "brand-fragile. A distribution board is <b>specified by the electrician or "
    "builder during construction</b>, before the customer has an opinion, and "
    "is never price-shopped by the homeowner. There is no comparison moment."))
A(P("Integrating the stabilizer into the board moves power protection out of "
    "the price-comparison aisle and into the electrician's specification "
    "decision.", "pull"))
A(P("That is a channel V-Guard already owns through switchgear and wires. It "
    "captures the customer years earlier \u2014 at wiring stage rather than "
    "appliance-purchase stage \u2014 and the attachment is durable, because "
    "nobody removes a distribution board to save Rs\u00a01,500. This matters "
    "because V-Guard's problem is margin, not volume: FY25-26 revenue grew 7.0% "
    "to Rs\u00a05,966 crore while PAT fell 1.7% to Rs\u00a0308 crore. The "
    "stabilizer market is growing \u2014 USD 770.65 million in 2025 to USD "
    "1,202.60 million by 2034 \u2014 but on price."))
A(P("For the consumer: one box instead of two, whole-circuit protection so a "
    "new appliance is covered automatically, no relay clicking, and nothing on "
    "the wall."))

A(P("Risks and honest limitations", "h2"))
A(B("<b>Thermal management is make-or-break.</b> If the enclosure cannot hold "
    "MCB ambient within its derating curve, the concept fails. The per-circuit "
    "and partial-power choices exist to make this tractable, and the thermal "
    "model in Phase 3 is built to answer it before any hardware is committed. "
    "Our working estimate is ~25\u201345 W dissipated per module, which puts "
    "the practical ceiling at <b>two to three regulated ways per "
    "enclosure</b> \u2014 not unlimited."))
A(B("<b>Certification.</b> Boards fall under IS 13032, stabilizers under IS "
    "9815. A combined unit is effectively a new product category requiring BIS "
    "engagement \u2014 a real timeline cost, not a footnote."))
A(B("<b>No sub-circuit selectivity.</b> A board cannot see inside a circuit. "
    "If an air conditioner shares a way with lights, the remedy is a dedicated "
    "way \u2014 already standard practice for heavy loads \u2014 or a plug-in "
    "stabilizer for that one unit. Depth is the other physical constraint: the "
    "module must trade width for depth to fit a standard recess, making this a "
    "<b>wider board, not a deeper one</b>, with the front cover carrying the "
    "thermal path. Surface-mounted installations are unconstrained; concealed "
    "fitting needs a nine-inch wall."))
A(B("<b>Correction depth bounds the input range.</b> Converter size scales with "
    "how much voltage must be injected, so INVIDIA CORE targets roughly "
    "170\u2013290 V \u2014 not the 110\u2013500 V of a mainline stabilizer. "
    "Homes with extreme excursions still need that separate box. Cost per kVA "
    "is also higher than relay-tap iron at low volume, so this launches "
    "premium."))
A(B("<b>The voltage problem is shrinking.</b> Grid quality is improving under "
    "RDSS and appliances tolerate wider ranges. The long-run case rests on the "
    "board becoming the home's power-quality and load-management node \u2014 "
    "which is why the architecture targets solar reverse flow and EV load "
    "management, not just low mains voltage."))

A(P("Phase 3 plan \u2014 modelling first", "h2"))
A(P("The decisive question is thermal, and it is answerable analytically before "
    "hardware exists. We lead with simulation and reserve bench work for "
    "validation."))
A(B("<b>Lumped-parameter thermal model</b> of the enclosure: junction \u2192 "
    "heatsink \u2192 internal air \u2192 wall/front-cover paths, swept across "
    "module count (1\u20134), enclosure depth (55\u201395 mm) and vent area. "
    "Output: the maximum number of regulated ways that keeps MCB ambient inside "
    "its derating curve \u2014 the single most important number in the "
    "proposal."))
A(B("<b>Converter simulation</b> (SPICE / Python): series-injection waveforms "
    "for step-up and step-down operation, regulation versus input across "
    "170\u2013290 V, efficiency versus load, and step response contrasted "
    "against a relay tap-changer's dead-band."))
A(B("<b>Parametric study of the core trade-off:</b> converter VA versus correction "
    "depth, establishing where series injection stops being cheaper than a tap "
    "transformer \u2014 and therefore the product's honest input range."))
A(B("<b>Enclosure CAD plus an interactive configurator:</b> the wider, "
    "shallower geometry with a finned front-cover thermal path, confirming fit "
    "in a standard 75\u201395 mm recess, alongside a tool showing per-circuit "
    "module allocation, MCB-based sizing and cumulative heat budget."))
A(B("<b>Bench validation, if time permits:</b> a low-voltage scaled-down "
    "injection stage and thermocouple mapping in a real enclosure \u2014 the "
    "confirmation step, not the foundation of the argument."))

# ---------------------------------------------------------------- assemble
def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 13 * mm, PAGE_W - MARGIN, 13 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 9 * mm, "INVIDIA CORE  \u00b7  Track 1 Executive Summary")
    canvas.drawRightString(PAGE_W - MARGIN, 9 * mm, "%d" % doc.page)
    canvas.restoreState()


doc = BaseDocTemplate(
    "INVIDIA-CORE-Executive-Summary.pdf", pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN, bottomMargin=20 * mm,
    title="INVIDIA CORE - Track 1 Executive Summary",
    author="V-Guard Big Idea Tech Design Contest 2026",
)
frame = Frame(MARGIN, 20 * mm, CONTENT_W, PAGE_H - MARGIN - 20 * mm,
              id="body", showBoundary=0)
doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
doc.build(BODY)
print("PDF written.")
