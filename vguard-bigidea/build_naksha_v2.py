#!/usr/bin/env python3
"""NAKSHA executive summary, structured to the contest's four required aspects.
Also emits a standalone one-page diagram for use in the pitch video."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                               PageTemplate, Paragraph, Spacer, Table,
                               TableStyle)

INK = colors.HexColor("#1B1B1B")
MUTED = colors.HexColor("#6E6E6E")
ACCENT = colors.HexColor("#1F6E5A")
RULE = colors.HexColor("#CFCFCF")
FILL = colors.HexColor("#EFF1F0")

PW, PH = A4
MG = 20 * mm
CW = PW - 2 * MG


def st(name, **kw):
    b = dict(name=name, fontName="Helvetica", fontSize=9.4, leading=13.2,
             textColor=INK, spaceAfter=0)
    b.update(kw)
    return ParagraphStyle(**b)


S = {
    "title": st("title", fontName="Helvetica-Bold", fontSize=19, leading=22,
                spaceAfter=2),
    "sub": st("sub", fontSize=10, leading=13, textColor=ACCENT, spaceAfter=10),
    "h2": st("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=14,
             spaceBefore=11, spaceAfter=4, keepWithNext=1, textColor=ACCENT),
    "body": st("body", alignment=TA_JUSTIFY, spaceAfter=5),
    "lead": st("lead", fontSize=10.3, leading=14.2, spaceAfter=6),
    "bul": st("bul", alignment=TA_JUSTIFY, leftIndent=11, bulletIndent=1,
              spaceAfter=3.2),
    "cap": st("cap", fontSize=7.8, leading=10.4, textColor=MUTED,
              spaceBefore=3, spaceAfter=8),
    "small": st("small", fontSize=8.2, leading=11, textColor=MUTED),
}


def P(t, s="body"):
    return Paragraph(t, S[s])


def B(t):
    return Paragraph(t, S["bul"], bulletText="\u2022")


# ----------------------------------------------------------- the one diagram
def draw_pipeline(c, x0, y0, scale=1.0, big=False):
    """Draws the plan -> engine -> three outputs diagram."""
    def sx(v):
        return x0 + v * scale

    def sy(v):
        return y0 + v * scale

    fs = (9.5 if big else 7.4) * 1.0
    fs2 = fs - 1.2

    def box(bx, by, bw, bh, label, sub=None, fill=None, stroke=INK, size=fs,
            tc=None):
        c.saveState()
        c.setStrokeColor(stroke)
        c.setLineWidth(1.1 if big else 0.9)
        if fill is not None:
            c.setFillColor(fill)
            c.roundRect(sx(bx), sy(by), bw * scale, bh * scale, 3 * scale,
                        stroke=1, fill=1)
        else:
            c.roundRect(sx(bx), sy(by), bw * scale, bh * scale, 3 * scale,
                        stroke=1, fill=0)
        c.setFillColor(tc or (colors.white if fill == ACCENT else INK))
        c.setFont("Helvetica-Bold", size)
        cx = sx(bx) + bw * scale / 2
        if sub:
            c.drawCentredString(cx, sy(by) + bh * scale / 2 + 2 * scale, label)
            c.setFont("Helvetica", size - 1.3)
            c.setFillColor(tc or (colors.white if fill == ACCENT else MUTED))
            c.drawCentredString(cx, sy(by) + bh * scale / 2 - 7 * scale, sub)
        else:
            c.drawCentredString(cx, sy(by) + bh * scale / 2 - size / 3, label)
        c.restoreState()

    def arrow(ax1, ay, ax2, colr=INK):
        c.saveState()
        c.setStrokeColor(colr)
        c.setFillColor(colr)
        c.setLineWidth(1.1 if big else 0.9)
        c.line(sx(ax1), sy(ay), sx(ax2) - 4, sy(ay))
        p = c.beginPath()
        p.moveTo(sx(ax2), sy(ay))
        p.lineTo(sx(ax2) - 5 * scale, sy(ay) + 2.8 * scale)
        p.lineTo(sx(ax2) - 5 * scale, sy(ay) - 2.8 * scale)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()

    def tag(tx, ty, t, colr=MUTED, size=fs2, font="Helvetica"):
        c.saveState()
        c.setFillColor(colr)
        c.setFont(font, size)
        c.drawString(sx(tx), sy(ty), t)
        c.restoreState()

    box(0, 96, 100, 42, "ARCHITECT'S PLAN", "PDF or drawing", fill=FILL)
    arrow(104, 117, 126)
    box(130, 88, 130, 58, "NAKSHA ENGINE", "national wiring codes",
        fill=ACCENT, stroke=ACCENT)
    tag(133, 74, "circuits, board siting, routing")

    outs = [("WIRE SCHEDULE", "exact metres, by size", 140,
             "a purchase order"),
            ("SITE MARKING", "phone AR overlay", 88, "built correctly"),
            ("AS-BUILT RECORD", "permanent wiring map", 36,
             "lifetime lock-in")]
    for label, sub, oy, note in outs:
        c.saveState()
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.1 if big else 0.9)
        c.line(sx(264), sy(117), sx(282), sy(117))
        c.line(sx(282), sy(117), sx(282), sy(oy + 19))
        c.line(sx(282), sy(oy + 19), sx(300), sy(oy + 19))
        c.restoreState()
        box(300, oy, 152, 38, label, sub, fill=None, stroke=ACCENT, tc=INK)
        tag(462, oy + 16, "\u2192 " + note, ACCENT, fs2, "Helvetica-Bold")


class DiagFlow(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width, self.height = CW, 152

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        draw_pipeline(self.canv, 0, -30, scale=1.0)


# ----------------------------------------------------------------- content
BODY = []
A = BODY.append

A(P("NAKSHA", "title"))
A(P("V-Guard designs the wiring, then sells the wire", "sub"))

hdr = Table([["Track", "Track 4: Reimagining V-Guard for an AI Powered Era"],
             ["Team name", ""],
             ["Institute", ""],
             ["Team members", ""]],
            colWidths=[80, CW - 80], rowHeights=[15] * 4)
hdr.setStyle(TableStyle([
    ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 8.4),
    ("FONT", (1, 0), (1, -1), "Helvetica", 8.4),
    ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
    ("TEXTCOLOR", (1, 0), (1, -1), INK),
    ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
    ("LINEABOVE", (0, 0), (-1, 0), 0.4, RULE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
A(hdr)
A(Spacer(1, 10))

# ---- 1
A(P("1. Brief of the Idea / Solution", "h2"))
A(P("Wire is the most commoditised product V-Guard sells. It competes on price, "
    "brand recall, and whatever the electrician happens to be carrying. "
    "<b>NAKSHA changes what is being sold: not a coil of wire, but a designed "
    "electrical installation that specifies V-Guard wire.</b>", "lead"))
A(P("An owner, contractor or electrician uploads the architect's floor plan and "
    "answers a few questions about appliances. NAKSHA returns a complete "
    "residential electrical design: circuit split, distribution board siting, "
    "conduit routing and point placement, generated against the national wiring "
    "and earthing codes."))
A(Spacer(1, 3))
A(KeepTogether([DiagFlow(),
                P("One upload, three outputs. The first is effectively a "
                  "purchase order, the second gets the job built correctly, "
                  "and the third never leaves the house.", "cap")]))
A(P("Indian homes are wired from memory. The electrician works without a "
    "drawing, improvises conduit routes and leaves no record behind. Roughly "
    "42% of building fires in India are attributed to electrical short "
    "circuits, a phrase that conceals ageing wiring, overloaded circuits and "
    "substandard material. The codes already exist and regulations already "
    "require a licensed contractor. <b>Nothing translates those rules into a "
    "drawing anyone on an Indian residential site will actually use, and with "
    "no drawing there is no record.</b>"))

# ---- 2
A(P("2. Novelty and Innovation", "h2"))
A(P("The components are not new, and the proposal is stronger for saying so. "
    "Automated electrical takeoff is a mature commercial category: tools such "
    "as drawer.ai already accept PDF drawings and return quantities and wire "
    "lengths with marked-up routing, and Kreo, Trimble Accubid and PlanSwift "
    "serve the same market. Robotic site layout is also solved, with Dusty "
    "Robotics having printed coordinated models onto more than 300 million "
    "square feet of slab."))
A(P("All of it serves Western commercial contractors bidding large projects. "
    "Our contribution is positional:"))
A(B("<b>Indian codes as the rule set</b>, which none of the existing tools "
    "encode."))
A(B("<b>Residential scale</b>, where no drawing exists today, rather than "
    "commercial scale where one already does."))
A(B("<b>Distribution through a channel V-Guard already owns.</b> Every major "
    "Indian wire brand has already digitised its electrician relationship. "
    "Polycab's Experts platform alone reaches around 2.5 lakh electricians and "
    "retailers. <b>Every one of them is a loyalty scheme: scan a code, collect "
    "points, redeem a gift. Nobody has put a tool in that channel that does "
    "any actual work.</b>"))
A(B("<b>The as-built record</b>, which no takeoff tool produces because its "
    "users leave the site and never return."))

# ---- 3
A(P("3. Technology Proposed", "h2"))
A(B("<b>Plan understanding.</b> Vectorise the uploaded plan, then segment "
    "rooms, walls and openings. Room type is inferred from dimensions and "
    "adjacency, with human confirmation rather than blind trust."))
A(B("<b>Rule engine.</b> The national wiring and earthing codes encoded as "
    "explicit, auditable constraints: separate lighting and power circuits, "
    "dedicated ways for heavy loads, points per circuit, earthing "
    "requirements and diversity factors. Deterministic and inspectable, not a "
    "language model guessing at safety rules."))
A(B("<b>Layout optimisation.</b> The core computational problem. Place the "
    "distribution board and route conduits to minimise total wire length and "
    "voltage drop, subject to the rule set and to buildable chase geometry. A "
    "graph problem over the room adjacency network, solved with shortest path "
    "routing plus a search over board placement."))
A(B("<b>Bill of quantities.</b> Wire length per size with waste allowance, "
    "plus conduit, boxes and switchgear, mapped directly onto V-Guard SKUs."))
A(B("<b>Site delivery.</b> A phone based AR overlay puts the design on the "
    "actual wall. Cheap, works on any modern handset, needs no equipment on "
    "site. A trained marking partner is offered in metros, and a robotic "
    "layout flagship exists as a showcase rather than as a margin line."))
A(B("<b>As-built capture.</b> The electrician confirms each run as it is laid, "
    "before plastering. The corrected model becomes the homeowner's permanent "
    "record and the training signal that improves the generator."))

# ---- 4
A(P("4. End Consumer and Business Value", "h2"))
A(P("<b>For the consumer</b>, a home wired to code rather than to habit, an "
    "itemised material list that makes overcharging visible, and a permanent "
    "map of where every cable runs, which is what makes future renovation and "
    "fault finding safe instead of speculative."))
A(P("<b>For the electrician</b>, the load calculation done, wire sizes decided, "
    "the material list totalled, and a defensible answer when the owner asks "
    "why it costs what it costs. He does not want loyalty points."))
A(P("<b>For V-Guard</b>, four things:"))
A(B("<b>Every design is a purchase order</b>, because the output is a wire "
    "schedule in metres by size. Specifying the material is a stronger "
    "position than advertising to whoever walks into a shop. This is the Asian "
    "Paints move, which used Beautiful Homes services to escape commodity "
    "paint competition, and which Berger followed with Express Painting."))
A(B("<b>It captures the decision years earlier.</b> Wiring is specified during "
    "construction, before the owner has any brand opinion, and it is never "
    "re-shopped. You cannot rewire a finished house."))
A(B("<b>It opens a portfolio funnel.</b> The same plan positions the water "
    "heater, chimney, RO and gas point, all V-Guard categories, all decided at "
    "construction stage."))
A(B("<b>It is a margin story.</b> FY25-26 revenue grew 7.0% to Rs 5,966 crore "
    "while PAT fell 1.7% to Rs 308 crore. Commodity wire cannot fix that; "
    "specified systems can."))

# ---- closing
A(P("Risks we acknowledge", "h2"))
A(P("Indian residential plans are often scanned, hand marked or dimensionally "
    "unreliable, so the first release must degrade gracefully to guided manual "
    "tracing. Because a licensed contractor is legally responsible for the "
    "installation, the tool must be positioned as a decision aid he signs off, "
    "not as designer of record. AR marking accuracy on a live site is unproven "
    "at the tolerance conduit chasing needs, so we promise dimensioned guidance "
    "rather than millimetre placement. <b>The real risk is adoption, not "
    "technology:</b> the tool must visibly save an electrician time on load "
    "calculation and estimating on day one, or it will be ignored. That is what "
    "we would test first."))


def footer(cv, doc):
    cv.saveState()
    cv.setStrokeColor(RULE)
    cv.setLineWidth(0.5)
    cv.line(MG, 13 * mm, PW - MG, 13 * mm)
    cv.setFont("Helvetica", 7)
    cv.setFillColor(MUTED)
    cv.drawString(MG, 9 * mm, "NAKSHA  |  Executive Summary  |  Track 4")
    cv.drawRightString(PW - MG, 9 * mm, "%d" % doc.page)
    cv.restoreState()


doc = BaseDocTemplate("NAKSHA-Executive-Summary.pdf", pagesize=A4,
                      leftMargin=MG, rightMargin=MG, topMargin=MG,
                      bottomMargin=20 * mm, title="NAKSHA Executive Summary",
                      author="V-Guard Big Idea Tech Design Contest 2026")
doc.addPageTemplates([PageTemplate(id="m", frames=[
    Frame(MG, 20 * mm, CW, PH - MG - 20 * mm, id="b")], onPage=footer)])
doc.build(BODY)
print("summary written")

# ------------------------------------------------- standalone video diagram
LW, LH = landscape(A4)
c = pdfcanvas.Canvas("NAKSHA-Diagram.pdf", pagesize=(LW, LH))
c.setTitle("NAKSHA - how it works")
c.setFillColor(colors.white)
c.rect(0, 0, LW, LH, stroke=0, fill=1)
c.setFillColor(ACCENT)
c.rect(0, 0, 9, LH, stroke=0, fill=1)
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 30)
c.drawString(58, LH - 78, "NAKSHA: how it works")
c.setFillColor(MUTED)
c.setFont("Helvetica", 15)
c.drawString(58, LH - 104, "One upload. Three outputs.")
draw_pipeline(c, 74, 150, scale=1.28, big=True)
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 15)
c.drawString(58, 92, "The first output is a purchase order.")
c.drawString(58, 68, "The third one never leaves the house.")
c.save()
print("diagram written")
