#!/usr/bin/env python3
"""NAKSHA executive summary - Track 4."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                               PageTemplate, Paragraph, Spacer)

INK = colors.HexColor("#1B1B1B")
MUTED = colors.HexColor("#6E6E6E")
ACCENT = colors.HexColor("#1F6E5A")
RULE = colors.HexColor("#D4D4D4")
FILL = colors.HexColor("#EFF1F0")

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN


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
                  spaceAfter=13),
    "h2": style("h2", fontName="Helvetica-Bold", fontSize=11.2, leading=13.6,
                spaceBefore=8.5, spaceAfter=3.5, keepWithNext=1),
    "body": style("body", alignment=TA_JUSTIFY, spaceAfter=4),
    "lead": style("lead", fontSize=10.2, leading=14, spaceAfter=5),
    "bullet": style("bullet", alignment=TA_JUSTIFY, leftIndent=11,
                    bulletIndent=1, spaceAfter=2.9),
    "pull": style("pull", fontName="Helvetica-Bold", fontSize=10,
                  leading=14.2, textColor=ACCENT, leftIndent=10,
                  spaceBefore=5, spaceAfter=7),
    "cap": style("cap", fontSize=7.8, leading=10.4, textColor=MUTED,
                 spaceBefore=3, spaceAfter=9),
}


def P(t, s="body"):
    return Paragraph(t, S[s])


def B(t):
    return Paragraph(t, S["bullet"], bulletText="\u2013")


class Diagram(Flowable):
    def __init__(self, h):
        Flowable.__init__(self)
        self.width, self.height = CONTENT_W, h

    def wrap(self, *_):
        return self.width, self.height

    def box(self, x, y, w, h, label, sub=None, fill=None, stroke=INK,
            size=7.6, dash=None, tc=None, bold=True):
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
            c.drawCentredString(x + w / 2, y + h / 2 + 1.6, label)
            c.setFont("Helvetica", size - 1.1)
            c.setFillColor(tc or (colors.white if fill == ACCENT else MUTED))
            c.drawCentredString(x + w / 2, y + h / 2 - 6.6, sub)
        else:
            c.drawCentredString(x + w / 2, y + h / 2 - size / 2 + 1.2, label)
        c.restoreState()

    def arrow(self, x1, y, x2, colr=INK, lw=0.9):
        c = self.canv
        c.saveState()
        c.setStrokeColor(colr)
        c.setFillColor(colr)
        c.setLineWidth(lw)
        c.line(x1, y, x2 - 3, y)
        p = c.beginPath()
        p.moveTo(x2, y)
        p.lineTo(x2 - 4.2, y + 2.3)
        p.lineTo(x2 - 4.2, y - 2.3)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()

    def tag(self, x, y, t, colr=MUTED, size=7.2, anchor="l",
            font="Helvetica"):
        c = self.canv
        c.saveState()
        c.setFillColor(colr)
        c.setFont(font, size)
        if anchor == "c":
            c.drawCentredString(x, y, t)
        elif anchor == "r":
            c.drawRightString(x, y, t)
        else:
            c.drawString(x, y, t)
        c.restoreState()


class DiagPipeline(Diagram):
    def __init__(self):
        Diagram.__init__(self, 150)

    def draw(self):
        w = self.width
        self.box(0, 96, 96, 40, "ARCHITECT'S", "plan (PDF/DWG)", fill=FILL)
        self.arrow(100, 116, 122)
        self.box(126, 88, 130, 56, "NAKSHA ENGINE",
                 "IS 732 / IS 3043 rules", fill=ACCENT, stroke=ACCENT,
                 size=8.4)
        self.tag(191, 78, "circuits \u00b7 DB siting \u00b7 routing", MUTED,
                 6.6, anchor="c")
        outs = [("WIRE SCHEDULE", "exact metres, by size", 136),
                ("SITE MARKING", "phone AR or assisted", 84),
                ("AS-BUILT RECORD", "permanent digital map", 32)]
        for label, sub, y in outs:
            self.arrow(260, 116, 296, ACCENT)
            self.box(300, y - 8, 150, 34, label, sub, fill=None,
                     stroke=ACCENT, size=7.4, tc=INK)
            self.canv.saveState()
            self.canv.setStrokeColor(ACCENT)
            self.canv.setLineWidth(0.9)
            self.canv.line(280, 116, 280, y + 9)
            self.canv.line(280, y + 9, 300, y + 9)
            self.canv.restoreState()
        self.tag(462, 145, "\u2192 a V-Guard order", ACCENT, 7.4,
                 font="Helvetica-Bold")
        self.tag(462, 93, "\u2192 correct installation", MUTED, 7.4)
        self.tag(462, 41, "\u2192 lifetime lock-in", MUTED, 7.4)


class DiagChannel(Diagram):
    def __init__(self):
        Diagram.__init__(self, 118)

    def draw(self):
        w = self.width
        half = (w - 22) / 2
        self.tag(0, 106, "WHAT EVERY COMPETITOR SHIPS", MUTED, 7.4,
                 font="Helvetica-Bold")
        self.box(0, 40, half, 56, "LOYALTY POINTS",
                 "scan QR \u00b7 earn \u00b7 redeem", fill=FILL, size=9)
        self.tag(0, 26, "RR Connect \u00b7 Finolex Samruddhi \u00b7 Polycab "
                        "Experts \u00b7 Havells", MUTED, 6.8)
        self.tag(0, 12, "Polycab reaches ~2.5 lakh electricians this way.",
                 MUTED, 6.8)
        x2 = half + 22
        self.tag(x2, 106, "WHAT NAKSHA SHIPS", ACCENT, 7.4,
                 font="Helvetica-Bold")
        self.box(x2, 40, half, 56, "A TOOL THAT DOES THE WORK",
                 "designs the job \u00b7 sizes the wire", fill=ACCENT,
                 stroke=ACCENT, size=9)
        self.tag(x2, 26, "The channel is already digitised. Nobody has put "
                         "anything useful in it.", INK, 6.8,
                 font="Helvetica-Bold")


class DiagTiers(Diagram):
    def __init__(self):
        Diagram.__init__(self, 104)

    def draw(self):
        rows = [("Tier 1 \u00b7 App", "Free, all-India", "phone AR marking, "
                 "zero hardware, infinitely scalable", FILL, INK),
                ("Tier 2 \u00b7 Assisted", "Metro cities", "trained V-Guard "
                 "marking partner, paid service", FILL, INK),
                ("Tier 3 \u00b7 Flagship", "Showcase only", "robotic / laser "
                 "layout \u2014 built for marketing, not margin", ACCENT,
                 colors.white)]
        y = 74
        for name, scope, note, fill, tc in rows:
            self.box(0, y, 118, 24, name, fill=fill,
                     stroke=INK if fill is FILL else ACCENT, size=7.6, tc=tc)
            self.tag(128, y + 14, scope, INK, 7.8, font="Helvetica-Bold")
            self.tag(128, y + 4, note, MUTED, 7.2)
            y -= 34


BODY = []
A = BODY.append

A(P("NAKSHA", "title"))
A(P("V-Guard designs the wiring, then sells the wire", "sub"))
A(P("Track 4 &nbsp;\u00b7&nbsp; Reimagining V-Guard for an AI Powered Era "
    "&nbsp;\u00b7&nbsp; V-Guard Big Idea Tech Design Contest 2026", "meta"))

A(P("Wire is the most commoditised thing V-Guard sells. It competes on price, "
    "brand recall and whatever the electrician happens to have in his van. "
    "<b>NAKSHA changes what is being sold: not a coil of wire, but a designed "
    "electrical installation that happens to specify V-Guard wire.</b>", "lead"))

A(P("An owner, contractor or electrician uploads the architect's floor plan and "
    "answers a few questions about appliances. NAKSHA returns a complete "
    "residential electrical design \u2014 circuit split, distribution board "
    "siting, conduit routing, point placement \u2014 generated against "
    "<b>IS 732</b> and <b>IS 3043</b>. It produces three outputs: an exact "
    "<b>wire schedule in metres by size</b>, on-site <b>marking guidance</b> so "
    "the conduits actually go where the design says, and a permanent "
    "<b>as-built digital record</b> of where every cable in the house lives."))

A(Spacer(1, 4))
A(KeepTogether([DiagPipeline(),
                P("One upload, three outputs. The middle one gets the job "
                  "built correctly; the first one is a purchase order; the "
                  "third one never leaves the house.", "cap")]))

A(P("The problem this actually solves", "h2"))
A(P("Indian homes are wired from memory. The electrician works without a "
    "drawing, improvises conduit routes, and leaves behind no record. The "
    "consequences are measurable: <b>roughly 42% of building fires in India are "
    "attributed to electrical short circuits</b>, and fire officials note that "
    "the phrase conceals ageing wiring, overloaded circuits, substandard "
    "material and years of neglect accumulating behind plaster."))
A(P("The standards already exist. BIS publishes <b>IS 732</b> for wiring "
    "installation and <b>IS 3043</b> for earthing, and the CEA (Measures "
    "relating to Safety and Electric Supply) Regulations, 2023 require "
    "installation work to be carried out by a licensed electrical contractor "
    "under competent supervision. In February 2025 Parliament was asked why "
    "periodic household electrical safety checks are still not mandated."))
A(P("<b>So the gap is not the code. It is that nothing translates the code into "
    "a drawing anyone on an Indian residential site will actually use.</b> And "
    "because there is no drawing, there is no as-built record \u2014 which is "
    "why people drill into live cables and why renovation means guessing."))

A(P("The channel insight", "h2"))
A(P("Every major Indian wire brand has already digitised its electrician "
    "relationship. RR Kabel has RR Connect, Finolex has Samruddhi, Havells has "
    "an electrician app, and Polycab's Experts platform reaches around "
    "<b>2.5 lakh electricians and retailers</b>, which the company describes in "
    "its FY26 annual report as a grassroots influencer channel."))
A(P("Every one of them is a loyalty scheme. Scan a QR code, collect points, "
    "redeem a gift.", "pull"))
A(P("The distribution channel is built, the electricians are on smartphones, "
    "and no brand has put a tool in that channel that does any actual work. "
    "An electrician does not want points. He wants the load calculation done, "
    "the wire sizes decided, the material list totalled, and a defensible "
    "answer when the owner asks why it costs what it costs."))

A(Spacer(1, 3))
A(KeepTogether([DiagChannel(),
                P("The asset V-Guard needs already exists in the industry. "
                  "Only its content is wrong.", "cap")]))

A(P("Technology", "h2"))
A(B("<b>Plan understanding.</b> Vectorise the uploaded plan; segment rooms, "
    "walls, doors and openings. Room-type inference from dimensions, adjacency "
    "and labels, with human confirmation rather than blind trust."))
A(B("<b>Rule engine.</b> IS 732 and IS 3043 encoded as explicit, auditable "
    "constraints \u2014 separate lighting and power circuits, dedicated ways "
    "for heavy loads, points-per-circuit limits, earthing requirements, "
    "diversity factors for load estimation. Deterministic and inspectable, not "
    "a language model guessing at safety rules."))
A(B("<b>Layout optimisation.</b> This is the core computational problem: place "
    "the distribution board and route conduits to minimise total wire length "
    "and voltage drop, subject to the rule set and to buildable chase "
    "geometry. A graph problem over the room adjacency network, solved with "
    "shortest-path routing plus a metaheuristic over board placement."))
A(B("<b>Bill of quantities.</b> Wire length per size with waste allowance, "
    "conduit, boxes, switchgear, mapped directly onto V-Guard SKUs."))
A(B("<b>Site delivery.</b> Phone-based AR overlays the design onto the actual "
    "wall using the plan geometry and device pose. Cheap, works on any modern "
    "handset, and requires no equipment on site."))
A(B("<b>As-built capture.</b> The electrician confirms or corrects each run "
    "as it is laid, before plastering. The corrected model becomes the "
    "homeowner's permanent record and the training signal that improves the "
    "generator."))

A(P("Novelty, stated honestly", "h2"))
A(P("The components are not new and the proposal is stronger for saying so. "
    "Automated electrical takeoff is a mature commercial category \u2014 tools "
    "such as drawer.ai already accept PDF drawings and export quantities, "
    "device properties and <b>wire lengths with marked-up routing</b>, and "
    "Kreo, Trimble Accubid and PlanSwift serve the same market. Academic work "
    "presented at ISARC 2026 automates outlet-to-circuit and "
    "circuit-to-panelboard assignment in a CAD\u2013BIM workflow. Robotic "
    "site layout is also solved: Dusty Robotics' FieldPrinter has printed "
    "coordinated models on more than <b>300 million square feet</b> of slab."))
A(P("All of that serves <b>Western commercial contractors bidding large "
    "projects.</b> None of it serves an electrician wiring a 3BHK in Kochi, "
    "none of it encodes Indian standards, and none of it is distributed by "
    "the company that sells the wire."))
A(P("Our contribution is therefore positional, not algorithmic: <b>Indian code "
    "compliance as the rule set</b>, <b>residential scale</b> where no drawing "
    "exists today rather than commercial scale where one already does, "
    "<b>distribution through a channel V-Guard already owns</b>, and the "
    "<b>as-built record</b> as a durable asset none of the takeoff tools "
    "produce because their users leave the site and never return."))

A(P("Business value", "h2"))
A(B("<b>Every design is a purchase order.</b> The output is a wire schedule in "
    "metres by size. Specifying the material is a categorically stronger "
    "position than advertising to whoever walks into a shop \u2014 this is the "
    "Asian Paints move, which used Beautiful Homes services to escape "
    "commodity paint competition, and which Berger followed with Express "
    "Painting."))
A(B("<b>It captures the decision years earlier.</b> Wiring is specified during "
    "construction, before the owner has any brand opinion, and it is never "
    "re-shopped. Rewiring a finished house is unthinkable."))
A(B("<b>It creates a portfolio funnel.</b> The same plan positions the water "
    "heater, chimney, RO and gas point \u2014 all V-Guard categories, all "
    "decided at construction stage, all currently decided by whoever is "
    "standing there."))
A(B("<b>It is a margin story, not a volume story.</b> V-Guard's FY25-26 "
    "revenue grew 7.0% to Rs\u00a05,966 crore while PAT fell 1.7% to "
    "Rs\u00a0308 crore. Commodity wire cannot fix that; specified systems can."))
A(B("<b>The as-built record is the lock-in.</b> A household whose wiring map "
    "lives in V-Guard's app has a reason to return for every future addition, "
    "fault and renovation."))

A(P("On scale \u2014 and the marking problem", "h2"))
A(P("A national service business is genuinely hard: staff, training, equipment, "
    "quality control. We do not propose one. The design engine scales at "
    "software cost; only the physical marking needs people, so we separate "
    "them deliberately."))
A(Spacer(1, 2))
A(DiagTiers())
A(P("Tier 1 carries the strategy \u2014 free, national, zero marginal cost, "
    "and it is where the wire schedules come from. Tier 3 exists to be "
    "photographed. Treating the flagship as a marketing instrument rather than "
    "a P&amp;L line is the honest position, and it is exactly how paint "
    "companies launched their service brands."))

A(P("Risks and honest limitations", "h2"))
A(B("<b>Plan quality is the hard input problem.</b> Indian residential plans "
    "are often scanned, hand-marked, incomplete or dimensionally unreliable. "
    "The engine must degrade gracefully to guided manual tracing, and the "
    "first release should assume human confirmation of every inferred room."))
A(B("<b>Liability.</b> Software that produces an electrical design in a "
    "jurisdiction where a licensed contractor is legally responsible must "
    "position itself as a decision aid the contractor signs off, not as the "
    "designer of record. This needs legal structuring before launch."))
A(B("<b>Electrician adoption is the real commercial risk</b>, not the "
    "technology. Experienced electricians may see the tool as a challenge to "
    "their judgment. It has to visibly save them time on load calculation and "
    "estimation on day one, or it will be ignored."))
A(B("<b>AR marking accuracy on a construction site</b> is unproven at the "
    "tolerances conduit chasing needs. Tier 1 should therefore promise "
    "guidance and dimensioned reference marks, not millimetre placement."))
A(B("<b>Track fit.</b> This is a Track 4 entry on the basis that the brief "
    "invites solutions \u201caligned with its core categories,\u201d and wires "
    "and switchgear are core. We note plainly that the intelligence sits in "
    "the design tool rather than inside a powered product \u2014 though its "
    "output, the as-built model, becomes a permanent fixture of the home."))

A(P("Phase 3 plan", "h2"))
A(B("<b>Working layout generator</b> on real Indian floor plans: rooms in, "
    "circuits and routed conduits out, with the IS 732 rule set explicit and "
    "each decision traceable to a clause."))
A(B("<b>Optimisation study:</b> total wire length and voltage drop versus "
    "distribution-board placement across several house typologies \u2014 "
    "quantifying the material saving a good layout produces over an improvised "
    "one."))
A(B("<b>Interactive browser demo</b> generating and visualising a design from "
    "an uploaded plan, plus a costed bill of quantities."))
A(B("<b>AR feasibility test:</b> phone-based overlay on a real wall, with "
    "measured registration error reported honestly rather than asserted."))


def footer(cv, doc):
    cv.saveState()
    cv.setStrokeColor(RULE)
    cv.setLineWidth(0.5)
    cv.line(MARGIN, 13 * mm, PAGE_W - MARGIN, 13 * mm)
    cv.setFont("Helvetica", 7)
    cv.setFillColor(MUTED)
    cv.drawString(MARGIN, 9 * mm, "NAKSHA  \u00b7  Track 4 Executive Summary")
    cv.drawRightString(PAGE_W - MARGIN, 9 * mm, "%d" % doc.page)
    cv.restoreState()


doc = BaseDocTemplate("NAKSHA-Executive-Summary.pdf", pagesize=A4,
                      leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN,
                      bottomMargin=20 * mm,
                      title="NAKSHA - Track 4 Executive Summary",
                      author="V-Guard Big Idea Tech Design Contest 2026")
doc.addPageTemplates([PageTemplate(id="m", frames=[
    Frame(MARGIN, 20 * mm, CONTENT_W, PAGE_H - MARGIN - 20 * mm, id="b")],
    onPage=footer)])
doc.build(BODY)
print("NAKSHA PDF written.")
