"""Generate the LinkedIn social graphic for the Round Two announcement post.

Output: brand/social/round-two-linkedin.png  (1200x627, LinkedIn link card spec)

Composition: glacier wash background, centered brand lockup (mark + DM Sans
wordmark), tagline below. Brand-faithful — uses the same color tokens as the
app and the same DM Sans weights.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

W, H = 1200, 627

GLACIER = (124, 192, 184)
CHARCOAL = (11, 18, 32)
MUTED = (71, 85, 105)
WHITE = (255, 255, 255)

DMSANS_BOLD = "/tmp/fonts/DMSans-Bold.ttf"
DMSANS_REGULAR = "/tmp/fonts/DMSans-Regular.ttf"

OUT = Path(__file__).parent / "round-two-linkedin.png"


# ---------------------------------------------------------------------------
# Background — glacier wash (white at top, glacier ~12% at bottom)
# ---------------------------------------------------------------------------

def render_background() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = overlay.load()
    for y in range(H):
        # 0 alpha at top, ~30/255 (~12%) at bottom; ease quadratic for a softer wash.
        t = y / H
        alpha = int(30 * (t * t))
        for x in range(W):
            px[x, y] = (*GLACIER, alpha)
    img.paste(overlay, (0, 0), overlay)
    return img


# ---------------------------------------------------------------------------
# Brand mark — glacier checkmark with charcoal dot at the upstroke tip
# ---------------------------------------------------------------------------

def draw_mark(img: Image.Image, cx: int, cy: int, size: int) -> None:
    """Draw the brand mark centered at (cx, cy) at `size` px tall.

    Mirrors brand/mark.svg: viewBox 64x64, path M 16 34 L 27 46 L 50 18 with
    stroke width 10 and round caps, plus a charcoal circle r=4.5 at (50, 18).
    """
    draw = ImageDraw.Draw(img, "RGBA")
    s = size / 64  # scale factor

    def pt(x, y):
        return (cx - size // 2 + int(x * s), cy - size // 2 + int(y * s))

    p1 = pt(16, 34)
    p2 = pt(27, 46)
    p3 = pt(50, 18)
    stroke_w = max(2, int(10 * s))

    # Two segments with round joins. Pillow's line() doesn't support round
    # caps natively in older versions, so we draw the segments and stamp
    # circles at each endpoint to round them off.
    draw.line([p1, p2], fill=GLACIER, width=stroke_w)
    draw.line([p2, p3], fill=GLACIER, width=stroke_w)
    for cx_, cy_ in (p1, p2, p3):
        r = stroke_w // 2
        draw.ellipse((cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill=GLACIER)

    # Charcoal dot at the upstroke tip (signature element).
    dot_r = max(3, int(4.5 * s))
    draw.ellipse((p3[0] - dot_r, p3[1] - dot_r, p3[0] + dot_r, p3[1] + dot_r),
                 fill=CHARCOAL)


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def main() -> None:
    img = render_background()
    draw = ImageDraw.Draw(img)

    # Lockup: mark on the left, "Round Two" wordmark to its right. Sized so
    # the combined unit reads as the dominant element on the card.
    # Per brand/wordmark.svg the wordmark uses mixed weights — "Round" at
    # Regular (400), "Two" at Bold (700) — so we measure and draw each part
    # separately to preserve that weight contrast.
    mark_size = 156
    wm_regular = ImageFont.truetype(DMSANS_REGULAR, 116)
    wm_bold = ImageFont.truetype(DMSANS_BOLD, 116)
    word_a = "Round"
    word_b = " Two"

    a_bbox = draw.textbbox((0, 0), word_a, font=wm_regular)
    b_bbox = draw.textbbox((0, 0), word_b, font=wm_bold)
    a_w = a_bbox[2] - a_bbox[0]
    b_w = b_bbox[2] - b_bbox[0]
    wm_w = a_w + b_w
    wm_h = max(a_bbox[3] - a_bbox[1], b_bbox[3] - b_bbox[1])
    wm_top = min(a_bbox[1], b_bbox[1])

    gap = 14  # tight pixel gap between mark and wordmark
    lockup_w = mark_size + gap + wm_w

    # Position lockup horizontally centered, slightly above vertical center.
    lockup_cx = W // 2
    lockup_cy = int(H * 0.42)

    mark_cx = lockup_cx - lockup_w // 2 + mark_size // 2
    mark_cy = lockup_cy
    draw_mark(img, mark_cx, mark_cy, mark_size)

    # Wordmark — vertical-center the optical baseline against the mark.
    wm_x = lockup_cx - lockup_w // 2 + mark_size + gap
    wm_y = lockup_cy - wm_h // 2 - wm_top
    draw.text((wm_x, wm_y), word_a, font=wm_regular, fill=CHARCOAL)
    draw.text((wm_x + a_w, wm_y), word_b, font=wm_bold, fill=CHARCOAL)

    # Tagline below the lockup.
    tag_top_font = ImageFont.truetype(DMSANS_REGULAR, 36)
    tag_bottom_font = ImageFont.truetype(DMSANS_BOLD, 36)
    tag_top = "Practice worksheets in under a minute."
    tag_bottom = "Math you can trust."

    tag_y = lockup_cy + mark_size // 2 + 56

    tt_bbox = draw.textbbox((0, 0), tag_top, font=tag_top_font)
    tt_w = tt_bbox[2] - tt_bbox[0]
    draw.text(((W - tt_w) // 2, tag_y), tag_top, font=tag_top_font, fill=MUTED)

    tb_bbox = draw.textbbox((0, 0), tag_bottom, font=tag_bottom_font)
    tb_w = tb_bbox[2] - tb_bbox[0]
    draw.text(((W - tb_w) // 2, tag_y + 50), tag_bottom,
              font=tag_bottom_font, fill=GLACIER)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}  ({W}x{H})")


if __name__ == "__main__":
    main()
