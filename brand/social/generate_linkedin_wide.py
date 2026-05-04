"""Second LinkedIn social graphic — wide-lockup variant.

Output: brand/social/round-two-linkedin-wide.png  (1200x627)

Composition:
  - Brand lockup centered horizontally
  - Single-row tagline below, sized so its rendered width matches the
    lockup width exactly. Two charcoal sentences + a glacier
    "Math you can trust." (matching the app's hero accent color).
  - Glacier-wash background flowing top-down (same as the primary
    variant for brand consistency).
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
WHITE = (255, 255, 255)

DMSANS_BOLD = "/tmp/fonts/DMSans-Bold.ttf"
DMSANS_REGULAR = "/tmp/fonts/DMSans-Regular.ttf"

OUT = Path(__file__).parent / "round-two-linkedin-wide.png"


# ---------------------------------------------------------------------------
# Background — same glacier wash as the primary variant
# ---------------------------------------------------------------------------

def render_background() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = overlay.load()
    max_alpha = 110
    for y in range(H):
        t = y / H
        alpha = int(max_alpha * (1 - t) * (1 - t))
        for x in range(W):
            px[x, y] = (*GLACIER, alpha)
    img.paste(overlay, (0, 0), overlay)
    return img


# ---------------------------------------------------------------------------
# Brand mark
# ---------------------------------------------------------------------------

def draw_mark(img: Image.Image, cx: int, cy: int, size: int) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    s = size / 64

    def pt(x, y):
        return (cx - size // 2 + int(x * s), cy - size // 2 + int(y * s))

    p1 = pt(16, 34)
    p2 = pt(27, 46)
    p3 = pt(50, 18)
    stroke_w = max(2, int(10 * s))

    draw.line([p1, p2], fill=GLACIER, width=stroke_w)
    draw.line([p2, p3], fill=GLACIER, width=stroke_w)
    for cx_, cy_ in (p1, p2, p3):
        r = stroke_w // 2
        draw.ellipse((cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill=GLACIER)

    dot_r = max(3, int(4.5 * s))
    draw.ellipse((p3[0] - dot_r, p3[1] - dot_r, p3[0] + dot_r, p3[1] + dot_r),
                 fill=CHARCOAL)


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def main() -> None:
    img = render_background()
    draw = ImageDraw.Draw(img)

    # Lockup sizing — slightly wider than the original 60% target so the
    # tagline at a comfortable read size can match it exactly. With these
    # sizes the lockup lands at ~800 px, leaving the tagline at ~30 px
    # font (highly readable on LinkedIn).
    mark_size = 144
    wordmark_size = 124
    gap = 22

    wm_regular = ImageFont.truetype(DMSANS_REGULAR, wordmark_size)
    wm_bold = ImageFont.truetype(DMSANS_BOLD, wordmark_size)
    word_a, word_b = "Round", " Two"
    a_bbox = draw.textbbox((0, 0), word_a, font=wm_regular)
    b_bbox = draw.textbbox((0, 0), word_b, font=wm_bold)
    a_w = a_bbox[2] - a_bbox[0]
    b_w = b_bbox[2] - b_bbox[0]
    wm_h = max(a_bbox[3] - a_bbox[1], b_bbox[3] - b_bbox[1])
    wm_top = min(a_bbox[1], b_bbox[1])
    lockup_w = mark_size + gap + a_w + b_w

    # Single-row tagline, three sentences with consistent generous spacing
    # between them. Last sentence in glacier as the visual hook (matches
    # the app's hero accent color).
    SEP = "   "  # three spaces between sentences for breathing room
    sentences = [
        ("Test in the morning." + SEP, CHARCOAL),
        ("Practice after lunch." + SEP, CHARCOAL),
        ("Math you can trust.", GLACIER),
    ]
    full_text = "".join(s for s, _ in sentences)

    # Pick a tagline font size whose rendered width matches the lockup
    # width as closely as possible. Linear scaling from a base measurement
    # is accurate enough for a target match within a couple of pixels.
    base_size = 40
    base_font = ImageFont.truetype(DMSANS_BOLD, base_size)
    base_bbox = draw.textbbox((0, 0), full_text, font=base_font)
    base_w = base_bbox[2] - base_bbox[0]
    tagline_size = max(20, int(round(base_size * lockup_w / base_w)))

    tagline_font = ImageFont.truetype(DMSANS_BOLD, tagline_size)
    tag_bbox = draw.textbbox((0, 0), full_text, font=tagline_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_h = tag_bbox[3] - tag_bbox[1]
    tag_top = tag_bbox[1]

    # Vertical layout: lockup + breathing room + tagline, vertically centered.
    breathing = 70
    total_h = mark_size + breathing + tag_h
    content_top = (H - total_h) // 2

    # Center lockup and tagline horizontally on the canvas (both share the
    # same width by construction, so they align cleanly).
    lockup_left = (W - lockup_w) // 2
    lockup_cy = content_top + mark_size // 2

    mark_cx = lockup_left + mark_size // 2
    draw_mark(img, mark_cx, lockup_cy, mark_size)

    wm_x = lockup_left + mark_size + gap
    wm_y = lockup_cy - wm_h // 2 - wm_top
    draw.text((wm_x, wm_y), word_a, font=wm_regular, fill=CHARCOAL)
    draw.text((wm_x + a_w, wm_y), word_b, font=wm_bold, fill=CHARCOAL)

    # Render each tagline sentence with its own color, accumulating x.
    tag_x = (W - tag_w) // 2
    tag_y = content_top + mark_size + breathing - tag_top
    cursor_x = tag_x
    for sentence, color in sentences:
        draw.text((cursor_x, tag_y), sentence, font=tagline_font, fill=color)
        bbox = draw.textbbox((cursor_x, tag_y), sentence, font=tagline_font)
        cursor_x = bbox[2]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}  ({W}x{H})  lockup_w={lockup_w}  "
          f"tagline_w={tag_w}  tagline_size={tagline_size}px  "
          f"width_diff={tag_w - lockup_w:+d}px")


if __name__ == "__main__":
    main()
