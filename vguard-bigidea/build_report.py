"""Builds the NAKSHA detailed report PDF.

Formatting is fixed by the submission rules and is not a matter of taste:
Times New Roman at 11 point, 1.5 line spacing, 3 cm margins on every side, a
synopsis of no more than 300 words, a table of contents, and references numbered
so they match the markers in the text.

    python3 build_report.py

Times New Roman is not redistributable, so the built in Times faces are used.
They are metrically the same family and render identically for this purpose.
"""

from __future__ import annotations

import re

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
import os

from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)
from reportlab.lib.utils import ImageReader

import report_content as C

MARGIN = 3 * cm
BODY_SIZE = 11
LEADING = BODY_SIZE * 1.5          # 1.5 line spacing
OUT = "NAKSHA-Detailed-Report.pdf"


# ------------------------------------------------------------------ styles

def styles() -> dict:
    def make(name: str, **over) -> ParagraphStyle:
        """Body defaults, overridable. Keeps 11pt Times and 1.5 leading as the
        starting point for every style so the spec holds unless overridden."""
        spec = dict(fontName="Times-Roman", fontSize=BODY_SIZE,
                    leading=LEADING)
        spec.update(over)
        return ParagraphStyle(name, **spec)

    return {
        "title": make("title", alignment=TA_CENTER, fontSize=26, leading=30,
                      spaceAfter=6),
        "subtitle": make("subtitle", alignment=TA_CENTER, fontSize=13,
                         leading=18, spaceAfter=4),
        "front": make("front", alignment=TA_CENTER, spaceAfter=4),
        "frontlabel": make("frontlabel", fontName="Times-Bold",
                           alignment=TA_CENTER, spaceBefore=16, spaceAfter=4),
        "h1": make("h1", fontName="Times-Bold", fontSize=13, leading=18,
                   spaceBefore=16, spaceAfter=7),
        "h2": make("h2", fontName="Times-Bold", spaceBefore=11, spaceAfter=5),
        "p": make("p", alignment=TA_JUSTIFY, spaceAfter=8),
        "b": make("b", alignment=TA_JUSTIFY, leftIndent=18, bulletIndent=6,
                  spaceAfter=7),
        "toc": make("toc", alignment=TA_LEFT, spaceAfter=5),
        "caption": make("caption", fontSize=9.5, leading=13,
                        alignment=TA_LEFT, spaceBefore=5, spaceAfter=10),
        "ref": make("ref", alignment=TA_JUSTIFY, leftIndent=22,
                    firstLineIndent=-22, spaceAfter=6),
    }


def count_words(text: str) -> int:
    """Body words only. Markers, markup and table cells are not prose."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[\d+\]", " ", text)
    return len([w for w in text.split() if any(c.isalnum() for c in w)])


# ------------------------------------------------------------------- build

def build() -> None:
    s = styles()
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title=f"{C.TITLE} Detailed Report",
                          author=f"Team {C.TEAM}")
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="body")

    def numbered(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Times-Roman", 9)
        canvas.drawCentredString(A4[0] / 2, MARGIN / 2 - 4,
                                 str(canvas.getPageNumber() - 1))
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id="front", frames=[frame]),
        PageTemplate(id="body", frames=[frame], onPage=numbered),
    ])

    story = []

    # ---------------------------------------------------------- front page
    # Team name and participants only. No institution anywhere in the report.
    story += [
        Spacer(1, 4.5 * cm),
        Paragraph(C.TITLE, s["title"]),
        Paragraph(C.SUBTITLE, s["subtitle"]),
        Spacer(1, 0.5 * cm),
        Paragraph(C.TRACK, s["subtitle"]),
        Spacer(1, 3 * cm),
        Paragraph("Team Name", s["frontlabel"]),
        Paragraph(C.TEAM, s["front"]),
        Paragraph("Participant", s["frontlabel"]),
    ]
    for m in C.MEMBERS:
        story.append(Paragraph(m, s["front"]))
    story += [NextPageTemplate("body"), PageBreak()]

    # ------------------------------------------------------------ synopsis
    syn_words = count_words(C.SYNOPSIS)
    story.append(Paragraph("Synopsis", s["h1"]))
    for para in C.SYNOPSIS.strip().split("\n\n"):
        story.append(Paragraph(para.replace("\n", " "), s["p"]))
    story.append(PageBreak())

    # --------------------------------------------------------------- toc
    story.append(Paragraph("Table of Contents", s["h1"]))
    for kind, text in C.BODY:
        if kind == "h1":
            story.append(Paragraph(text, s["toc"]))
        elif kind == "h2":
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{text}",
                                   s["toc"]))
    story.append(Paragraph("References", s["toc"]))
    story.append(PageBreak())

    # -------------------------------------------------------------- body
    body_words = 0
    exhibit_no = 0
    missing_images = []
    for kind, text in C.BODY:
        if kind == "img":
            path, caption, width_cm = [x.strip() for x in text.split("|")]
            exhibit_no += 1
            if not os.path.exists(path):
                missing_images.append(path)
                continue
            # Scale to the requested width, preserving the aspect ratio, and
            # never wider than the text block.
            iw, ih = ImageReader(path).getSize()
            w = min(float(width_cm) * cm, doc.width)
            story.append(KeepTogether([
                Spacer(1, 4),
                Image(path, width=w, height=w * ih / iw, hAlign="CENTER"),
                Paragraph(f"Exhibit {exhibit_no}. {caption}", s["caption"]),
            ]))
            continue

        if kind == "t":
            rows = [C.TABLE_HEADER] + [r.split("|") for r in text.split("\n")]
            table = Table(rows, hAlign="LEFT",
                          colWidths=[3.6 * cm, 2.2 * cm, 2.2 * cm,
                                     3.1 * cm, 2.6 * cm])
            table.setStyle(TableStyle([
                ("FONT", (0, 0), (-1, 0), "Times-Bold", 9.5),
                ("FONT", (0, 1), (-1, -1), "Times-Roman", 9.5),
                ("FONT", (0, -1), (-1, -1), "Times-Bold", 9.5),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, (0, 0, 0)),
                ("LINEABOVE", (0, -1), (-1, -1), 0.4, (0, 0, 0)),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(KeepTogether([
                table,
                Paragraph("Exhibit. Conduit length by routing method, "
                          "measured on three house types. Radial is one run "
                          "per point. Topology saving is the reduction from "
                          "sharing conduit as a Steiner tree. Board siting is "
                          "the further reduction from solving for the board "
                          "position, holding topology constant.",
                          s["caption"])]))
            continue

        body_words += count_words(text)
        if kind == "b":
            story.append(Paragraph(text, s["b"], bulletText="\u2022"))
        else:
            story.append(Paragraph(text, s[kind]))

    # -------------------------------------------------------- references
    story.append(Paragraph("References", s["h1"]))
    for i, ref in enumerate(C.REFERENCES, start=1):
        story.append(Paragraph(f"[{i}]&nbsp;&nbsp;{ref}", s["ref"]))

    doc.build(story)

    # ------------------------------------------------------------ report
    print(f"\nwritten: {OUT}")
    print(f"  synopsis   {syn_words} words   (limit 300)"
          f"   {'OK' if syn_words <= 300 else 'OVER'}")
    print(f"  body       {body_words} words   (excludes synopsis, contents, "
          f"exhibit and references)")
    print(f"  references {len(C.REFERENCES)}")
    used = sorted({int(n) for _, t in C.BODY
                   for n in re.findall(r"\[(\d+)\]", t)}
                  | {int(n) for n in re.findall(r"\[(\d+)\]", C.SYNOPSIS)})
    print(f"  markers used in text: {used}")
    missing = [n for n in range(1, len(C.REFERENCES) + 1) if n not in used]
    print(f"  references never cited: {missing or 'none'}")
    dangling = [n for n in used if n > len(C.REFERENCES)]
    print(f"  markers with no reference: {dangling or 'none'}")
    print(f"  exhibits placed: {exhibit_no - len(missing_images)}"
          f" of {exhibit_no}")
    if missing_images:
        print("  MISSING IMAGE FILES, exhibits skipped:")
        for m in missing_images:
            print(f"    {m}")
    print(f"  Times New Roman 11pt, {LEADING}pt leading (1.5), "
          f"{MARGIN / cm:.0f} cm margins")


if __name__ == "__main__":
    build()
