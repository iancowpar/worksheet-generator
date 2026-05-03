"""Round Two — worksheet renderer.

ReportLab canvas-direct renderer that reproduces the canonical practice
worksheet style from reference/module16_practice_worksheet.pdf. This is
Step 1: page header + section header + example box + one problem, drawn
at fixed y. Distribution math (block_h) and exponent parser arrive in
Step 2; multi-page and answer key in Step 3; MC/table/short-answer
layouts in Step 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as canvas_module

# --- Visual constants from CLAUDE.md ---

NAVY = colors.HexColor("#1B2B5E")
BLACK = colors.HexColor("#111111")
LIGHT = colors.HexColor("#f0f0eb")  # example box fill
TAN = colors.HexColor("#d8cfc4")    # example box border
GRAY_RULE = colors.HexColor("#cccccc")

PAGE_W, PAGE_H = letter
MARGIN_LEFT = 50
MARGIN_RIGHT = 50
MARGIN_TOP = 50

# Reserved for Step 2 (separator clearance rule from CLAUDE.md)
PAD_TOP = 28


# --- Data shapes ---

@dataclass(frozen=True)
class Problem:
    label: str       # "1-A"
    prompt: str      # "Find the sum."
    body: str        # the centered expression text
    answer: str      # canonical answer (used for the answer key)


@dataclass(frozen=True)
class ProblemType:
    number: int
    title: str
    instruction: str
    example_lines: list[str]   # last line is rendered bold (the worked answer)
    problems: list[Problem]


@dataclass(frozen=True)
class Worksheet:
    title: str
    types: list[ProblemType]


# --- Public entry point ---

def render_worksheet(worksheet: Worksheet, output_path: str | Path) -> None:
    output_path = Path(output_path)
    c = canvas_module.Canvas(str(output_path), pagesize=letter)
    c.setTitle(worksheet.title)
    c.setAuthor("Round Two")

    for type_ in worksheet.types:
        _render_type_page(c, worksheet.title, type_)
        c.showPage()

    c.save()


# --- Page composition ---

def _render_type_page(c, worksheet_title: str, type_: ProblemType) -> None:
    y = PAGE_H - MARGIN_TOP
    y = _draw_page_header(c, worksheet_title, y)
    y -= 14
    y = _draw_section_header(c, type_, y)
    y -= 14
    y = _draw_example_box(c, type_.example_lines, y)
    y -= 8
    y = _draw_instruction_line(c, type_.instruction, y)
    y -= 18

    if type_.problems:
        _draw_problem_centered(c, type_.problems[0], y)


def _draw_page_header(c, title: str, y: float) -> float:
    """Title + rule + Name/Date/Period blanks. Returns new y (below the blanks)."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN_LEFT, y - 12, title)
    y -= 16

    c.setStrokeColor(BLACK)
    c.setLineWidth(0.6)
    c.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
    y -= 22

    c.setFont("Helvetica", 10)
    fields = [
        ("Name:", 220),
        ("Date:", 110),
        ("Period:", 90),
    ]
    x = MARGIN_LEFT
    for label, blank_w in fields:
        c.drawString(x, y, label)
        label_w = c.stringWidth(label, "Helvetica", 10)
        blank_x = x + label_w + 4
        c.setStrokeColor(BLACK)
        c.setLineWidth(0.5)
        c.line(blank_x, y - 2, blank_x + blank_w, y - 2)
        x = blank_x + blank_w + 18
    return y - 12


def _draw_section_header(c, type_: ProblemType, y: float) -> float:
    """'Type N — Title' in NAVY bold, with a NAVY rule beneath. Returns new y."""
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN_LEFT, y - 12, f"Type {type_.number} — {type_.title}")
    y -= 16

    c.setStrokeColor(NAVY)
    c.setLineWidth(0.7)
    c.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
    return y


def _draw_example_box(c, lines: list[str], y: float) -> float:
    """Cream box with tan border holding the worked example. Returns new y (box bottom)."""
    box_x = MARGIN_LEFT
    box_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    pad_x = 12
    pad_y = 10
    line_h = 13
    header_gap = 6

    # Compute height: header + gap + body lines + top/bottom padding
    body_h = line_h + header_gap + line_h * len(lines)
    box_h = body_h + 2 * pad_y

    box_top = y
    box_bottom = y - box_h

    c.setFillColor(LIGHT)
    c.setStrokeColor(TAN)
    c.setLineWidth(0.8)
    c.rect(box_x, box_bottom, box_w, box_h, fill=1, stroke=1)

    # Header
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    inner_y = box_top - pad_y - 10
    c.drawString(box_x + pad_x, inner_y, "EXAMPLE — Look at this before you begin:")
    inner_y -= line_h + header_gap

    # Body lines (last line bold — the answer)
    for i, line in enumerate(lines):
        is_last = i == len(lines) - 1
        c.setFont("Helvetica-Bold" if is_last else "Helvetica", 10)
        c.drawString(box_x + pad_x, inner_y, line)
        inner_y -= line_h

    return box_bottom


def _draw_instruction_line(c, text: str, y: float) -> float:
    """Italic instruction sentence between the example box and the problems."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(MARGIN_LEFT, y - 12, text)
    return y - 14


def _draw_problem_centered(c, problem: Problem, y: float) -> float:
    """Centered-expression layout: bold label + bold prompt on one row, then a
    centered body expression. Returns the y below the body. Step 1 uses fixed
    spacing; Step 2 will replace this with the block_h distribution math."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 11)
    label_text = f"Problem {problem.label}."
    c.drawString(MARGIN_LEFT, y - 12, label_text)

    label_w = c.stringWidth(label_text, "Helvetica-Bold", 11)
    c.drawString(MARGIN_LEFT + label_w + 12, y - 12, problem.prompt)

    y -= 26

    c.setFont("Helvetica", 11)
    body_w = c.stringWidth(problem.body, "Helvetica", 11)
    body_x = (PAGE_W - body_w) / 2
    c.drawString(body_x, y, problem.body)

    return y - 14
