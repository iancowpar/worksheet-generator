"""Convert a cover letter markdown file into a .docx (and matching .pdf).

Usage:
    python3 applications/build_cover_docx.py applications/hungryroot/CoverLetter_Hungryroot_IanCowpar.md
    python3 applications/build_cover_docx.py applications/   # processes every CoverLetter_*.md and Note_*.md

Cover letter markdown format (see existing files for examples):

    **Ian Cowpar**

    ian.cowpar@gmail.com  |  351-235-0365  |  linkedin.com/in/ian-cowpar

    May 2026

    Hi [Hiring Manager],         (or "Hiring Team, Company")

    Paragraph 1...

    Paragraph 2...

    Ian Cowpar                   (signature: last line, just a name)
"""

import re
import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches


def parse_cover_md(text):
    lines = [ln.rstrip() for ln in text.split("\n")]
    out = {"name": "", "contact": "", "date": "", "salutation": "", "paragraphs": [], "signature": ""}

    # Strip blank lines for grouping
    blocks = []
    current = []
    for ln in lines:
        if ln.strip() == "":
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(ln)
    if current:
        blocks.append("\n".join(current))

    if not blocks:
        return out

    # First block: name (likely "**Ian Cowpar**")
    out["name"] = blocks[0].strip("*").strip()
    # Second block: contact line
    out["contact"] = blocks[1] if len(blocks) > 1 else ""
    # Third block: date
    out["date"] = blocks[2] if len(blocks) > 2 else ""
    # Fourth block: salutation
    out["salutation"] = blocks[3] if len(blocks) > 3 else ""

    # Last block is the signature (single short line, just a name)
    if len(blocks) > 4:
        last = blocks[-1].strip()
        if len(last) < 50 and "\n" not in last:
            out["signature"] = last
            body_blocks = blocks[4:-1]
        else:
            body_blocks = blocks[4:]
    else:
        body_blocks = []

    out["paragraphs"] = body_blocks
    return out


def add_run_with_inline_italic(p, text, base_font="Calibri"):
    """Render a string, converting *italic markers* to italic runs."""
    parts = re.split(r"(\*[^*]+\*)", text)
    for part in parts:
        if not part:
            continue
        italic = part.startswith("*") and part.endswith("*")
        content = part.strip("*") if italic else part
        r = p.add_run(content)
        r.italic = italic
        r.font.name = base_font


def build_cover_docx(parsed, output_path):
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    def add_run(p, text, bold=False, italic=False, size=None):
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.name = "Calibri"
        if size:
            r.font.size = Pt(size)
        return r

    # Name
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    add_run(p, parsed["name"], bold=True, size=16)

    # Contact
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(14)
    add_run(p, parsed["contact"])

    # Date
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(14)
    add_run(p, parsed["date"])

    # Salutation
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(12)
    add_run(p, parsed["salutation"])

    # Body paragraphs
    for para in parsed["paragraphs"]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = 1.15
        add_run_with_inline_italic(p, para)

    # Signature
    if parsed["signature"]:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        add_run(p, parsed["signature"])

    doc.save(output_path)
    return output_path


def build_from_md(md_path):
    md_path = Path(md_path)
    text = md_path.read_text()
    parsed = parse_cover_md(text)
    output_path = md_path.with_suffix(".docx")
    build_cover_docx(parsed, str(output_path))
    return output_path


def looks_like_cover(path):
    name = path.name
    return name.startswith("CoverLetter") or name.startswith("Note_")


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    if target.is_file() and target.suffix == ".md":
        out = build_from_md(target)
        print(f"Saved: {out}")
    elif target.is_dir():
        for md_file in target.rglob("*.md"):
            if looks_like_cover(md_file):
                out = build_from_md(md_file)
                print(f"Saved: {out}")
    else:
        print(f"Don't know how to handle: {target}")
        sys.exit(1)
