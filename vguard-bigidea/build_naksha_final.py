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

    box(0, 96, 100, 42, "FLOOR PLAN", "from the architect", fill=FILL)
    arrow(104, 117, 126)
    box(130, 88, 130, 58, "NAKSHA AR APP", "wiring, water, gas, duct",
        fill=ACCENT, stroke=ACCENT)
    tag(131, 74, "walk the house, place the runs")
    for label, sub, oy, note in [
            ("MATERIAL SCHEDULE", "wire and pipe, in metres", 140,
             "a V-Guard order"),
            ("CONTRACTOR MAP", "simple, buildable drawing", 88,
             "built correctly"),
            ("AS-BUILT RECORD", "permanent utility map", 36,
             "lifetime lock-in")]:
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
        self.width, self.height = CW, 99

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        draw_pipeline(self.canv, 0, -24, 0.67)


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
    [P("<b>Team Name:</b>&nbsp;&nbsp;D38N", "field")],
    [P("<b>Team Members</b> <i>(Format: Full Name \u2013 Year of passing)</i>",
       "field")],
    [P("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1)&nbsp;&nbsp;Ayush Gupta \u2013 2027", "field")],
    [P("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2)", "field")],
    [P("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3)", "field")],
    [Spacer(1, 6)],
    [P("<b>Institute/E-School:</b>&nbsp;&nbsp;Manipal University", "field")],
    [Spacer(1, 4)],
    [P("<b>Mobile No of Team Lead:</b>&nbsp;&nbsp;8318010062", "field")],
    [Spacer(1, 4)],
    [P("<b>E-mail ID of Team Lead:</b>&nbsp;&nbsp;ayushgupta.2406@gmail.com", "field")],
    [Spacer(1, 6)],
    [Table([[P("<b>Number of words:</b> 1,431", "field"),
             P("<b>Date of Submission:</b>&nbsp;&nbsp;12 August 2026", "field")]],
           colWidths=[(CW - 30) * 0.5, (CW - 30) * 0.5])],
    [Spacer(1, 6)],
    [P("<b><u>Google Drive Video Link</u></b>", "field")],
    [P("<b><u>Please paste the google drive link of your team\u2019s video "
       "pitch (40 seconds) below.</u></b>", "field")],
    [Paragraph("https://drive.google.com/file/d/"
               "1eBcNDpe4yKDJRv7YKbVwHbuWcS2VZ9WY/view?usp=sharing",
               ParagraphStyle(name="link", fontName="Times-Roman",
                              fontSize=9.5, leading=13,
                              textColor=colors.HexColor("#0645AD")))],
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
A(P("When a family builds a house, they do not know where anything needs to go. "
    "The wiring, the water pipes, the gas line, the chimney duct. Even with the "
    "architect\u2019s drawings it stays confusing, because a flat plan cannot tell "
    "you how a room will feel, or where you will actually want a socket, a geyser "
    "or a chimney."))
A(P("So these decisions get made on site, quickly, by whoever happens to be "
    "there. Runs are improvised, material is mis-ordered, and nothing is written "
    "down. Roughly 42% of building fires in India are attributed to electrical "
    "short circuits, and with no record, later renovation becomes guesswork."))
A(P("<b>For V-Guard, that same moment is a missed commercial opportunity.</b> "
    "Every one of those decisions settles which brand of wire, water heater, "
    "chimney, RO unit and gas stove ends up in the house. V-Guard sells all of "
    "them, and is present for none of it."))

A(P("Brief Description of the Idea/Solution", "h2"))
A(P("<b>NAKSHA is an augmented reality app from V-Guard.</b> The owner walks "
    "through the under-construction house holding a phone and places what they "
    "want where they want it: sockets and switches, the water heater, the water "
    "line, the gas point, the chimney duct. They see it at full scale on the "
    "actual wall, before anything is chased or plastered."))
A(Spacer(1, 2))
A(KeepTogether([DiagFlow(),
                P("The owner designs in AR. The app produces a material "
                  "order, a drawing the trades can build from, and a permanent "
                  "record.", "cap")]))
A(P("<b>The app is a marketing instrument as much as a design tool.</b> At the "
    "exact moment the owner is deciding where the water heater goes, V-Guard is "
    "the brand in their hand, showing the V-Guard model that fits the space. "
    "The app is free. What it sells is wire, water heaters, chimneys, RO systems "
    "and gas stoves. V-Guard offers it as a service, and the service sells the "
    "products."))

A(P("Technology Proposed", "h2"))
A(P("<b>Augmented reality layer:</b> ARCore and ARKit plane detection with "
    "world tracking, so placed runs and appliances stay fixed to the wall as the "
    "user moves. Phone based, nothing to carry on site. <b>Plan "
    "understanding:</b> an architect\u2019s plan can optionally be uploaded and "
    "segmented into rooms to give real dimensions. <b>Rule engine:</b> the "
    "national wiring and earthing codes encoded as explicit, auditable "
    "constraints, so what the owner draws is corrected to code rather than merely "
    "recorded. <b>Routing and estimation:</b> runs are routed to minimise length "
    "and voltage drop, then converted into wire by size, pipe and duct lengths, "
    "boxes and switchgear, mapped onto V-Guard product codes. <b>Output for "
    "trades:</b> a dimensioned drawing, because a contractor will not use an app. "
    "<b>As-built capture:</b> each run is confirmed before plastering."))
A(PageBreak())

A(P("(From the second page: remaining content that supports and justifies the "
    "Executive Summary)", "ital"))

A(P("Why V-Guard, and not a startup", "h2"))
A(P("This is the argument the whole proposal rests on. An independent app that "
    "helps you plan your home services has no way to make money except by "
    "charging for the software, which nobody in this market will pay for."))
A(P("<b>V-Guard sells products in every category the app touches:</b> wires and "
    "cables, water heaters, chimneys, RO purifiers and gas stoves. That makes "
    "the app a sales channel rather than a product. It can be given away free, "
    "forever, because the revenue is downstream. <b>No competitor spans all four "
    "utilities, so no competitor can afford to give this away.</b>"))

A(P("Novelty and Innovation", "h2"))
A(P("The components exist and the proposal is stronger for saying so. Automated "
    "electrical takeoff is a mature category: tools such as drawer.ai accept PDF "
    "drawings and return quantities and wire lengths with marked-up routing, and "
    "Kreo, Trimble Accubid and PlanSwift serve the same market. Work presented at "
    "ISARC 2026 automates circuit assignment in a CAD and BIM workflow. Robotic "
    "site layout is solved too, with Dusty Robotics having printed coordinated "
    "models onto over 300 million square feet of slab."))
A(P("All of it serves Western commercial contractors bidding large projects. Our "
    "contribution is positional:"))
A(B("<b>The home owner is the user</b>, not an estimator. Existing tools ask for "
    "a finished design; NAKSHA lets a non-technical person create one by walking "
    "around and pointing."))
A(B("<b>All four utilities in one pass</b>, which mirrors how a house is "
    "actually built and which only V-Guard\u2019s portfolio can monetise."))
A(B("<b>Indian codes as the rule set.</b> None of the existing tools encode "
    "them."))
A(B("<b>The as-built record</b>, which no takeoff tool produces, because its "
    "users leave the site and never return."))

A(P("The channel is already built", "h2"))
A(P("Every major Indian wire brand has already digitised its electrician "
    "relationship. RR Kabel has RR Connect, Finolex has Samruddhi, Havells has "
    "an electrician app, and Polycab\u2019s Experts platform reaches around 2.5 "
    "lakh electricians and retailers, described in its FY26 annual report as a "
    "grassroots influencer channel."))
A(P("<b>Every one of them is a loyalty scheme. Scan a code, collect points, "
    "redeem a gift. Nobody has put a tool in that channel that does any actual "
    "work.</b> The electrician does not want points. He wants the load "
    "calculation done, the sizes decided, the material list totalled, and a "
    "defensible answer when the owner asks why it costs what it costs. Give him "
    "that, and he becomes the distribution."))

A(P("End Consumer and Business Value", "h2"))
A(P("<b>For the owner:</b> the ability to see and decide the house before it is "
    "sealed, an itemised material list that makes overcharging visible, a home "
    "wired to code rather than to habit, and a permanent map of every service "
    "run in the building."))
A(P("<b>For V-Guard,</b> four things:"))
A(B("<b>It is a marketing channel that sells at the moment of decision.</b> "
    "Every appliance the owner places in AR is a V-Guard product shown in their "
    "own room, at the point where the choice is actually made."))
A(B("<b>Every design becomes an order.</b> The output is a material schedule in "
    "metres and units, mapped to V-Guard codes. Specifying material is a stronger "
    "position than advertising to whoever walks into a shop. This is the Asian "
    "Paints move, which used Beautiful Homes services to escape commodity paint "
    "competition, and which Berger followed with Express Painting."))
A(B("<b>It captures the decision years earlier.</b> Services are specified "
    "during construction, before the owner has any brand opinion, and they are "
    "never re-shopped. You cannot rewire or re-plumb a finished house."))
A(B("<b>It is a margin story, not a volume story.</b> FY25-26 revenue grew 7.0% "
    "to Rs 5,966 crore while PAT fell 1.7% to Rs 308 crore. Commodity wire "
    "cannot fix that; specified systems can."))

A(P("Delivery and scale", "h2"))
A(P("The app scales at software cost and needs no field organisation, which is "
    "the whole point of choosing AR over any equipment-based approach. Optional "
    "paid layers sit on top: a trained V-Guard marking partner in metro cities, "
    "and a robotic layout flagship deployed as a showcase. Treating the flagship "
    "as a marketing instrument rather than a revenue line is the honest position, "
    "and it is exactly how paint companies launched their service brands."))

A(P("Risks and honest limitations", "h2"))
A(B("<b>AR accuracy on a live site is the technical risk.</b> Drift and poor "
    "lighting are real, so the app should promise dimensioned guidance and "
    "reference marks rather than millimetre placement, and always emit a "
    "measured drawing as the authoritative output."))
A(B("<b>A contractor will not use an app.</b> This is why the deliverable to "
    "the trades is a printed drawing and a material list, not a phone screen."))
A(B("<b>Liability.</b> A licensed contractor is legally responsible for the "
    "installation, so the tool must be a decision aid he signs off, not the "
    "designer of record. This needs legal structuring before launch."))
A(B("<b>Adoption, not technology, is the real risk.</b> The app must visibly "
    "save time on load calculation and estimating from day one, or it will be "
    "ignored by the trades who decide what gets bought."))

A(P("What we would build next", "h2"))
A(B("A working AR prototype on a phone: place sockets, a water heater and a pipe "
    "run in a real room, and export a dimensioned drawing plus a material list."))
A(B("The code rule engine, with every generated decision traceable to a "
    "clause."))
A(B("An optimisation study of material length against distribution board "
    "placement across several house typologies, quantifying the saving a good "
    "layout produces over an improvised one."))
A(B("An AR registration test on a real wall, reporting measured error honestly "
    "rather than asserting it."))


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
c.drawString(58, 92, "The first output is a V-Guard order.")
c.drawString(58, 68, "The third one never leaves the house.")
c.save()
print("diagram written")
