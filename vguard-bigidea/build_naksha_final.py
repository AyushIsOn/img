#!/usr/bin/env python3
"""NAKSHA executive summary in the official V-Guard template structure.
Cover page + 'First Page' (<=500 words) + supporting content (<=2000 words)."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                               PageBreak, PageTemplate, Paragraph, Spacer,
                               Table, TableStyle)

INK = colors.black
MUTED = colors.HexColor("#5F5F5F")
RED = colors.HexColor("#FF0000")
ACCENT = colors.HexColor("#1F6E5A")
FILL = colors.HexColor("#EFF1F0")

PW, PH = A4
MG = 22 * mm
CW = PW - 2 * MG


def st(n, **kw):
    b = dict(name=n, fontName="Times-Roman", fontSize=11, leading=14.6,
             textColor=INK, spaceAfter=0)
    b.update(kw)
    return ParagraphStyle(**b)


S = {
    "redhead": st("redhead", fontName="Times-Bold", fontSize=13.5, leading=17,
                  textColor=RED, alignment=TA_CENTER, spaceAfter=14),
    "ital": st("ital", fontName="Times-Italic", fontSize=10.5, leading=14,
               spaceAfter=10),
    "field": st("field", fontName="Times-Bold", fontSize=11, leading=20),
    "h2": st("h2", fontName="Times-Bold", fontSize=12, leading=15,
             spaceBefore=9, spaceAfter=3.5, keepWithNext=1),
    "body": st("body", alignment=TA_JUSTIFY, spaceAfter=5),
    "bul": st("bul", alignment=TA_JUSTIFY, leftIndent=13, bulletIndent=2,
              spaceAfter=4),
    "cap": st("cap", fontName="Times-Italic", fontSize=8.6, leading=11,
              textColor=MUTED, spaceBefore=2, spaceAfter=3),
    "pagelab": st("pagelab", fontName="Times-Bold", fontSize=11,
                  alignment=2, spaceAfter=10),
}


def P(t, s="body"):
    return Paragraph(t, S[s])


def B(t):
    return Paragraph(t, S["bul"], bulletText="\u2022")


# --------------------------------------------------------------- diagram
def draw_pipeline(c, x0, y0, scale=1.0, big=False):
    def sx(v):
        return x0 + v * scale

    def sy(v):
        return y0 + v * scale

    fs = 9.6 if big else 7.4

    def box(bx, by, bw, bh, label, sub=None, fill=None, stroke=INK, tc=None):
        c.saveState()
        c.setStrokeColor(stroke)
        c.setLineWidth(1.1 if big else 0.9)
        if fill is not None:
            c.setFillColor(fill)
            c.roundRect(sx(bx), sy(by), bw * scale, bh * scale, 3 * scale, 1, 1)
        else:
            c.roundRect(sx(bx), sy(by), bw * scale, bh * scale, 3 * scale, 1, 0)
        c.setFillColor(tc or (colors.white if fill == ACCENT else INK))
        c.setFont("Helvetica-Bold", fs)
        cx = sx(bx) + bw * scale / 2
        if sub:
            c.drawCentredString(cx, sy(by) + bh * scale / 2 + 2 * scale, label)
            c.setFont("Helvetica", fs - 1.3)
            c.setFillColor(tc or (colors.white if fill == ACCENT else MUTED))
            c.drawCentredString(cx, sy(by) + bh * scale / 2 - 7 * scale, sub)
        else:
            c.drawCentredString(cx, sy(by) + bh * scale / 2 - fs / 3, label)
        c.restoreState()

    def arrow(a1, ay, a2, colr=INK):
        c.saveState()
        c.setStrokeColor(colr)
        c.setFillColor(colr)
        c.setLineWidth(1.1 if big else 0.9)
        c.line(sx(a1), sy(ay), sx(a2) - 4, sy(ay))
        p = c.beginPath()
        p.moveTo(sx(a2), sy(ay))
        p.lineTo(sx(a2) - 5 * scale, sy(ay) + 2.8 * scale)
        p.lineTo(sx(a2) - 5 * scale, sy(ay) - 2.8 * scale)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()

    def tag(tx, ty, t, colr=MUTED, size=None, font="Helvetica"):
        c.saveState()
        c.setFillColor(colr)
        c.setFont(font, size or fs - 1.2)
        c.drawString(sx(tx), sy(ty), t)
        c.restoreState()

    box(0, 96, 100, 42, "ARCHITECT'S PLAN", "PDF or drawing", fill=FILL)
    arrow(104, 117, 126)
    box(130, 88, 130, 58, "NAKSHA ENGINE", "national wiring codes",
        fill=ACCENT, stroke=ACCENT)
    tag(133, 74, "circuits, board siting, routing")
    for label, sub, oy, note in [
            ("WIRE SCHEDULE", "exact metres, by size", 140, "a purchase order"),
            ("SITE MARKING", "phone AR overlay", 88, "built correctly"),
            ("AS-BUILT RECORD", "permanent wiring map", 36, "lifetime lock-in")]:
        c.saveState()
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.1 if big else 0.9)
        c.line(sx(264), sy(117), sx(282), sy(117))
        c.line(sx(282), sy(117), sx(282), sy(oy + 19))
        c.line(sx(282), sy(oy + 19), sx(300), sy(oy + 19))
        c.restoreState()
        box(300, oy, 152, 38, label, sub, fill=None, stroke=ACCENT, tc=INK)
        tag(462, oy + 16, "\u2192 " + note, ACCENT, font="Helvetica-Bold")


class DiagFlow(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width, self.height = CW, 116

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        draw_pipeline(self.canv, 0, -27, 0.79)


# --------------------------------------------------------------- page 1
BODY = []
A = BODY.append


class TitleBox(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width, self.height = CW, 54

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        bw, bh = 300, 46
        bx = (CW - bw) / 2
        c.setStrokeColor(INK)
        c.setLineWidth(1.1)
        c.rect(bx, 4, bw, bh, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont("Times-Bold", 23)
        txt = "EXECUTIVE SUMMARY"
        c.drawCentredString(CW / 2, 20, txt)
        tw = c.stringWidth(txt, "Times-Bold", 23)
        c.setLineWidth(1.2)
        c.line(CW / 2 - tw / 2, 15, CW / 2 + tw / 2, 15)


A(Spacer(1, 8))
A(TitleBox())
A(Spacer(1, 40))
A(P("V-GUARD INDUSTRIES LTD \u2013 BIG IDEA TECH DESIGN<br/>COMPETITION 2026",
    "redhead"))
A(Spacer(1, 16))
A(P("(The first page of the executive summary must adhere to the format given "
    "below)", "ital"))

rows = [
    [P("<b>Team Name:</b>", "field")],
    [P("<b>Team Members</b> <i>(Format: Full Name \u2013 Year of passing)</i>",
       "field")],
    [P("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1)", "field")],
    [P("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2)", "field")],
    [P("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3)", "field")],
    [Spacer(1, 6)],
    [P("<b>Institute/E-School:</b>", "field")],
    [Spacer(1, 4)],
    [P("<b>Mobile No of Team Lead:</b>", "field")],
    [Spacer(1, 4)],
    [P("<b>E-mail ID of Team Lead:</b>", "field")],
    [Spacer(1, 6)],
    [Table([[P("<b>Number of words:</b> 1,362", "field"),
             P("<b>Date of Submission:</b>", "field")]],
           colWidths=[(CW - 30) * 0.5, (CW - 30) * 0.5])],
    [Spacer(1, 6)],
    [P("<b><u>Google Drive Video Link</u></b>", "field")],
    [P("<b><u>Please paste the google drive link of your team\u2019s video "
       "pitch (40 seconds) below.</u></b>", "field")],
    [Spacer(1, 40)],
]
box = Table(rows, colWidths=[CW])
box.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 1.1, INK),
    ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, -1), 1),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
]))
A(box)
A(PageBreak())

# --------------------------------------------------------- FIRST PAGE (<=500)
A(P("(First Page)", "pagelab"))
A(P("(The first page of the executive summary must adhere to the format given "
    "below and must not exceed 500 words)", "ital"))

A(P("Problem Statement (What &amp; Why)", "h2"))
A(P("Indian homes are wired from memory. The electrician works without a "
    "drawing, improvises conduit routes, and leaves no record behind. Roughly "
    "42% of building fires in India are attributed to electrical short "
    "circuits, a phrase that conceals ageing wiring, overloaded circuits and "
    "substandard material."))
A(P("The rules are not the missing piece. India already publishes codes of "
    "practice for wiring installation and earthing, and current regulations "
    "already require installation work to be done by a licensed contractor. "
    "<b>What is missing is any tool that turns those rules into a drawing "
    "someone on an Indian residential site will actually use.</b> Because there "
    "is no drawing, there is also no record, which is why households drill into "
    "live cables and why renovation becomes guesswork."))
A(P("For V-Guard the commercial problem is adjacent. Wire is the most "
    "commoditised product it sells, competing on price, brand recall and "
    "whatever the electrician happens to be carrying."))

A(P("Brief Description of the Idea/Solution", "h2"))
A(P("<b>NAKSHA changes what is being sold: not a coil of wire, but a designed "
    "electrical installation that specifies V-Guard wire.</b> An owner, "
    "contractor or electrician uploads the architect's floor plan and answers a "
    "few questions about appliances. NAKSHA returns a complete residential "
    "electrical design, generated against the national wiring and earthing "
    "codes: circuit split, distribution board siting, conduit routing and point "
    "placement."))
A(Spacer(1, 2))
A(KeepTogether([DiagFlow(),
                P("One upload, three outputs. The first is effectively a "
                  "purchase order, the second gets the job built correctly, "
                  "and the third never leaves the house.", "cap")]))

A(P("Technology Proposed", "h2"))
A(P("<b>Plan understanding:</b> the uploaded plan is vectorised and segmented "
    "into rooms, walls and openings, with room type inferred from dimensions and "
    "adjacency and confirmed by the user. <b>Rule engine:</b> the wiring and "
    "earthing codes are encoded as explicit, auditable constraints covering "
    "circuit separation, dedicated ways for heavy loads, points per circuit, "
    "earthing and diversity factors. This layer is deterministic and "
    "inspectable, not a language model guessing at safety rules. <b>Layout "
    "optimisation</b> is the core computational problem: place the distribution "
    "board and route conduits to minimise total wire length and voltage drop, "
    "subject to the rule set and to buildable chase geometry, solved as a graph "
    "problem over room adjacency. <b>Bill of quantities</b> converts the design "
    "into wire length per size with waste allowance, plus conduit, boxes and "
    "switchgear, mapped onto V-Guard SKUs. <b>Site delivery</b> uses a phone "
    "based AR overlay, which needs no equipment on site. <b>As-built capture</b> "
    "has the electrician confirm each run before plastering, producing the "
    "permanent record."))
A(PageBreak())

# ------------------------------------------------- SUPPORTING (<=2000 words)
A(P("(From the second page: remaining content that supports and justifies the "
    "Executive Summary)", "ital"))

A(P("Novelty and Innovation", "h2"))
A(P("The components are not new, and this proposal is stronger for saying so. "
    "Automated electrical takeoff is a mature commercial category. Tools such "
    "as drawer.ai already accept PDF drawings and return quantities and wire "
    "lengths with marked-up routing, and Kreo, Trimble Accubid and PlanSwift "
    "serve the same market. Work presented at ISARC 2026 automates outlet to "
    "circuit and circuit to panelboard assignment in a CAD and BIM workflow. "
    "Robotic site layout is also solved: Dusty Robotics has printed coordinated "
    "models onto more than 300 million square feet of slab."))
A(P("All of that serves Western commercial contractors bidding large projects. "
    "Our contribution is therefore positional rather than algorithmic:"))
A(B("<b>Indian codes as the rule set.</b> None of the existing tools encode "
    "them."))
A(B("<b>Residential scale, where no drawing exists today</b>, rather than "
    "commercial scale where one already does."))
A(B("<b>The as-built record</b>, which no takeoff tool produces, because its "
    "users leave the site and never return."))
A(B("<b>Distribution through a channel V-Guard already owns.</b> This is the "
    "finding that convinced us, and it is set out below."))

A(P("The channel insight", "h2"))
A(P("Every major Indian wire brand has already digitised its electrician "
    "relationship. RR Kabel has RR Connect, Finolex has Samruddhi, Havells has "
    "an electrician app, and Polycab's Experts platform reaches around 2.5 lakh "
    "electricians and retailers, which the company describes in its FY26 annual "
    "report as a grassroots influencer channel."))
A(P("<b>Every one of them is a loyalty scheme. Scan a code, collect points, "
    "redeem a gift.</b> The distribution channel is already built, the "
    "electricians are already on smartphones, and no brand has put a tool in "
    "that channel that does any actual work. An electrician does not want "
    "points. He wants the load calculation done, the wire sizes decided, the "
    "material list totalled, and a defensible answer when the owner asks why it "
    "costs what it costs."))

A(P("End Consumer and Business Value", "h2"))
A(P("<b>For the consumer:</b> a home wired to code rather than to habit, an "
    "itemised material list that makes overcharging visible, and a permanent map "
    "of where every cable runs, which is what makes future renovation and fault "
    "finding safe instead of speculative."))
A(P("<b>For V-Guard,</b> four things:"))
A(B("<b>Every design is a purchase order</b>, because the output is a wire "
    "schedule in metres by size. Specifying the material is a stronger position "
    "than advertising to whoever walks into a shop. This is the Asian Paints "
    "move, which used Beautiful Homes services to escape commodity paint "
    "competition, and which Berger followed with Express Painting."))
A(B("<b>It captures the decision years earlier.</b> Wiring is specified during "
    "construction, before the owner has any brand opinion, and it is never "
    "re-shopped. You cannot rewire a finished house."))
A(B("<b>It opens a portfolio funnel.</b> The same plan positions the water "
    "heater, chimney, RO and gas point. All are V-Guard categories, all decided "
    "at construction stage, and all currently decided by whoever happens to be "
    "standing there."))
A(B("<b>It is a margin story, not a volume story.</b> FY25-26 revenue grew 7.0% "
    "to Rs 5,966 crore while PAT fell 1.7% to Rs 308 crore. Commodity wire "
    "cannot fix that; specified systems can."))

A(P("On scale, and how the marking is delivered", "h2"))
A(P("A national service business is genuinely hard: staffing, training, "
    "equipment and quality control. We do not propose one. The design engine "
    "scales at software cost, and only the physical marking needs people, so the "
    "two are separated deliberately into three tiers."))
A(B("<b>Tier 1, the app.</b> Free, all-India, phone AR marking, no hardware, "
    "infinitely scalable. This tier carries the strategy, because this is where "
    "the wire schedules come from."))
A(B("<b>Tier 2, assisted.</b> A trained V-Guard marking partner in metro "
    "cities, offered as a paid service."))
A(B("<b>Tier 3, flagship.</b> Robotic or laser layout, deployed as a showcase. "
    "Treating it as a marketing instrument rather than a P&amp;L line is the "
    "honest position, and it is exactly how paint companies launched their "
    "service brands."))

A(P("Risks and honest limitations", "h2"))
A(B("<b>Plan quality is the hard input problem.</b> Indian residential plans "
    "are often scanned, hand marked, incomplete or dimensionally unreliable. The "
    "engine must degrade gracefully to guided manual tracing, and the first "
    "release should assume human confirmation of every inferred room."))
A(B("<b>Liability.</b> Because a licensed contractor is legally responsible for "
    "the installation, the tool must be positioned as a decision aid he signs "
    "off, not as designer of record. This needs legal structuring before "
    "launch."))
A(B("<b>AR marking accuracy on a live site is unproven</b> at the tolerance "
    "conduit chasing needs, so Tier 1 should promise dimensioned guidance and "
    "reference marks rather than millimetre placement."))
A(B("<b>Adoption is the real risk, not the technology.</b> Experienced "
    "electricians may read the tool as a challenge to their judgment. It must "
    "visibly save them time on load calculation and estimating on day one, or it "
    "will be ignored."))

A(P("What we would build next", "h2"))
A(B("A working layout generator on real Indian floor plans: rooms in, circuits "
    "and routed conduits out, with every decision traceable to a rule."))
A(B("An optimisation study of total wire length and voltage drop against "
    "distribution board placement across several house typologies, quantifying "
    "the material saving a good layout produces over an improvised one."))
A(B("A browser demo that generates and visualises a design from an uploaded "
    "plan, with a costed bill of quantities."))
A(B("An AR feasibility test on a real wall, reporting measured registration "
    "error honestly rather than asserting it."))


def footer(cv, doc):
    cv.saveState()
    cv.setFont("Times-Roman", 9)
    cv.setFillColor(MUTED)
    if doc.page > 1:
        cv.drawCentredString(PW / 2, 12 * mm, "%d" % doc.page)
    cv.restoreState()


doc = BaseDocTemplate("NAKSHA-Executive-Summary.pdf", pagesize=A4,
                      leftMargin=MG, rightMargin=MG, topMargin=MG,
                      bottomMargin=18 * mm, title="NAKSHA Executive Summary",
                      author="V-Guard Big Idea Tech Design Competition 2026")
doc.addPageTemplates([PageTemplate(id="m", frames=[
    Frame(MG, 18 * mm, CW, PH - MG - 18 * mm, id="b")], onPage=footer)])
doc.build(BODY)
print("summary written")

# ---------------------------------------------------- standalone video diagram
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
draw_pipeline(c, 74, 150, 1.28, True)
c.setFillColor(INK)
c.setFont("Helvetica-Bold", 15)
c.drawString(58, 92, "The first output is a purchase order.")
c.drawString(58, 68, "The third one never leaves the house.")
c.save()
print("diagram written")
