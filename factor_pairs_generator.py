"""Standalone generator for a 'Factor Pairs from 1 - 100' reference sheet.

Differences from the commercial original this was modeled on:
  - In every factor pair the LARGER factor is written first (e.g. 6 . 2, 4 . 3).
  - Perfect-square numbers bold their header and bold+box the equal-factor
    equation (e.g. 6 . 6 for 36).
  - Clean styling: no extra highlight boxes, no gray shading.
  - 50 numbers per page: 1-50 on page one, 51-100 on page two.

Run:  python factor_pairs_generator.py
Out:  factor_pairs_1-100.pdf
"""

from __future__ import annotations

import math

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as canvas_module

PAGE_W, PAGE_H = letter  # 612 x 792 pt

MARGIN = 36
N_COLS = 10
PER_PAGE = 50           # 5 rows of 10
ROWS_PER_PAGE = PER_PAGE // N_COLS

COL_W = (PAGE_W - 2 * MARGIN) / N_COLS

HEADER_SIZE = 10
PAIR_SIZE = 9.5
LINE_H = 13
CELL_PAD_TOP = 7
CELL_PAD_BOTTOM = 7

TITLE = "Factor Pairs from 1 – 100"
SUBTITLE = "with the larger factor first · perfect squares in bold"


def is_perfect_square(n: int) -> bool:
    r = int(math.isqrt(n))
    return r * r == n


def factor_pairs_larger_first(n: int) -> list[tuple[int, int, bool]]:
    """Return (big, small, is_square_pair) for each factor pair a*b = n with
    a <= b, ordered by the smaller factor ascending (larger factor first in
    the displayed equation). is_square_pair flags the a == b pair."""
    pairs = []
    a = 1
    while a * a <= n:
        if n % a == 0:
            b = n // a
            pairs.append((b, a, a == b))
        a += 1
    return pairs


def row_heights(numbers: list[int]) -> list[float]:
    """Height of each grid row, sized to the busiest cell in that row so the
    layout stays tight like the original (a prime's row is short; a row with
    a highly composite number is tall)."""
    heights = []
    for r in range(ROWS_PER_PAGE):
        row_nums = numbers[r * N_COLS:(r + 1) * N_COLS]
        max_lines = max(1 + len(factor_pairs_larger_first(n)) for n in row_nums)
        heights.append(max_lines * LINE_H + CELL_PAD_TOP + CELL_PAD_BOTTOM)
    return heights


def draw_cell(c, x_left: float, y_top: float, width: float, height: float, n: int) -> None:
    # Cell border.
    c.setLineWidth(0.6)
    c.setStrokeColorRGB(0.15, 0.15, 0.15)
    c.rect(x_left, y_top - height, width, height, stroke=1, fill=0)

    cx = x_left + width / 2
    is_sq = is_perfect_square(n)

    # Header number (underlined; bold for perfect squares).
    head_font = "Helvetica-Bold" if is_sq else "Helvetica"
    c.setFont(head_font, HEADER_SIZE)
    c.setFillColorRGB(0, 0, 0)
    head_y = y_top - CELL_PAD_TOP - HEADER_SIZE
    c.drawCentredString(cx, head_y, str(n))
    num_w = c.stringWidth(str(n), head_font, HEADER_SIZE)
    c.setLineWidth(0.8)
    c.line(cx - num_w / 2, head_y - 1.5, cx + num_w / 2, head_y - 1.5)

    # Factor-pair equations, larger factor first.
    line_y = head_y - LINE_H
    for big, small, square_pair in factor_pairs_larger_first(n):
        text = f"{big} · {small}"
        if square_pair:
            c.setFont("Helvetica-Bold", PAIR_SIZE)
            tw = c.stringWidth(text, "Helvetica-Bold", PAIR_SIZE)
            c.drawCentredString(cx, line_y, text)
            # Box the perfect-square equation.
            pad_x, pad_y = 4, 2.5
            c.setLineWidth(1.0)
            c.rect(cx - tw / 2 - pad_x, line_y - pad_y,
                   tw + 2 * pad_x, PAIR_SIZE + 2 * pad_y, stroke=1, fill=0)
        else:
            c.setFont("Helvetica", PAIR_SIZE)
            c.drawCentredString(cx, line_y, text)
        line_y -= LINE_H


def draw_page(c, numbers: list[int], page_label: str) -> None:
    # Title block.
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Times-Bold", 19)
    title_y = PAGE_H - MARGIN - 14
    c.drawCentredString(PAGE_W / 2, title_y, TITLE)
    c.setFont("Times-Italic", 11)
    c.drawCentredString(PAGE_W / 2, title_y - 16, SUBTITLE)

    grid_top = title_y - 30
    grid_bottom = MARGIN + 14
    available = grid_top - grid_bottom

    heights = row_heights(numbers)
    total_h = sum(heights)
    # Expand rows to fill the page so the sheet doesn't float in the middle
    # (cells gain breathing room at the bottom, like the original).
    if available > total_h:
        spread = (available - total_h) / ROWS_PER_PAGE
        heights = [h + spread for h in heights]

    y = grid_top
    for r in range(ROWS_PER_PAGE):
        row_h = heights[r]
        for col in range(N_COLS):
            n = numbers[r * N_COLS + col]
            x_left = MARGIN + col * COL_W
            draw_cell(c, x_left, y, COL_W, row_h, n)
        y -= row_h

    # Footer.
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.45, 0.45, 0.45)
    c.drawRightString(PAGE_W - MARGIN, MARGIN - 2, page_label)


def main(out_path: str = "factor_pairs_1-100.pdf") -> None:
    c = canvas_module.Canvas(out_path, pagesize=letter)
    draw_page(c, list(range(1, 51)), "page 1 of 2  ·  numbers 1–50")
    c.showPage()
    draw_page(c, list(range(51, 101)), "page 2 of 2  ·  numbers 51–100")
    c.showPage()
    c.save()
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
