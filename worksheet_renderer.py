"""Round Two — worksheet renderer.

ReportLab canvas-direct renderer that reproduces the canonical practice
worksheet style from reference/module16_practice_worksheet.pdf. Step 2:
five-problem distribution with separator clearance + exponent markup
parser. Multi-page and answer key in Step 3; MC/table/short-answer
layouts in Step 4.
"""

from __future__ import annotations

import re
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
MARGIN_LEFT = 43
MARGIN_RIGHT = 43
MARGIN_TOP = 42      # title cap-line lands at the same y as the reference
MARGIN_BOTTOM = 22   # reference uses a tight bottom margin so 5 blocks fit at block_h ≈ 107.6

# Distance from the left margin to the column where each problem's prompt
# ("Find the sum.", "Find the difference.", etc.) starts. Pulled from the
# reference PDFs: every problem in module 16 page 1 has the prompt at this
# fixed tab stop, not at a floating offset after the label.
PROMPT_INDENT = 90

# CLAUDE.md rule 3: separator clearance. Block 0 has no top padding; every
# subsequent block has PAD_TOP added so the light-gray separator can sit
# halfway in the gap without colliding with the next problem's header.
PAD_TOP = 28

# Exponent rendering. Reference uses Helvetica 7.2pt for exponents alongside
# 11pt body — so the ratio is ~0.65. Raise is ~40% of body size, which puts
# the exponent's baseline near the cap-height of the surrounding text.
EXP_SIZE_RATIO = 0.65
EXP_RAISE_RATIO = 0.4

# `^N` (single alphanumeric) or `^{...}` (any non-} run). Negative or
# multi-character exponents must use the brace form: `^{-2}`, `^{n+1}`.
_EXPONENT_PATTERN = re.compile(r"\^(\{[^}]+\}|[A-Za-z0-9])")


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
    answer_key_title: str | None = None  # short form for the answer key (defaults to title)


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
    _render_answer_key_pages(c, worksheet)

    c.save()


# --- Page composition ---

def _render_type_page(c, worksheet_title: str, type_: ProblemType) -> None:
    y = PAGE_H - MARGIN_TOP
    y = _draw_page_header(c, worksheet_title, y)
    y -= 6   # ref: ~22pt name-baseline → type-baseline; with helper offsets this lands the type header at y ≈ 700
    y = _draw_section_header(c, type_, y)
    y -= 14  # ref: ~36pt type-baseline → example-header-baseline
    y = _draw_example_box(c, type_.example_lines, y)
    y = _draw_instruction_line(c, type_.instruction, y)
    y -= 2   # ref: ~14pt instruction-baseline → first-problem-baseline

    _draw_problems(c, type_.problems, y)


def _draw_problems(c, problems: list, y_top: float) -> None:
    """Distribute problems evenly down the page with separator clearance.

    Implements CLAUDE.md rules 2 and 3:
      block_h = (avail - PAD_TOP) / n   (block 0 has no top padding; blocks
                                          1..n-1 each get an extra PAD_TOP
                                          added once, between block 0 and
                                          block 1)
      problem i drawn at  y_top - i*block_h - (PAD_TOP if i > 0 else 0)
      separator i drawn at y_top - (i+1)*block_h - PAD_TOP/2

    The reference's 1-A → 1-B gap is block_h + PAD_TOP, while 1-B → 1-C,
    1-C → 1-D, 1-D → 1-E are all exactly block_h. This formula reproduces
    that pattern precisely.
    """
    n = len(problems)
    if n == 0:
        return
    avail = y_top - MARGIN_BOTTOM
    block_h = (avail - PAD_TOP) / n

    for i, problem in enumerate(problems):
        content_y = y_top - i * block_h - (PAD_TOP if i > 0 else 0)
        _draw_problem_centered(c, problem, content_y)
        if i < n - 1:
            sep_y = y_top - (i + 1) * block_h - PAD_TOP / 2
            c.setStrokeColor(GRAY_RULE)
            c.setLineWidth(0.5)
            c.line(MARGIN_LEFT, sep_y, PAGE_W - MARGIN_RIGHT, sep_y)


def _draw_page_header(c, title: str, y: float) -> float:
    """Title + rule + Name/Date/Period blanks. Returns new y (below the blanks)."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_LEFT, y - 11, title)
    y -= 14

    c.setStrokeColor(BLACK)
    c.setLineWidth(0.6)
    c.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
    y -= 15

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
    return y - 4


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
    pad_y = 7      # tighter than 10 to match reference's example-box density
    line_h = 13
    header_gap = 3 # reference: ~16pt example-header → first-body-line gap (= line_h + 3)

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
    c.setFont("Helvetica-Bold", 9)
    inner_y = box_top - pad_y - 9
    c.drawString(box_x + pad_x, inner_y, "EXAMPLE — Look at this before you begin:")
    inner_y -= line_h + header_gap

    # Body lines (last line bold — the answer)
    for i, line in enumerate(lines):
        is_last = i == len(lines) - 1
        c.setFont("Helvetica-Bold" if is_last else "Helvetica", 9)
        c.drawString(box_x + pad_x, inner_y, line)
        inner_y -= line_h

    return box_bottom


def _draw_instruction_line(c, text: str, y: float) -> float:
    """Plain instruction sentence between the example box and the problems.
    Reference uses regular Helvetica 9pt — not italic, despite first-impression
    appearance in the rendered PDF."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_LEFT, y - 10, text)
    return y - 12


def _draw_problem_centered(c, problem: Problem, y: float) -> float:
    """Centered-expression layout: bold label + regular prompt on one row, then
    a centered body expression. The body is drawn through the exponent parser
    so `m^2` renders as `m²` (true superscript), not as a black box."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    label_text = f"Problem {problem.label}."
    c.drawString(MARGIN_LEFT, y - 10, label_text)

    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_LEFT + PROMPT_INDENT, y - 10, problem.prompt)

    body_y = y - 28  # reference: ~18pt label-baseline → body-baseline
    body_w = _width_with_exponents(c, problem.body, "Helvetica", 11)
    body_x = (PAGE_W - body_w) / 2
    _draw_text_with_exponents(c, body_x, body_y, problem.body, "Helvetica", 11)

    return body_y - 14


# --- Answer key page ---

ANSWER_KEY_INDENT = 14  # answer rows sit 14pt to the right of MARGIN_LEFT (matches reference x=57.2 - 43.2)
ANSWER_LINE_H = 12      # vertical step between consecutive answer rows in the reference
ANSWER_TYPE_GAP = 5     # extra whitespace below the last answer of one type before the next type's subheader


def _render_answer_key_pages(c, worksheet: Worksheet) -> None:
    """Render the answer key page(s) at the end of the PDF.

    Falls onto a continuation page ('Answer Key (continued)') if the remaining
    types don't fit. Sized for module 16 (4 types fit on one page) and module
    13/14 (8 types on page 1, type 9 on a continuation page) without changes.
    """
    y = _start_answer_key_page(c, worksheet, continued=False)

    for type_ in worksheet.types:
        # Estimate vertical room for this type: subheader + N answer lines + a small trailing gap.
        type_h = 14 + ANSWER_LINE_H * len(type_.problems) + ANSWER_TYPE_GAP
        if y - type_h < MARGIN_BOTTOM:
            c.showPage()
            y = _start_answer_key_page(c, worksheet, continued=True)

        # Per-type subheader — NAVY 10pt bold, uses the shorter answer_key_title if provided.
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        ak_title = type_.answer_key_title or type_.title
        c.drawString(MARGIN_LEFT, y - 10, f"Type {type_.number} — {ak_title}")
        y -= 14

        # Answer rows — Helvetica 8.5pt, label + answer on one line, answer through the exponent parser.
        c.setFillColor(BLACK)
        for problem in type_.problems:
            x_label = MARGIN_LEFT + ANSWER_KEY_INDENT
            c.setFont("Helvetica", 8.5)
            c.drawString(x_label, y - 9, problem.label)
            label_w = c.stringWidth(problem.label, "Helvetica", 8.5)
            _draw_text_with_exponents(
                c, x_label + label_w + 8, y - 9, problem.answer, "Helvetica", 8.5
            )
            y -= ANSWER_LINE_H

        y -= ANSWER_TYPE_GAP


def _start_answer_key_page(c, worksheet: Worksheet, continued: bool) -> float:
    """Begin an answer-key page: page header + 'Answer Key' header. Returns the y
    position right below the header rule (where the first type subheader lands)."""
    y = PAGE_H - MARGIN_TOP
    y = _draw_page_header(c, worksheet.title, y)
    y -= 6
    label = "Answer Key (continued)" if continued else "Answer Key"
    y = _draw_answer_key_header(c, y, label)
    y -= 8  # ref: ~22pt baseline-to-baseline from "Answer Key" to first type subheader
    return y


def _draw_answer_key_header(c, y: float, text: str) -> float:
    """NAVY 13pt bold header with rule beneath. Mirrors the section-header
    pattern but at the larger answer-key size."""
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN_LEFT, y - 13, text)
    y -= 17
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.7)
    c.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
    return y


# --- Exponent markup ---

def _parse_exponent_markup(s: str) -> list[tuple[str, str]]:
    """Tokenize a string with `^N` / `^{...}` markup into runs.

    'm^2n - 3mn^2'  ->  [('text','m'), ('exp','2'), ('text','n - 3mn'), ('exp','2')]
    'x^{10}'        ->  [('text','x'), ('exp','10')]
    """
    out: list[tuple[str, str]] = []
    pos = 0
    for m in _EXPONENT_PATTERN.finditer(s):
        if m.start() > pos:
            out.append(("text", s[pos:m.start()]))
        exp = m.group(1)
        if exp.startswith("{"):
            exp = exp[1:-1]
        out.append(("exp", exp))
        pos = m.end()
    if pos < len(s):
        out.append(("text", s[pos:]))
    return out


def _width_with_exponents(c, text: str, font: str, size: float) -> float:
    exp_size = size * EXP_SIZE_RATIO
    w = 0.0
    for kind, t in _parse_exponent_markup(text):
        w += c.stringWidth(t, font, exp_size if kind == "exp" else size)
    return w


def _draw_text_with_exponents(
    c, x: float, y: float, text: str, font: str, size: float
) -> float:
    """Draw `text` at (x, y) interpreting `^N` and `^{...}` as superscripts.
    Returns the x position after the last glyph."""
    exp_size = size * EXP_SIZE_RATIO
    raise_y = size * EXP_RAISE_RATIO
    cur = x
    for kind, t in _parse_exponent_markup(text):
        if kind == "exp":
            c.setFont(font, exp_size)
            c.drawString(cur, y + raise_y, t)
            cur += c.stringWidth(t, font, exp_size)
        else:
            c.setFont(font, size)
            c.drawString(cur, y, t)
            cur += c.stringWidth(t, font, size)
    return cur
