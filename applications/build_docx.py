"""Convert one of our standard resume markdown files into a .docx.

Usage:
    python3 applications/build_docx.py applications/jerry-ai/Ian_Cowpar_Resume_Jerry_AI.md
    python3 applications/build_docx.py applications/   # builds every *.md in subdirs

Assumes our standard resume markdown format (see Ian_Cowpar_Resume_Master.md).
"""

import re
import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches


SECTION_HEADERS = {
    "**SUMMARY**",
    "**SELECTED OUTCOMES**",
    "**EXPERIENCE**",
    "**SKILLS AND FOCUS AREAS**",
    "**EDUCATION**",
    "**WRITING AND THOUGHT LEADERSHIP**",
}


def parse_resume_md(text):
    lines = [ln.rstrip() for ln in text.split("\n")]
    out = {
        "name": "",
        "tagline": "",
        "contact": "",
        "summary": "",
        "outcomes": [],
        "experience": [],
        "skills": [],
        "education": [],
        "writing": [],
    }
    section = "header"
    role = None

    def is_role_title(s):
        # Match "**Title** Date Range" (where Title doesn't contain SKILLS, EDUCATION, etc.)
        m = re.match(r"^\*\*([^*]+?)\*\*\s+(.+)$", s)
        if not m:
            return None
        title = m.group(1).strip()
        if title.isupper():
            return None
        return (title, m.group(2).strip())

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # skip markdown horizontal rules (source-file organization only)
        if re.fullmatch(r"-{3,}", line):
            i += 1
            continue

        if line in SECTION_HEADERS:
            section = line.strip("*").strip().lower().split(" ")[0]
            # normalize
            if line == "**SKILLS AND FOCUS AREAS**":
                section = "skills"
            elif line == "**WRITING AND THOUGHT LEADERSHIP**":
                section = "writing"
            elif line == "**SELECTED OUTCOMES**":
                section = "outcomes"
            i += 1
            continue

        if section == "header":
            if not out["name"] and line.startswith("**") and line.endswith("**"):
                out["name"] = line.strip("*").strip()
            elif not out["tagline"]:
                out["tagline"] = line
            elif not out["contact"]:
                out["contact"] = line
            i += 1
            continue

        if section == "summary":
            out["summary"] = line
            i += 1
            continue

        if section == "outcomes":
            if line.startswith("- "):
                bullet_text = line[2:].strip()
                m = re.match(r"^\*\*([^*]+?)\*\*\s*(.*)$", bullet_text)
                if m:
                    out["outcomes"].append((m.group(1).strip(), m.group(2).strip()))
                else:
                    out["outcomes"].append(("", bullet_text))
            i += 1
            continue

        if section == "experience":
            rt = is_role_title(line)
            if rt:
                role = {"title": rt[0], "dates": rt[1], "company": "", "bullets": [], "footer": ""}
                out["experience"].append(role)
                i += 1
                continue
            if line.startswith("*") and not line.startswith("**") and line.endswith("*"):
                content = line.strip("*").strip()
                if role and not role["company"]:
                    role["company"] = content
                elif role:
                    role["footer"] = content
                i += 1
                continue
            if line.startswith("- "):
                bullet_text = line[2:].strip()
                m = re.match(r"^\*\*([^*]+?)\*\*\s*(.*)$", bullet_text)
                if m:
                    role["bullets"].append((m.group(1).strip(), m.group(2).strip()))
                else:
                    role["bullets"].append(("", bullet_text))
                i += 1
                continue
            i += 1
            continue

        if section == "skills":
            m = re.match(r"^\*\*([^*]+?):\*\*\s*(.*)$", line)
            if m:
                out["skills"].append((m.group(1).strip(), m.group(2).strip()))
            i += 1
            continue

        if section == "education":
            if line.startswith("**") and line.endswith("**"):
                out["education"].append({"line": line.strip("*").strip(), "bold": True})
            else:
                out["education"].append({"line": line, "bold": False})
            i += 1
            continue

        if section == "writing":
            if line.startswith("**"):
                # "**The Unofficial Leader**  (Substack)  |  url"
                m = re.match(r"^\*\*([^*]+?)\*\*\s*(.*)$", line)
                if m:
                    out["writing"].append({"bold": m.group(1).strip(), "rest": m.group(2).strip()})
                else:
                    out["writing"].append({"bold": line.strip("*").strip(), "rest": ""})
            else:
                out["writing"].append({"text": line})
            i += 1
            continue

        i += 1

    return out


def build_docx(parsed, output_path):
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    def add_run(p, text, bold=False, italic=False, size=None):
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.name = "Calibri"
        if size:
            r.font.size = Pt(size)
        return r

    def add_body(runs, indent=None, space_before=0, space_after=2, style=None):
        p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        if indent is not None:
            p.paragraph_format.left_indent = Inches(indent)
        for text, bold, italic in runs:
            add_run(p, text, bold=bold, italic=italic)
        return p

    def add_section_header(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        add_run(p, text, bold=True, size=11)
        return p

    # === NAME ===
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    add_run(p, parsed["name"], bold=True, size=18)

    # === TAGLINE ===
    add_body([(parsed["tagline"], False, False)], space_after=2)

    # === CONTACT ===
    add_body([(parsed["contact"], False, False)], space_after=4)

    # === SUMMARY ===
    add_section_header("SUMMARY")
    add_body([(parsed["summary"], False, False)], space_after=4)

    # === SELECTED OUTCOMES ===
    if parsed.get("outcomes"):
        add_section_header("SELECTED OUTCOMES")
        for lead, rest in parsed["outcomes"]:
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.left_indent = Inches(0.25)
            if lead:
                add_run(p, lead + " ", bold=True)
            add_run(p, rest, bold=False)

    # === EXPERIENCE ===
    add_section_header("EXPERIENCE")

    for idx, role in enumerate(parsed["experience"]):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4 if idx > 0 else 2)
        p.paragraph_format.space_after = Pt(0)
        add_run(p, role["title"], bold=True)
        add_run(p, "    " + role["dates"], bold=False)

        if role["company"]:
            add_body([(role["company"], False, True)], space_after=3)

        for lead, rest in role["bullets"]:
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.left_indent = Inches(0.25)
            if lead:
                add_run(p, lead + " ", bold=True)
            add_run(p, rest, bold=False)

        if role["footer"]:
            add_body([(role["footer"], False, True)], space_after=2)

    # === SKILLS ===
    add_section_header("SKILLS AND FOCUS AREAS")
    for cat, content in parsed["skills"]:
        add_body([(cat + ":  ", True, False), (content, False, False)], space_after=3)

    # === EDUCATION ===
    add_section_header("EDUCATION")
    for entry in parsed["education"]:
        if entry.get("bold"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            add_run(p, entry["line"], bold=True)
        else:
            add_body([(entry["line"], False, False)], space_after=2)

    # === WRITING ===
    add_section_header("WRITING AND THOUGHT LEADERSHIP")
    for entry in parsed["writing"]:
        if "bold" in entry:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            add_run(p, entry["bold"], bold=True)
            if entry["rest"]:
                add_run(p, "  " + entry["rest"], bold=False)
        else:
            add_body([(entry["text"], False, False)], space_after=2)

    doc.save(output_path)
    return output_path


def build_from_md(md_path):
    md_path = Path(md_path)
    text = md_path.read_text()
    parsed = parse_resume_md(text)
    output_path = md_path.with_suffix(".docx")
    build_docx(parsed, str(output_path))
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
