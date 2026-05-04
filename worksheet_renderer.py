"""Round Two — worksheet renderer.

ReportLab canvas-direct renderer that reproduces the canonical practice
worksheet style from the reference PDFs in `reference/`. Step 4 adds the
six layout variants needed to cover both reference outputs end-to-end:

    centered             - module 16 Types 1, 2 (and the original default)
    word_setup           - module 16 Type 3 (paragraph + pre-filled "P = ...")
    word_blanks          - module 16 Type 4 (paragraph + 2-col fillable blanks)
    mc_2col              - module 13/14 Types 1, 2, 3, 5 (4 options in 2 cols)
    mc_4row              - module 13/14 Type 4 (4 options stacked vertically)
    short_answer_right   - module 13/14 Type 7 ("r = ___" same row as label)
    short_answer_below   - module 13/14 Type 9 ("f(n) = ___" full-width below)
    table                - module 13/14 Type 6 (single multi-row classify grid)
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
MARGIN_TOP = 42
MARGIN_BOTTOM = 22

# Column where each problem's prompt ("Find the sum.", etc.) starts in the
# centered layout — fixed tab stop, not floating after the label.
PROMPT_INDENT = 90

# Within-block indent used by setup lines (Type 3) and option labels (MC).
INNER_INDENT = 16

# Two-column horizontal positions used by word_blanks and MC layouts.
# Pulled from the reference: column 1 starts at MARGIN_LEFT + 16 = 59.2,
# column 2 starts at x=322 (about 280pt right of column 1).
COL1_X = MARGIN_LEFT + INNER_INDENT
COL2_X = 322
COL_BLANK_W = 200  # underscored answer-blank width in the right portion of each column

# CLAUDE.md rule 3: separator clearance.
PAD_TOP = 28

# Exponent rendering — reference uses 7.2pt for 11pt body (ratio ~0.65).
EXP_SIZE_RATIO = 0.65
EXP_RAISE_RATIO = 0.4

# `^N` (single alphanumeric) or `^{...}` (any non-} run).
_EXPONENT_PATTERN = re.compile(r"\^(\{[^}]+\}|[A-Za-z0-9])")


# --- Data shapes ---

@dataclass(frozen=True)
class Problem:
    label: str
    body: str
    answer: str
    prompt: str = ""                            # centered layout
    setup: str | None = None                    # word_setup
    blanks: list[str] | None = None             # word_blanks
    options: list[str] | None = None            # mc_*  (4 entries, A-D)
    correct_letter: str | None = None           # mc_*
    answer_label: str | None = None             # short_answer_*  (e.g., "r =", "f(n) =")


@dataclass(frozen=True)
class ProblemType:
    number: int
    title: str
    instruction: str
    example_lines: list[str]
    problems: list[Problem]
    answer_key_title: str | None = None
    layout: str = "centered"
    table_columns: list[str] | None = None      # table layout (e.g., ["Arithmetic", "Geometric"])


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
    y -= 6
    y = _draw_section_header(c, type_, y)
    y -= 14
    y = _draw_example_box(c, type_.example_lines, y)
    y = _draw_instruction_line(c, type_.instruction, y)
    y -= 2

    if type_.layout == "table":
        _draw_classification_table(c, type_, y)
    else:
        _draw_problems(c, type_, y)


def _draw_problems(c, type_: ProblemType, y_top: float) -> None:
    """Distribute problems evenly down the page with separator clearance."""
    problems = type_.problems
    n = len(problems)
    if n == 0:
        return
    avail = y_top - MARGIN_BOTTOM
    block_h = (avail - PAD_TOP) / n
    draw_fn = LAYOUT_DRAW_FNS[type_.layout]

    for i, problem in enumerate(problems):
        content_y = y_top - i * block_h - (PAD_TOP if i > 0 else 0)
        draw_fn(c, problem, content_y, block_h)
        if i < n - 1:
            sep_y = y_top - (i + 1) * block_h - PAD_TOP / 2
            c.setStrokeColor(GRAY_RULE)
            c.setLineWidth(0.5)
            c.line(MARGIN_LEFT, sep_y, PAGE_W - MARGIN_RIGHT, sep_y)


def _draw_page_header(c, title: str, y: float) -> float:
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_LEFT, y - 11, title)
    y -= 14

    c.setStrokeColor(BLACK)
    c.setLineWidth(0.6)
    c.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
    y -= 15

    c.setFont("Helvetica", 10)
    fields = [("Name:", 220), ("Date:", 110), ("Period:", 90)]
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
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN_LEFT, y - 12, f"Type {type_.number} — {type_.title}")
    y -= 16
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.7)
    c.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
    return y


def _draw_example_box(c, lines: list[str], y: float) -> float:
    box_x = MARGIN_LEFT
    box_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    pad_x = 12
    pad_y = 7
    line_h = 13
    header_gap = 3

    body_h = line_h + header_gap + line_h * len(lines)
    box_h = body_h + 2 * pad_y

    box_top = y
    box_bottom = y - box_h

    c.setFillColor(LIGHT)
    c.setStrokeColor(TAN)
    c.setLineWidth(0.8)
    c.rect(box_x, box_bottom, box_w, box_h, fill=1, stroke=1)

    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 9)
    inner_y = box_top - pad_y - 9
    c.drawString(box_x + pad_x, inner_y, "EXAMPLE — Look at this before you begin:")
    inner_y -= line_h + header_gap

    for i, line in enumerate(lines):
        is_last = i == len(lines) - 1
        c.setFont("Helvetica-Bold" if is_last else "Helvetica", 9)
        _draw_text_with_exponents(c, box_x + pad_x, inner_y, line, "Helvetica-Bold" if is_last else "Helvetica", 9)
        inner_y -= line_h

    return box_bottom


def _draw_instruction_line(c, text: str, y: float) -> float:
    c.setFillColor(BLACK)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_LEFT, y - 10, text)
    return y - 12


# --- Per-problem layout renderers ---

def _draw_problem_centered(c, problem: Problem, y: float, block_h: float) -> None:
    """Bold label + regular prompt on one row; centered body expression below."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y - 10, f"Problem {problem.label}.")

    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_LEFT + PROMPT_INDENT, y - 10, problem.prompt)

    body_y = y - 28
    body_w = _width_with_exponents(c, problem.body, "Helvetica", 11)
    body_x = (PAGE_W - body_w) / 2
    _draw_text_with_exponents(c, body_x, body_y, problem.body, "Helvetica", 11)


def _draw_problem_word_setup(c, problem: Problem, y: float, block_h: float) -> None:
    """Bold label · paragraph (wrapped) · pre-filled setup line indented from margin.

    Layout from module 16 Type 3:
      Problem 3-A.                                      <- label, bold 10pt at margin
      Find the perimeter of a triangle with sides ...   <- paragraph, regular 9pt at margin
        P = (3x + 2) + (5x - 1) + (2x + 4)              <- setup, regular 9pt indented 16pt
    """
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y - 10, f"Problem {problem.label}.")

    body_y = y - 25
    max_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    last_y = _draw_paragraph(c, MARGIN_LEFT, body_y, problem.body, "Helvetica", 9, 13, max_w)

    if problem.setup:
        setup_y = last_y - 17
        _draw_text_with_exponents(c, MARGIN_LEFT + INNER_INDENT, setup_y, problem.setup, "Helvetica", 9)


def _draw_problem_word_blanks(c, problem: Problem, y: float, block_h: float) -> None:
    """Bold label · paragraph (wrapped) · two-column row of bold answer cues.

    Layout from module 16 Type 4 (and any profit/substitution word problem):
      Problem 4-A.
      The revenue for a company selling x products is modeled by ... if x = 5.
        Profit expression:                If x = 5, profit =

    No fill-in-the-blank rules are drawn after the cues — the teacher decided
    those eat working space and the student is better served by an open
    expanse beneath the cues to show their work freehand. The two-column
    label arrangement is binding for this layout regardless of what's in
    `problem.blanks`.
    """
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y - 10, f"Problem {problem.label}.")

    body_y = y - 25
    max_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    last_y = _draw_paragraph(c, MARGIN_LEFT, body_y, problem.body, "Helvetica", 9, 13, max_w)

    if problem.blanks:
        cues_y = last_y - 19
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 9)
        col_xs = [COL1_X, COL2_X]
        for i, label in enumerate(problem.blanks[:2]):
            c.drawString(col_xs[i], cues_y, label)


def _draw_problem_mc_2col(c, problem: Problem, y: float, block_h: float) -> None:
    """Bold label · paragraph stem · 4 options laid out as 2 columns (A,B left · C,D right).

    Module 13/14 Types 1, 2, 3, 5. Options are short — fits in two columns.
    """
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y - 10, f"Problem {problem.label}.")

    body_y = y - 25
    max_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    last_y = _draw_paragraph(c, MARGIN_LEFT, body_y, problem.body, "Helvetica", 9, 13, max_w)

    if not problem.options or len(problem.options) < 4:
        return

    options_y_top = last_y - 17
    line_h = 13
    layout_positions = [
        (COL1_X, options_y_top),                # (A) top-left
        (COL1_X, options_y_top - line_h),       # (B) bottom-left
        (COL2_X, options_y_top),                # (C) top-right
        (COL2_X, options_y_top - line_h),       # (D) bottom-right
    ]
    for letter_idx, ((opt_x, opt_y), opt_text) in enumerate(zip(layout_positions, problem.options)):
        _draw_mc_option(c, opt_x, opt_y, "ABCD"[letter_idx], opt_text)


def _draw_problem_mc_4row(c, problem: Problem, y: float, block_h: float) -> None:
    """Bold label · paragraph stem · 4 options stacked vertically (long sentence options).

    Module 13/14 Type 4 — option text is too long for 2-column layout, so each
    option gets its own row. Options may themselves wrap to multiple lines.
    """
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y - 10, f"Problem {problem.label}.")

    body_y = y - 25
    max_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    last_y = _draw_paragraph(c, MARGIN_LEFT, body_y, problem.body, "Helvetica", 9, 13, max_w)

    if not problem.options or len(problem.options) < 4:
        return

    opt_y = last_y - 17
    opt_max_w = PAGE_W - MARGIN_RIGHT - COL1_X - 22  # leave room for "(A) " prefix
    for i, opt_text in enumerate(problem.options):
        opt_y = _draw_mc_option_wrapped(c, COL1_X, opt_y, "ABCD"[i], opt_text, opt_max_w)
        opt_y -= 2  # small gap between options


def _draw_problem_short_answer_right(c, problem: Problem, y: float, block_h: float) -> None:
    """Bold label + right-aligned blank (with optional answer label) on the same row · paragraph below.

    Module 13/14 Type 7 (with `r =` label):
      Problem 7-A.                              r = _____________
      What is the common ratio of the sequence 81, 27, 9, 3, 1, ...?

    Module 13/14 Type 8 (no label — student knows from the question what to write):
      Problem 8-A.                                  _____________
      If f(x) = 625(0.8)^x, what is the value of f(4)?
    """
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y - 10, f"Problem {problem.label}.")

    # Reference anchors `r =` (and similar short-answer labels) at a fixed
    # tab stop ~350pt from the left margin, with the blank running from the
    # end of the label to the right margin. Type 8 has no label — the blank
    # starts at the same anchor.
    label_anchor_x = MARGIN_LEFT + 350
    right_edge = PAGE_W - MARGIN_RIGHT

    if problem.answer_label:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(label_anchor_x, y - 10, problem.answer_label)
        label_w = c.stringWidth(problem.answer_label, "Helvetica-Bold", 9)
        blank_x = label_anchor_x + label_w + 6
    else:
        blank_x = label_anchor_x
    _draw_blank(c, blank_x, y - 12, right_edge - blank_x)

    body_y = y - 23
    max_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    _draw_paragraph(c, MARGIN_LEFT, body_y, problem.body, "Helvetica", 9, 13, max_w)


def _draw_problem_short_answer_below(c, problem: Problem, y: float, block_h: float) -> None:
    """Bold label · paragraph stem · "f(n) = ___" full-width line beneath.

    Module 13/14 Type 9:
      Problem 9-A.
      A geometric sequence has a first term of 6 and a common ratio of 4. ...
        f(n) = ________________________________
    """
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_LEFT, y - 10, f"Problem {problem.label}.")

    body_y = y - 25
    max_w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    last_y = _draw_paragraph(c, MARGIN_LEFT, body_y, problem.body, "Helvetica", 9, 13, max_w)

    if problem.answer_label:
        ans_y = last_y - 17
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN_LEFT + INNER_INDENT, ans_y, problem.answer_label)
        label_w = c.stringWidth(problem.answer_label, "Helvetica-Bold", 9)
        blank_x = MARGIN_LEFT + INNER_INDENT + label_w + 6
        _draw_blank(c, blank_x, ans_y - 2, PAGE_W - MARGIN_RIGHT - blank_x)


def _draw_classification_table(c, type_: ProblemType, y_top: float) -> None:
    """Single multi-row grid for module 13/14 Type 6 (Arithmetic vs. Geometric).

    Reference geometry:
      header row: x=43.2, top=205.2, width=480, height=30
      body rows: each 103.4pt tall, total 5 rows
      column borders at x=323.2 and x=423.2  (sequence ~280pt, then two ~100pt cols)
    """
    table_x = MARGIN_LEFT
    table_w = 480
    header_h = 30
    row_h = 103.4

    # Position table top right after the instruction line + small gap.
    table_top = y_top - 8
    n = len(type_.problems)

    # Header row
    c.setStrokeColor(BLACK)
    c.setLineWidth(0.6)
    c.setFillColor(colors.white)
    c.rect(table_x, table_top - header_h, table_w, header_h, fill=0, stroke=1)

    # Header text — Helvetica-Bold 9pt, centered in each classification column.
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 9)
    col1_border = table_x + 280
    col2_border = table_x + 380
    table_right = table_x + table_w
    cols = type_.table_columns or ["Arithmetic", "Geometric"]
    if len(cols) >= 2:
        for label, cell_x_left, cell_x_right in [
            (cols[0], col1_border, col2_border),
            (cols[1], col2_border, table_right),
        ]:
            label_w = c.stringWidth(label, "Helvetica-Bold", 9)
            cx = cell_x_left + (cell_x_right - cell_x_left - label_w) / 2
            c.drawString(cx, table_top - header_h + 11, label)

    # Body rows
    c.setFont("Helvetica", 9)
    for i, problem in enumerate(type_.problems[:5]):
        row_top = table_top - header_h - i * row_h
        row_bottom = row_top - row_h
        # Row outline
        c.setStrokeColor(BLACK)
        c.setLineWidth(0.6)
        c.rect(table_x, row_bottom, table_w, row_h, fill=0, stroke=1)
        # Internal vertical borders
        c.line(col1_border, row_bottom, col1_border, row_top)
        c.line(col2_border, row_bottom, col2_border, row_top)
        # Sequence text (vertically centered within the row)
        seq_x = table_x + 10
        seq_y = row_bottom + row_h / 2 - 3
        _draw_text_with_exponents(c, seq_x, seq_y, problem.body, "Helvetica", 9)


# --- Helpers ---

def _draw_mc_option(c, x: float, y: float, letter: str, text: str) -> None:
    """Single-row option: '(A) <text>' at (x, y), regular 9pt with exponent rendering."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica", 9)
    prefix = f"({letter})"
    c.drawString(x, y, prefix)
    prefix_w = c.stringWidth(prefix, "Helvetica", 9)
    _draw_text_with_exponents(c, x + prefix_w + 6, y, text, "Helvetica", 9)


def _draw_mc_option_wrapped(c, x: float, y: float, letter: str, text: str, max_w: float) -> float:
    """Multi-line option for mc_4row. Returns the y for the next option's first line
    (i.e., one line_h below the last line drawn — caller adds further gap if needed)."""
    c.setFillColor(BLACK)
    c.setFont("Helvetica", 9)
    prefix = f"({letter})"
    c.drawString(x, y, prefix)
    prefix_w = c.stringWidth(prefix, "Helvetica", 9)
    text_x = x + prefix_w + 6
    lines = _wrap_text(c, text, max_w, "Helvetica", 9)
    for i, line in enumerate(lines):
        c.drawString(text_x, y - i * 12, line)
    return y - len(lines) * 12


def _draw_blank(c, x: float, y: float, width: float) -> None:
    """Underscored answer-blank line. y is the line's vertical position."""
    c.setStrokeColor(BLACK)
    c.setLineWidth(0.5)
    c.line(x, y, x + width, y)


def _wrap_text(c, text: str, max_width: float, font: str, size: float) -> list[str]:
    """Greedy word-wrap. Returns lines that each fit within max_width.

    Treats ^N and ^{...} markup as part of the preceding word for measurement
    so a token like 'm^2n' is kept whole. We measure widths through
    `_width_with_exponents` so superscript glyphs are accounted for.
    """
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if _width_with_exponents(c, candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _draw_paragraph(
    c, x: float, y_first: float, text: str, font: str, size: float, line_h: float, max_width: float
) -> float:
    """Draw a wrapped paragraph; first line at y_first. Returns baseline of LAST line."""
    lines = _wrap_text(c, text, max_width, font, size)
    c.setFillColor(BLACK)
    for i, line in enumerate(lines):
        _draw_text_with_exponents(c, x, y_first - i * line_h, line, font, size)
    return y_first - (len(lines) - 1) * line_h


# Layout dispatch — table is special-cased upstream in _render_type_page.
LAYOUT_DRAW_FNS = {
    "centered": _draw_problem_centered,
    "word_setup": _draw_problem_word_setup,
    "word_blanks": _draw_problem_word_blanks,
    "mc_2col": _draw_problem_mc_2col,
    "mc_4row": _draw_problem_mc_4row,
    "short_answer_right": _draw_problem_short_answer_right,
    "short_answer_below": _draw_problem_short_answer_below,
}


# --- Answer key page ---

ANSWER_KEY_INDENT = 14
ANSWER_LINE_H = 12
ANSWER_TYPE_GAP = 5


def _render_answer_key_pages(c, worksheet: Worksheet) -> None:
    y = _start_answer_key_page(c, worksheet, continued=False)

    for type_ in worksheet.types:
        type_h = 14 + ANSWER_LINE_H * len(type_.problems) + ANSWER_TYPE_GAP
        if y - type_h < MARGIN_BOTTOM:
            c.showPage()
            y = _start_answer_key_page(c, worksheet, continued=True)

        # Per-type subheader
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        ak_title = type_.answer_key_title or type_.title
        c.drawString(MARGIN_LEFT, y - 10, f"Type {type_.number} — {ak_title}")
        y -= 14

        # Answer rows. For `table` layout, the format is "body -> answer"
        # (e.g., "78, 69, 60, 51, 42, ... -> Arithmetic (d = -9)") instead of
        # "label  answer". Otherwise the label is the row anchor.
        c.setFillColor(BLACK)
        for problem in type_.problems:
            x_label = MARGIN_LEFT + ANSWER_KEY_INDENT
            c.setFont("Helvetica", 8.5)
            if type_.layout == "table":
                # body + " -> " + answer, drawn through exponent parser
                line = f"{problem.body} -> {problem.answer}"
                _draw_text_with_exponents(c, x_label, y - 9, line, "Helvetica", 8.5)
            else:
                c.drawString(x_label, y - 9, problem.label)
                label_w = c.stringWidth(problem.label, "Helvetica", 8.5)
                _draw_text_with_exponents(
                    c, x_label + label_w + 8, y - 9, problem.answer, "Helvetica", 8.5
                )
            y -= ANSWER_LINE_H

        y -= ANSWER_TYPE_GAP


def _start_answer_key_page(c, worksheet: Worksheet, continued: bool) -> float:
    y = PAGE_H - MARGIN_TOP
    y = _draw_page_header(c, worksheet.title, y)
    y -= 6
    label = "Answer Key (continued)" if continued else "Answer Key"
    y = _draw_answer_key_header(c, y, label)
    y -= 8
    return y


def _draw_answer_key_header(c, y: float, text: str) -> float:
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


def _draw_text_with_exponents(c, x: float, y: float, text: str, font: str, size: float) -> float:
    """Draw `text` at (x, y) interpreting `^N` and `^{...}` as superscripts."""
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
