"""Graphic organizer: Solving Quadratic Equations with the Quadratic Formula.

Rebuilds a teacher's handwritten worked-example page (x^2 - x - 6 = 0) as a
clean, printable graphic organizer: a numbered step flow down the left, a
factoring-check callout and reminder box on the right, and a solutions banner.

Math is rendered with matplotlib mathtext (no LaTeX install needed).

Run:  python graphic_organizer_quadratic.py
Out:  quadratic_formula_organizer.pdf
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

NAVY = "#1B2B5E"
ORANGE = "#E2580B"
SLATE = "#4A4A4A"
STEP_FILL = "#F4F4F2"
FORMULA_FILL = "#FFF1E2"
CHECK_FILL = "#EAF3F1"
CHECK_EDGE = "#2F7E73"
REMEMBER_FILL = "#FDF6E3"
REMEMBER_EDGE = "#C9A227"
BORDER = "#D8D8D4"

# (instruction, math, math_fontsize, highlight_as_formula)
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


def rounded_box(ax, x, y, w, h, facecolor, edgecolor, lw=1.0):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.004,rounding_size=0.012",
        linewidth=lw, facecolor=facecolor, edgecolor=edgecolor, zorder=2,
    )
    ax.add_patch(box)


def main(out_path: str = "quadratic_formula_organizer.pdf") -> None:
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # --- Header ---
    ax.text(0.5, 0.962, "Solving Quadratics with the Quadratic Formula",
            ha="center", va="center", fontsize=19, fontweight="bold", color=NAVY)
    ax.text(0.5, 0.934,
            "Step-by-step graphic organizer   •   worked example:  $x^2 - x - 6 = 0$",
            ha="center", va="center", fontsize=11, color=SLATE, style="italic")
    ax.plot([0.045, 0.955], [0.915, 0.915], color=NAVY, lw=1.4)

    # --- Left column: step flow ---
    x_L, col_w = 0.045, 0.595
    top_start, region_bottom = 0.888, 0.150
    pitch = (top_start - region_bottom) / len(STEPS)
    box_h = pitch - 0.020
    cx = x_L + col_w / 2

    prev_bottom = None
    for i, (instr, math, msize, is_formula) in enumerate(STEPS):
        box_top = top_start - i * pitch
        box_bottom = box_top - box_h

        # Arrow from previous box.
        if prev_bottom is not None:
            ax.annotate("", xy=(cx, box_top), xytext=(cx, prev_bottom),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6),
                        zorder=1)

        fill = FORMULA_FILL if is_formula else STEP_FILL
        edge = ORANGE if is_formula else BORDER
        rounded_box(ax, x_L, box_bottom, col_w, box_h, fill, edge,
                    lw=1.6 if is_formula else 1.0)

        # Step-number badge.
        bx, by = x_L + 0.028, box_top - 0.022
        ax.scatter([bx], [by], s=300, color=ORANGE, zorder=5, edgecolors="none")
        ax.text(bx, by, str(i + 1), color="white", ha="center", va="center",
                fontsize=11, fontweight="bold", zorder=6)

        # Instruction + math.
        ax.text(x_L + 0.058, box_top - 0.022, instr, ha="left", va="center",
                fontsize=10, fontweight="bold", color=NAVY, zorder=6)
        ax.text(cx + 0.018, box_bottom + box_h * 0.34, math, ha="center", va="center",
                fontsize=msize, color="#111111", zorder=6)

        prev_bottom = box_bottom

    # --- Right column callouts ---
    x_R, col_wR = 0.665, 0.290
    cxR = x_R + col_wR / 2

    # Check by factoring.
    ck_top, ck_h = 0.888, 0.300
    rounded_box(ax, x_R, ck_top - ck_h, col_wR, ck_h, CHECK_FILL, CHECK_EDGE, lw=1.4)
    ax.text(cxR, ck_top - 0.030, "✓  Check by Factoring", ha="center", va="center",
            fontsize=11.5, fontweight="bold", color=CHECK_EDGE)
    ax.text(cxR, ck_top - 0.085, r"$(x - 3)(x + 2) = 0$", ha="center", va="center",
            fontsize=13, color="#111111")
    ax.text(cxR, ck_top - 0.150, r"$x - 3 = 0 \;\Rightarrow\; x = 3$",
            ha="center", va="center", fontsize=12, color="#111111")
    ax.text(cxR, ck_top - 0.205, r"$x + 2 = 0 \;\Rightarrow\; x = -2$",
            ha="center", va="center", fontsize=12, color="#111111")
    ax.text(cxR, ck_top - 0.262, "Same answers — it checks!", ha="center", va="center",
            fontsize=9.5, style="italic", color=SLATE)

    # Remember box.
    rm_top, rm_h = 0.575, 0.330
    rounded_box(ax, x_R, rm_top - rm_h, col_wR, rm_h, REMEMBER_FILL, REMEMBER_EDGE, lw=1.4)
    ax.text(cxR, rm_top - 0.030, "★  Remember", ha="center", va="center",
            fontsize=11.5, fontweight="bold", color="#9A7B0A")
    tips = [
        "Set it $= 0$ before you start.",
        "Keep parentheses when you\n   substitute — watch negatives.",
        "Look for a perfect square\n   under the radical.",
        "Not a perfect square? The\n   answer is irrational — leave\n   it in exact (radical) form.",
    ]
    ty, line_h, gap = rm_top - 0.072, 0.026, 0.013
    for tip in tips:
        ax.text(x_R + 0.022, ty, "•", ha="left", va="top", fontsize=11,
                color="#9A7B0A", fontweight="bold")
        ax.text(x_R + 0.042, ty, tip, ha="left", va="top", fontsize=9.0,
                color="#3A3A3A", linespacing=1.4)
        ty -= line_h * (tip.count("\n") + 1) + gap

    # --- Solutions banner ---
    rounded_box(ax, 0.045, 0.050, 0.910, 0.072, ORANGE, ORANGE)
    ax.text(0.5, 0.086, "Solutions", ha="center", va="center",
            fontsize=11, color="#FFE2CC", fontweight="bold")
    ax.text(0.5, 0.066, r"$x = 3 \qquad \mathrm{or} \qquad x = -2$",
            ha="center", va="center", fontsize=17, color="white", fontweight="bold")

    fig.savefig(out_path)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
