"""Builds the NAKSHA detailed report as an editable .docx.

    python3 build_docx.py

Formatting is fixed by the submission rules, not by preference: Times New Roman
11 point, 1.5 line spacing, 3 cm margins on all four sides, a synopsis under 300
words, a table of contents, and references numbered to match the markers in the
text. All of it is applied as real Word styles, so the document stays editable
and the formatting survives editing.

The front page carries the team name and participant names only. No institution
appears anywhere in the document, as required.
"""

from __future__ import annotations

import os
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

import report_content as C

OUT = "NAKSHA-Detailed-Report.docx"
FONT = "Times New Roman"
SIZE = Pt(11)


# ------------------------------------------------------------------ helpers

def set_margins(section) -> None:
    section.top_margin = Cm(3)
    section.bottom_margin = Cm(3)
    section.left_margin = Cm(3)
    section.right_margin = Cm(3)


def style_base(doc: Document) -> None:
    """Set the document default so anything typed later inherits it too."""
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = SIZE
    # East Asian and complex script names must be set separately or Word
    # substitutes a different face for some characters.
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), FONT)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(6)


def para(doc: Document, text: str = "", *, size=None, bold=False,
         align=None, italic=False, space_before=None, space_after=None,
         spacing=WD_LINE_SPACING.ONE_POINT_FIVE, style=None):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing_rule = spacing
    if space_before is not None:
        pf.space_before = space_before
    if space_after is not None:
        pf.space_after = space_after
    if text:
        run = p.add_run(text)
        run.font.name = FONT
        run.font.size = size or SIZE
        run.bold = bold
        run.italic = italic
    return p


def count_words(text: str) -> int:
    text = re.sub(r"\[\d+\]", " ", text)
    return len([w for w in text.split() if any(c.isalnum() for c in w)])


# -------------------------------------------------------------------- build

def build() -> None:
    doc = Document()
    style_base(doc)
    set_margins(doc.sections[0])

    # ---------------------------------------------------------- front page
    # Team name and participants only. Deliberately no institution field.
    for _ in range(6):
        para(doc)
    para(doc, C.TITLE, size=Pt(28), bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(4))
    para(doc, C.SUBTITLE, size=Pt(13), align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=Pt(18))
    para(doc, C.TRACK, size=Pt(12), italic=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(48))

    para(doc, "Team Name", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=Pt(2))
    para(doc, C.TEAM, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(20))
    para(doc, "Participants", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=Pt(2))
    for m in C.MEMBERS:
        para(doc, m, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(2))

    doc.add_page_break()

    # ------------------------------------------------------------ synopsis
    syn = C.SYNOPSIS.strip().split("\n\n")
    syn_words = count_words(C.SYNOPSIS)
    para(doc, "Synopsis", size=Pt(14), bold=True, space_after=Pt(8))
    for block in syn:
        para(doc, block.replace("\n", " "),
             align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(8))
    doc.add_page_break()

    # ----------------------------------------------------------------- toc
    para(doc, "Table of Contents", size=Pt(14), bold=True, space_after=Pt(8))
    for kind, text in C.BODY:
        if kind == "h1":
            para(doc, text, space_after=Pt(3))
        elif kind == "h2":
            p = para(doc, text, space_after=Pt(3))
            p.paragraph_format.left_indent = Cm(0.8)
    para(doc, "References", space_after=Pt(3))
    doc.add_page_break()

    # ---------------------------------------------------------------- body
    body_words = 0
    exhibit = 0
    missing = []
    for kind, text in C.BODY:
        if kind == "h1":
            para(doc, text, size=Pt(14), bold=True,
                 space_before=Pt(14), space_after=Pt(7))
        elif kind == "h2":
            para(doc, text, bold=True, space_before=Pt(10),
                 space_after=Pt(5))
            body_words += count_words(text)
        elif kind == "b":
            p = doc.add_paragraph(style="List Bullet")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing_rule = \
                WD_LINE_SPACING.ONE_POINT_FIVE
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(text)
            run.font.name = FONT
            run.font.size = SIZE
            body_words += count_words(text)
        elif kind == "img":
            path, caption, width_cm = [x.strip() for x in text.split("|")]
            exhibit += 1
            if not os.path.exists(path):
                missing.append(path)
                continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(path, width=Cm(float(width_cm)))
            cap = para(doc, f"Exhibit {exhibit}. {caption}", size=Pt(9.5),
                       italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                       spacing=WD_LINE_SPACING.SINGLE, space_after=Pt(12))
            for r in cap.runs:
                r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        else:
            para(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                 space_after=Pt(8))
            body_words += count_words(text)

    # ---------------------------------------------------------- references
    para(doc, "References", size=Pt(14), bold=True,
         space_before=Pt(16), space_after=Pt(8))
    for i, ref in enumerate(C.REFERENCES, start=1):
        p = para(doc, f"[{i}]  {ref}", align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                 space_after=Pt(5))
        p.paragraph_format.left_indent = Cm(0.9)
        p.paragraph_format.first_line_indent = Cm(-0.9)

    # ------------------------------------------------------- page numbers
    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    run.font.name = FONT
    run.font.size = Pt(9)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.append(fld)

    doc.save(OUT)

    print(f"\nwritten: {OUT}")
    print(f"  synopsis   {syn_words} words (limit 300) "
          f"{'OK' if syn_words <= 300 else 'OVER'}")
    print(f"  body       {body_words} words")
    print(f"  references {len(C.REFERENCES)}")
    print(f"  exhibits   {exhibit - len(missing)} of {exhibit} placed")
    for m in missing:
        print(f"    MISSING {m}")
    print(f"  {FONT} 11pt, 1.5 line spacing, 3 cm margins on all sides")
    print("  front page: team name and participants only, no institution")


if __name__ == "__main__":
    build()
