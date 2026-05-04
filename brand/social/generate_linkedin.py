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
# Background — glacier wash flowing top down (saturated at top, white at bottom)
# ---------------------------------------------------------------------------

def render_background() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = overlay.load()
    # Top of the card sits at ~43% glacier alpha and tapers to 0 at the
    # bottom on a quadratic ease-out — the saturation collapses fast in
    # the upper third so the tagline area lands on near-white for legibility.
    max_alpha = 110
    for y in range(H):
        t = y / H
        alpha = int(max_alpha * (1 - t) * (1 - t))
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

    # Position lockup horizontally centered. Three-line tagline below
    # needs more room than a two-line one, so push the lockup higher.
    lockup_cx = W // 2
    lockup_cy = int(H * 0.34)

    mark_cx = lockup_cx - lockup_w // 2 + mark_size // 2
    mark_cy = lockup_cy
    draw_mark(img, mark_cx, mark_cy, mark_size)

    # Wordmark — vertical-center the optical baseline against the mark.
    wm_x = lockup_cx - lockup_w // 2 + mark_size + gap
    wm_y = lockup_cy - wm_h // 2 - wm_top
    draw.text((wm_x, wm_y), word_a, font=wm_regular, fill=CHARCOAL)
    draw.text((wm_x + a_w, wm_y), word_b, font=wm_bold, fill=CHARCOAL)

    # Three-line tagline below the lockup. Same copy as the app's hero
    # headline so the social card primes recognition. First two lines in
    # charcoal-muted regular, third in glacier bold as the visual hook.
    tag_regular = ImageFont.truetype(DMSANS_REGULAR, 44)
    tag_bold = ImageFont.truetype(DMSANS_BOLD, 44)
    lines = [
        ("Test in the morning.", tag_regular, MUTED),
        ("Practice after lunch.", tag_regular, MUTED),
        ("Math you can trust.", tag_bold, GLACIER),
    ]

    tag_y = lockup_cy + mark_size // 2 + 56
    line_h = 60
    for i, (text, font, color) in enumerate(lines):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((W - w) // 2, tag_y + i * line_h), text, font=font, fill=color)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}  ({W}x{H})")


if __name__ == "__main__":
    main()
