"""Generate the LinkedIn social graphic for the Round Two announcement post.

Output: brand/social/round-two-linkedin.png  (1200x627, LinkedIn link card spec)

Composition:
  - Three-line tagline in heavy DM Sans Bold ("Test in the morning. /
    Practice after lunch. / Math you can trust.") with the last line
    in glacier — same weight as the app's hero headline.
  - Brand lockup above, sized to ~50% of the tagline block's width,
    right-justified so its right edge aligns with the tagline's right
    edge, with breathing room between it and the first tagline line.
  - Glacier-wash background flowing top-down (saturated at top,
    fading to white).
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

OUT = Path(__file__).parent / "round-two-linkedin.png"


# ---------------------------------------------------------------------------
# Background — glacier wash flowing top down
# ---------------------------------------------------------------------------

def render_background() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = overlay.load()
    max_alpha = 110  # ~43% glacier at the very top
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
    """Draw the brand mark centered at (cx, cy) at `size` px tall."""
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

    # 1. Render the three-line tagline first to learn its block width and
    #    height. Same weight as the app's hero headline (DM Sans Bold) so
    #    the social card primes recognition. Last line in glacier.
    tag_size = 84
    tag_font = ImageFont.truetype(DMSANS_BOLD, tag_size)
    line_gap = 16  # extra leading between tagline lines
    lines = [
        ("Test in the morning.", CHARCOAL),
        ("Practice after lunch.", CHARCOAL),
        ("Math you can trust.", GLACIER),
    ]

    measured = []
    for text, color in lines:
        bbox = draw.textbbox((0, 0), text, font=tag_font)
        measured.append({
            "text": text,
            "color": color,
            "w": bbox[2] - bbox[0],
            "h": bbox[3] - bbox[1],
            "top": bbox[1],
            "ascent_to_baseline": bbox[3],
        })

    line_h = tag_size + line_gap
    tag_block_w = max(m["w"] for m in measured)
    tag_block_h = line_h * (len(lines) - 1) + measured[-1]["h"]

    # 2. Lockup target width = 50% of tagline block width. Pick a wordmark
    #    font size and mark size that combine to approximately that width,
    #    then right-justify the actual rendered lockup to the tagline's
    #    right edge (so it lines up cleanly even if the rendered width is
    #    a few px off the 50% target).
    lockup_target_w = tag_block_w // 2

    # Tune these to land near 50% of tagline_w. With tagline at 84px Bold
    # the longest line is ~770 px → target lockup ~385 px → mark ~74 px +
    # wordmark Regular/Bold at ~58 px font lands close.
    mark_size = 78
    wordmark_size = 60
    wm_regular = ImageFont.truetype(DMSANS_REGULAR, wordmark_size)
    wm_bold = ImageFont.truetype(DMSANS_BOLD, wordmark_size)
    word_a, word_b = "Round", " Two"
    a_bbox = draw.textbbox((0, 0), word_a, font=wm_regular)
    b_bbox = draw.textbbox((0, 0), word_b, font=wm_bold)
    a_w = a_bbox[2] - a_bbox[0]
    b_w = b_bbox[2] - b_bbox[0]
    wm_w = a_w + b_w
    wm_h = max(a_bbox[3] - a_bbox[1], b_bbox[3] - b_bbox[1])
    wm_top = min(a_bbox[1], b_bbox[1])
    gap = 12  # tight mark→wordmark gap so they read as one element
    lockup_w = mark_size + gap + wm_w

    # Vertical composition: total content height = lockup_size + breathing
    # room + tagline_block_h. Vertically center the whole stack on canvas.
    breathing = 56  # space between lockup bottom and first tagline line top
    total_h = mark_size + breathing + tag_block_h
    content_top = (H - total_h) // 2

    # 3. Position tagline block: left edge centered horizontally on canvas
    #    (so the whole composition reads as a single centered group).
    tag_left = (W - tag_block_w) // 2
    tag_right = tag_left + tag_block_w
    tag_top = content_top + mark_size + breathing

    # 4. Position lockup: right edge aligns with tagline right edge.
    lockup_right = tag_right
    lockup_left = lockup_right - lockup_w
    lockup_cy = content_top + mark_size // 2

    mark_cx = lockup_left + mark_size // 2
    draw_mark(img, mark_cx, lockup_cy, mark_size)

    wm_x = lockup_left + mark_size + gap
    wm_y = lockup_cy - wm_h // 2 - wm_top
    draw.text((wm_x, wm_y), word_a, font=wm_regular, fill=CHARCOAL)
    draw.text((wm_x + a_w, wm_y), word_b, font=wm_bold, fill=CHARCOAL)

    # 5. Draw the tagline lines, all sharing the same left edge.
    for i, m in enumerate(measured):
        y = tag_top + i * line_h - m["top"]
        draw.text((tag_left, y), m["text"], font=tag_font, fill=m["color"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT}  ({W}x{H})  lockup_w={lockup_w}  tagline_w={tag_block_w}  "
          f"ratio={lockup_w / tag_block_w:.2f}")


if __name__ == "__main__":
    main()
