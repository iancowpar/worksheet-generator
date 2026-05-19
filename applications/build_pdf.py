"""Convert resume markdown to PDF using reportlab.

Usage:
    python3 applications/build_pdf.py applications/aha/Ian_Cowpar_Resume_Aha.md
    python3 applications/build_pdf.py applications/   # builds every *.md in subdirs

Mirrors build_docx.py output (Helvetica 10.5pt, 0.6/0.75in margins, ATS-friendly).
"""

import re
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

sys.path.insert(0, str(Path(__file__).parent))
from build_docx import parse_resume_md  # noqa: E402


def esc(s):
    """Escape & < > for reportlab Paragraph HTML-ish parser."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_pdf(parsed, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    base = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=10.5,
        leading=13,
        spaceAfter=2,
    )
    name_style = ParagraphStyle(
        "Name", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22, spaceAfter=2
    )
    section_style = ParagraphStyle(
        "Section",
        parent=base,
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
    )
    role_style = ParagraphStyle(
        "Role", parent=base, spaceBefore=4, spaceAfter=0
    )
    italic_style = ParagraphStyle(
        "Italic", parent=base, fontName="Helvetica-Oblique", spaceAfter=3
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=base, leftIndent=24, bulletIndent=12, spaceAfter=3
    )
    contact_style = ParagraphStyle("Contact", parent=base, spaceAfter=4)
    summary_style = ParagraphStyle("Summary", parent=base, spaceAfter=4)

    story = []

    # Name + tagline + contact
    story.append(Paragraph(esc(parsed["name"]), name_style))
    story.append(Paragraph(esc(parsed["tagline"]), base))
    story.append(Paragraph(esc(parsed["contact"]), contact_style))

    # Summary
    story.append(Paragraph("SUMMARY", section_style))
    story.append(Paragraph(esc(parsed["summary"]), summary_style))

    # Experience
    story.append(Paragraph("EXPERIENCE", section_style))
    for role in parsed["experience"]:
        title_html = f"<b>{esc(role['title'])}</b>&nbsp;&nbsp;&nbsp;&nbsp;{esc(role['dates'])}"
        story.append(Paragraph(title_html, role_style))
        if role["company"]:
            story.append(Paragraph(f"<i>{esc(role['company'])}</i>", italic_style))
        for lead, rest in role["bullets"]:
            if lead:
                bullet_html = f"<b>{esc(lead)}</b> {esc(rest)}"
            else:
                bullet_html = esc(rest)
            story.append(Paragraph(bullet_html, bullet_style, bulletText="•"))
        if role["footer"]:
            story.append(Paragraph(f"<i>{esc(role['footer'])}</i>", italic_style))

    # Skills
    story.append(Paragraph("SKILLS AND FOCUS AREAS", section_style))
    for cat, content in parsed["skills"]:
        skill_html = f"<b>{esc(cat)}:</b>&nbsp;&nbsp;{esc(content)}"
        story.append(Paragraph(skill_html, ParagraphStyle("Skill", parent=base, spaceAfter=3)))

    # Education
    story.append(Paragraph("EDUCATION", section_style))
    for entry in parsed["education"]:
        if entry.get("bold"):
            story.append(Paragraph(f"<b>{esc(entry['line'])}</b>", base))
        else:
            story.append(Paragraph(esc(entry["line"]), base))

    # Writing
    story.append(Paragraph("WRITING AND THOUGHT LEADERSHIP", section_style))
    for entry in parsed["writing"]:
        if "bold" in entry:
            if entry["rest"]:
                html = f"<b>{esc(entry['bold'])}</b>&nbsp;&nbsp;{esc(entry['rest'])}"
            else:
                html = f"<b>{esc(entry['bold'])}</b>"
            story.append(Paragraph(html, base))
        else:
            story.append(Paragraph(esc(entry["text"]), base))

    doc.build(story)
    return output_path


def build_from_md(md_path):
    md_path = Path(md_path)
    text = md_path.read_text()
    parsed = parse_resume_md(text)
    output_path = md_path.with_suffix(".pdf")
    build_pdf(parsed, str(output_path))
    return output_path


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    if target.is_file() and target.suffix == ".md":
        out = build_from_md(target)
        print(f"Saved: {out}")
    elif target.is_dir():
        for md_file in target.rglob("Ian_Cowpar_Resume_*.md"):
            out = build_from_md(md_file)
            print(f"Saved: {out}")
    else:
        print(f"Don't know how to handle: {target}")
        sys.exit(1)
