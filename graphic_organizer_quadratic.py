"""Graphic organizers: Solving Quadratic Equations with the Quadratic Formula.

Builds a matched pair of printable, top-shelf graphic organizers from a
teacher's handwritten worked-example page (x^2 - x - 6 = 0):

  quadratic_formula_organizer.pdf         completed anchor / reference
  quadratic_formula_organizer_blank.pdf   "Your Turn" fill-in scaffold

Both share one layout engine so they read as a set. Math is rendered with
matplotlib mathtext (no LaTeX install needed).

Run:  python graphic_organizer_quadratic.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# --- Palette (cohesive: indigo primary, warm orange accent, semantic green) ---
INK = "#1E2742"        # body text
INDIGO = "#2B3A72"     # primary / headings / card left-edge
ORANGE = "#E26A18"     # accent: badges, formula, solutions
GREEN = "#2E7D5B"      # check (semantic "correct")
GREEN_FILL = "#E9F3EE"
AMBER = "#C2901C"      # remember
AMBER_FILL = "#FCF5E2"
AMBER_INK = "#8C6410"
CARD_FILL = "#F3F3EF"
CARD_EDGE = "#E2E2DC"
FORMULA_FILL = "#FFF1E2"
WRITE_EDGE = "#CFCFC8"        # faint rules (Name/Date lines)
WRITE_BOX_EDGE = "#B7B7AE"   # writing boxes — clearly visible on cards
MUTED = "#5A5A5A"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "dejavusans"

# (instruction, math, math_fontsize, is_formula)
STEPS = [
    ("Set the equation equal to 0", r"$x^2 - x - 6 = 0$", 14, False),
    ("Identify  $a$,  $b$,  and  $c$", r"$a = 1 \qquad b = -1 \qquad c = -6$", 13, False),
    ("Write the quadratic formula", r"$x = \frac{-b \pm \sqrt{\,b^2 - 4ac\,}}{2a}$", 15, True),
    ("Substitute  $a$, $b$, $c$  — keep the parentheses!",
     r"$x = \frac{-(-1) \pm \sqrt{\,(-1)^2 - 4(1)(-6)\,}}{2(1)}$", 12, False),
    ("Simplify under the radical",
     r"$x = \frac{1 \pm \sqrt{\,1 + 24\,}}{2} = \frac{1 \pm \sqrt{25}}{2}$", 13, False),
    ("Take the square root  (look for a perfect square)",
     r"$x = \frac{1 \pm 5}{2}$", 14, False),
    ("Split into two equations",
     r"$x = \frac{1 + 5}{2} \qquad x = \frac{1 - 5}{2}$", 13, False),
    ("Simplify each", r"$x = 3 \qquad\quad x = -2$", 14, False),
]


def card(ax, x, y, w, h, fill, edge, accent, lw=1.0):
    """A rounded card with a colored left edge (accent bar peeking out)."""
    sliver = 0.009
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.013",
        linewidth=0, facecolor=accent, zorder=2))
    ax.add_patch(FancyBboxPatch(
        (x + sliver, y), w - sliver, h,
        boxstyle="round,pad=0.004,rounding_size=0.012",
        linewidth=lw, facecolor=fill, edgecolor=edge, zorder=3))


def plain_card(ax, x, y, w, h, fill, edge, lw=1.2, zorder=2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.013",
        linewidth=lw, facecolor=fill, edgecolor=edge, zorder=zorder))


def write_line(ax, x0, x1, y, color, lw=2.0):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="round", zorder=6)


def build(mode: str, out_path: str) -> None:
    solved = mode == "solved"
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # --- Header ---
    ax.text(0.5, 0.975, "A L G E B R A   ·   Q U A D R A T I C   E Q U A T I O N S",
            ha="center", va="center", fontsize=8.5, color=ORANGE, fontweight="bold")
    ax.text(0.5, 0.949, "Solving with the Quadratic Formula",
            ha="center", va="center", fontsize=21, fontweight="bold", color=INDIGO)
    sub = (r"Step-by-step worked example:   $x^2 - x - 6 = 0$" if solved
           else "Your Turn — solve a quadratic, one step at a time")
    ax.text(0.5, 0.924, sub, ha="center", va="center", fontsize=11,
            color=MUTED, style="italic")

    rule_y = 0.905
    if not solved:
        rule_y = 0.882
        ax.text(0.045, 0.902, "Name", ha="left", va="center", fontsize=10, color=INK)
        write_line(ax, 0.105, 0.42, 0.898, WRITE_EDGE, 1.2)
        ax.text(0.52, 0.902, "Date", ha="left", va="center", fontsize=10, color=INK)
        write_line(ax, 0.575, 0.74, 0.898, WRITE_EDGE, 1.2)
        ax.text(0.79, 0.902, "Period", ha="left", va="center", fontsize=10, color=INK)
        write_line(ax, 0.86, 0.955, 0.898, WRITE_EDGE, 1.2)
    ax.plot([0.045, 0.955], [rule_y, rule_y], color=CARD_EDGE, lw=2, zorder=1)
    ax.plot([0.045, 0.235], [rule_y, rule_y], color=ORANGE, lw=2.6, zorder=1)

    # --- Left column: step flow ---
    x_L, col_w = 0.045, 0.595
    top_start = (rule_y - 0.020)
    region_bottom = 0.150
    pitch = (top_start - region_bottom) / len(STEPS)
    card_h = pitch - 0.020
    cx = x_L + col_w / 2

    prev_bottom = None
    for i, (instr, math, msize, is_formula) in enumerate(STEPS):
        box_top = top_start - i * pitch
        box_bottom = box_top - card_h

        if prev_bottom is not None:
            ax.annotate("", xy=(cx, box_top), xytext=(cx, prev_bottom),
                        arrowprops=dict(arrowstyle="-|>", color=INDIGO, lw=1.6),
                        zorder=1)

        fill = FORMULA_FILL if is_formula else CARD_FILL
        accent = ORANGE if is_formula else INDIGO
        card(ax, x_L, box_bottom, col_w, card_h, fill, CARD_EDGE, accent,
             lw=1.6 if is_formula else 1.0)

        # Number badge (filled circle with soft ring).
        bx, by = x_L + 0.044, box_top - 0.024
        ax.scatter([bx], [by], s=470, color="#FBE2CC", zorder=4, edgecolors="none")
        ax.scatter([bx], [by], s=300, color=ORANGE, zorder=5, edgecolors="none")
        ax.text(bx, by, str(i + 1), color="white", ha="center", va="center",
                fontsize=11, fontweight="bold", zorder=6)

        ax.text(x_L + 0.072, box_top - 0.024, instr, ha="left", va="center",
                fontsize=10, fontweight="bold", color=INDIGO, zorder=6)

        math_y = box_bottom + card_h * 0.36
        if solved or is_formula:
            ax.text(cx + 0.018, math_y, math, ha="center", va="center",
                    fontsize=msize, color=INK, zorder=6)
        else:
            # Generous, clearly-bordered writing area for the student.
            wx0, wx1 = x_L + 0.066, x_L + col_w - 0.028
            wy0, wy1 = box_bottom + 0.009, box_top - 0.040
            plain_card(ax, wx0, wy0, wx1 - wx0, wy1 - wy0,
                       "white", WRITE_BOX_EDGE, lw=1.1, zorder=5)

        prev_bottom = box_bottom

    # --- Right column ---
    x_R, col_wR = 0.665, 0.290
    cxR = x_R + col_wR / 2

    # Check box (semantic green).
    ck_top, ck_h = top_start, 0.300
    plain_card(ax, x_R, ck_top - ck_h, col_wR, ck_h, GREEN_FILL, GREEN, lw=1.4)
    title = "✓  Check by Factoring" if solved else "✓  Check Your Answer"
    ax.text(cxR, ck_top - 0.030, title, ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=GREEN)
    if solved:
        ax.text(cxR, ck_top - 0.090, r"$(x - 3)(x + 2) = 0$", ha="center",
                va="center", fontsize=13, color=INK)
        ax.text(cxR, ck_top - 0.150, r"$x - 3 = 0 \;\Rightarrow\; x = 3$",
                ha="center", va="center", fontsize=12, color=INK)
        ax.text(cxR, ck_top - 0.205, r"$x + 2 = 0 \;\Rightarrow\; x = -2$",
                ha="center", va="center", fontsize=12, color=INK)
        ax.text(cxR, ck_top - 0.262, "Same answers — it checks!", ha="center",
                va="center", fontsize=9.5, style="italic", color=MUTED)
    else:
        ax.text(cxR, ck_top - 0.066, "Factor, or substitute each answer",
                ha="center", va="center", fontsize=9, color=MUTED, style="italic")
        ax.text(cxR, ck_top - 0.090, "back into the original equation.",
                ha="center", va="center", fontsize=9, color=MUTED, style="italic")
        plain_card(ax, x_R + 0.022, ck_top - 0.255, col_wR - 0.044, 0.140,
                   "white", WRITE_BOX_EDGE, lw=1.1)

    # Remember box (amber).
    rm_top, rm_h = 0.575, 0.330
    plain_card(ax, x_R, rm_top - rm_h, col_wR, rm_h, AMBER_FILL, AMBER, lw=1.4)
    ax.text(cxR, rm_top - 0.030, "★  Remember", ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=AMBER_INK)
    tips = [
        "Set it $= 0$ before you start.",
        "Keep parentheses when you\n   substitute — watch negatives.",
        "Look for a perfect square\n   under the radical.",
        "Not a perfect square? The\n   answer is irrational — leave\n   it in exact (radical) form.",
    ]
    ty, line_h, gap = rm_top - 0.072, 0.026, 0.013
    for tip in tips:
        ax.text(x_R + 0.022, ty, "•", ha="left", va="top", fontsize=11,
                color=AMBER_INK, fontweight="bold")
        ax.text(x_R + 0.042, ty, tip, ha="left", va="top", fontsize=9.0,
                color="#3A3A3A", linespacing=1.4)
        ty -= line_h * (tip.count("\n") + 1) + gap

    # --- Solutions banner ---
    plain_card(ax, 0.045, 0.050, 0.910, 0.072, ORANGE, ORANGE)
    ax.text(0.5, 0.100, "SOLUTIONS", ha="center", va="center",
            fontsize=10, color="#FFE2CC", fontweight="bold")
    if solved:
        ax.text(0.5, 0.073, r"$x = 3 \qquad \mathrm{or} \qquad x = -2$",
                ha="center", va="center", fontsize=17, color="white", fontweight="bold")
    else:
        ax.text(0.30, 0.073, r"$x =$", ha="center", va="center", fontsize=17,
                color="white", fontweight="bold")
        write_line(ax, 0.345, 0.45, 0.066, "white", 2.2)
        ax.text(0.50, 0.073, "or", ha="center", va="center", fontsize=13,
                color="#FFE2CC", style="italic")
        ax.text(0.58, 0.073, r"$x =$", ha="center", va="center", fontsize=17,
                color="white", fontweight="bold")
        write_line(ax, 0.625, 0.73, 0.066, "white", 2.2)

    fig.savefig(out_path)
    plt.close(fig)
    print(f"wrote {out_path}")


def main() -> None:
    build("solved", "quadratic_formula_organizer.pdf")
    build("blank", "quadratic_formula_organizer_blank.pdf")


if __name__ == "__main__":
    main()
