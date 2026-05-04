"""Round Two — Streamlit app.

Four-step flow: Upload -> Types -> Problems -> PDF. Each step lives in its
own render function and the state machine is driven by `st.session_state.step`.

  Upload    file_uploader, hash the bytes, show a cost estimate, "Continue"
  Types     cached extract_problem_types call (one Opus invocation per unique
            file hash), preview each extracted type in an expander
  Problems  loop generate_problem_with_retry per (type, A-E) and surface a
            review pane with Approve / Regenerate per problem; flagged
            problems get a ⚠️ badge so the teacher can intervene
  PDF       hand off to worksheet_renderer.render_worksheet and serve the
            result via st.download_button

The theme CSS is injected once at the top so Streamlit's default chrome
reads as Notion-adjacent (Round Two brand). The brand mark+wordmark sits
in the sidebar, with a step-indicator pill list beneath it.

ANTHROPIC_API_KEY must be set in the environment (or in Streamlit Community
Cloud's Secrets UI). Missing key surfaces a friendly inline error.
"""

from __future__ import annotations

import hashlib
import io
import os
import re
from pathlib import Path

import streamlit as st

from problem_generator import (
    ExtractedTypeSpec,
    GeneratedProblem,
    MissingAPIKey,
    estimate_cost,
    extract_problem_types,
    generate_problem_with_retry,
)
from worksheet_renderer import Worksheet, render_worksheet


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

ASSETS_DIR = Path(__file__).parent
BRAND_DIR = ASSETS_DIR / "brand"
THEME_CSS = ASSETS_DIR / "assets" / "theme.css"

def _mark_svg(size: int) -> str:
    """Inline brand mark at an explicit pixel size. Width/height are baked
    into the SVG attributes (not CSS) so the icon renders at the intended
    size even if assets/theme.css fails to load — the live deploy has been
    flaky about CSS sizing of SVG descendants."""
    return (
        f'<svg viewBox="0 0 64 64" width="{size}" height="{size}" '
        'fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M 16 34 L 27 46 L 50 18" stroke="#7CC0B8" stroke-width="10" '
        'stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
        '<circle cx="50" cy="18" r="4.5" fill="#0B1220"/>'
        '</svg>'
    )

# Common sizes pre-rendered for ergonomic use at call sites.
MARK_SVG = _mark_svg(22)        # sidebar
MARK_SVG_LARGE = _mark_svg(32)  # PDF done state

STEP_LABELS = {"upload": "Step 1 of 4", "types": "Step 2 of 4",
               "problems": "Step 3 of 4", "pdf": "Step 4 of 4"}

# Brand color constants used in inline styles. Streamlit's HTML sanitizer
# can drop class attributes on nested divs in some versions, so we lean on
# inline `style="..."` for everything that needs to look right. Keep these
# in sync with assets/theme.css so a future class-based render path could
# still match.
COLOR_GLACIER = "#7CC0B8"
COLOR_CHARCOAL = "#0B1220"
COLOR_MUTED = "#475569"
COLOR_FAINT = "#94A3B8"
COLOR_BORDER = "#E5E5E2"
COLOR_SURFACE = "#FFFFFF"
COLOR_SURFACE_SOFT = "#F7F7F5"
COLOR_WARM = "#F59E0B"
COLOR_WARM_SOFT = "#FEF3C7"
COLOR_ACCENT = "#4338CA"
COLOR_ACCENT_SOFT = "#E0E7FF"

# Shared inline-style fragments. All callers concatenate these with
# any per-element overrides via `; <override>;`.
H1_STYLE = (
    f"font-size:2rem;font-weight:700;letter-spacing:-0.02em;"
    f"color:{COLOR_CHARCOAL};margin:0 0 0.875rem 0;line-height:1.1"
)
LEAD_STYLE = (
    f"font-size:1.0625rem;line-height:1.55;color:{COLOR_MUTED};"
    f"max-width:38rem;margin:0"
)
LEAD_STRONG_STYLE = f"color:{COLOR_CHARCOAL};font-weight:600"
CARD_STYLE = (
    f"background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};"
    f"border-radius:0.75rem;padding:1rem 1.25rem"
)
LABEL_FAINT_STYLE = (
    f"color:{COLOR_MUTED};text-transform:uppercase;letter-spacing:0.1em;"
    f"font-size:11px;font-weight:600"
)

# Sidebar status icons — checkmark for done steps, filled dot for the
# currently active step, hollow circle for steps yet to come. 14px to
# match Notion's sidebar row density. Width/height baked in so they
# render correctly even if theme.css doesn't apply.
_SIDEBAR_CHECK = (
    '<svg viewBox="0 0 14 14" width="14" height="14" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path d="M3 7.5 L6 10 L11 4" stroke="currentColor" stroke-width="1.75" '
    'stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'
)
_SIDEBAR_DOT = (
    '<svg viewBox="0 0 14 14" width="14" height="14" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="7" cy="7" r="3.5" fill="currentColor"/></svg>'
)
_SIDEBAR_CIRCLE = (
    '<svg viewBox="0 0 14 14" width="14" height="14" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="7" cy="7" r="3.25" stroke="currentColor" stroke-width="1.25" '
    'fill="none"/></svg>'
)

# Capability-card icons used on the upload hero. Custom 24x24 SVGs that
# share Round Two's visual vocabulary: round caps and joins (matching the
# brand mark), 1.75 stroke weight on outlines, 2.25 on the brand-style
# checkmark in `check`. The math-verified icon carries the signature
# charcoal dot at the checkmark tip — a direct echo of the brand mark.
_FEATURE_ICONS = {
    # Document with folded corner + two content lines
    "doc": (
        '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" '
        'stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>'
        '<path d="M14 3v5h5" stroke="currentColor" stroke-width="1.75" '
        'stroke-linejoin="round"/>'
        '<path d="M8.5 13h7" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round"/>'
        '<path d="M8.5 16.5h4.5" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round"/>'
        '</svg>'
    ),
    # Equality bars (=) on the left + brand-mark checkmark on the right,
    # with the signature charcoal dot at the checkmark tip
    "check": (
        '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M3 10h9" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round"/>'
        '<path d="M3 14h9" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round"/>'
        '<path d="M14.5 13.5l2.25 2.25 4.75-4.75" stroke="currentColor" '
        'stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="21.5" cy="11" r="1.4" fill="#0B1220"/>'
        '</svg>'
    ),
    # Rounded "example box" silhouette with a corner dot tag + content lines
    "example": (
        '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="3.5" y="5" width="17" height="14" rx="2.5" '
        'stroke="currentColor" stroke-width="1.75"/>'
        '<circle cx="6.5" cy="9" r="1.25" fill="currentColor"/>'
        '<path d="M9 9h7" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round"/>'
        '<path d="M6.5 13h11" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round"/>'
        '<path d="M6.5 16.5h7" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round"/>'
        '</svg>'
    ),
    # Three rows of (answer bar + checkmark) — a literal answer key
    "key": (
        '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M3 6h7" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round"/>'
        '<path d="M14 6l2 2 4-4" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M3 12h7" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round"/>'
        '<path d="M14 12l2 2 4-4" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M3 18h7" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round"/>'
        '<path d="M14 18l2 2 4-4" stroke="currentColor" stroke-width="1.75" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    ),
}

FEATURES = [
    ("doc", "Any test PDF",
     "Drop in a scan or export — Round Two extracts every problem type."),
    ("check", "Math-verified",
     "Every generated answer is checked algebraically with SymPy."),
    ("example", "Worked examples",
     "Each type opens with a clean example so students see the pattern."),
    ("key", "Answer key included",
     "Final pages are a full key — fold under or remove before printing."),
]


def _slugify(name: str) -> str:
    """Lowercase, replace runs of whitespace/punctuation with underscores,
    drop anything non-alphanumeric. Used for the download filename so a
    title like "Module 16 — Practice Worksheet" becomes
    "module_16_practice_worksheet"."""
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_-]+", "_", s).strip("_")
    return s or "practice_worksheet"


def _default_title_from_filename(pdf_name: str) -> str:
    """Seed the worksheet title from the uploaded file stem. Strips trailing
    punctuation, collapses underscores/dashes to spaces, title-cases the
    result. Filenames like "module16_test.pdf" become "Module16 Test"; the
    teacher edits from there."""
    stem = Path(pdf_name).stem.rstrip(" .-_")
    words = re.split(r"[\s_-]+", stem)
    cleaned = " ".join(w for w in words if w).strip()
    base = cleaned.title() if cleaned else "Practice"
    return f"{base} — Practice Worksheet"


# Spinner SVG — uses SVG SMIL animation (no CSS keyframes needed) so it
# works inside any markdown block regardless of CSS-load timing.
_SPINNER_SVG = (
    '<svg width="44" height="44" viewBox="0 0 40 40" '
    'xmlns="http://www.w3.org/2000/svg" style="display:inline-block">'
    f'<circle cx="20" cy="20" r="16" stroke="{COLOR_BORDER}" '
    'stroke-width="3.5" fill="none"/>'
    f'<circle cx="20" cy="20" r="16" stroke="{COLOR_GLACIER}" '
    'stroke-width="3.5" stroke-linecap="round" fill="none" '
    'stroke-dasharray="100.5" stroke-dashoffset="75" '
    'transform="rotate(-90 20 20)">'
    '<animateTransform attributeName="transform" type="rotate" '
    'from="0 20 20" to="360 20 20" dur="1.1s" repeatCount="indefinite"/>'
    '</circle></svg>'
)


def _overlay_html(title: str, subtitle: str = "", progress: float | None = None) -> str:
    """Centered loading card over a dimmed full-viewport backdrop. Used by
    _show_overlay for the three slow operations (extract, generate, render).

    progress: 0.0–1.0 to render an inline progress bar; None to omit."""
    progress_html = ""
    if progress is not None:
        pct = max(0.0, min(1.0, progress)) * 100
        progress_html = (
            f'<div style="margin-top:1.25rem;height:6px;width:100%;'
            f'background:{COLOR_BORDER};border-radius:999px;overflow:hidden">'
            f'<div style="height:100%;width:{pct:.1f}%;'
            f'background:{COLOR_GLACIER};border-radius:999px;'
            f'transition:width 0.25s ease"></div></div>'
        )
    return (
        f'<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;'
        f'background:rgba(11,18,32,0.45);backdrop-filter:blur(3px);'
        f'-webkit-backdrop-filter:blur(3px);'
        f'z-index:9999;display:flex;align-items:center;justify-content:center">'
        f'<div style="background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};'
        f'border-radius:1rem;padding:2rem 2.5rem;text-align:center;'
        f'min-width:340px;max-width:420px;'
        f'box-shadow:0 24px 48px rgba(11,18,32,0.18),'
        f'0 8px 16px rgba(11,18,32,0.08)">'
        f'{_SPINNER_SVG}'
        f'<div style="font-size:1.125rem;font-weight:600;color:{COLOR_CHARCOAL};'
        f'margin:1rem 0 0.375rem 0;letter-spacing:-0.01em">{title}</div>'
        f'<div style="color:{COLOR_MUTED};font-size:0.875rem;margin:0;'
        f'line-height:1.5">{subtitle}</div>'
        f'{progress_html}'
        f'</div></div>'
    )


def _show_overlay(placeholder, title: str, subtitle: str = "",
                  progress: float | None = None) -> None:
    """Render the loading overlay into a Streamlit placeholder. Caller is
    responsible for placeholder.empty() when work completes."""
    placeholder.markdown(
        _overlay_html(title, subtitle, progress),
        unsafe_allow_html=True,
    )


def _eyebrow(step_key: str, extra: str | None = None) -> str:
    """Eyebrow text rendered above an H1. Pairs the step label with an
    optional second clause (e.g. file name) joined by a middle dot.
    All styling inline so it survives Streamlit's sanitizer."""
    parts = [STEP_LABELS.get(step_key, "")]
    if extra:
        parts.append(extra)
    inner = " · ".join(p for p in parts if p)
    return (
        f'<div style="display:inline-flex;align-items:center;gap:0.5rem;'
        f'color:{COLOR_MUTED};text-transform:uppercase;letter-spacing:0.12em;'
        f'font-size:11px;font-weight:600;margin-bottom:0.875rem">'
        f'<span style="width:6px;height:6px;border-radius:50%;'
        f'background:{COLOR_GLACIER}"></span>'
        f'{inner}</div>'
    )

st.set_page_config(
    page_title="Round Two",
    page_icon=str(BRAND_DIR / "favicon.svg"),
    layout="centered",
    initial_sidebar_state="expanded",
)


def _inject_theme() -> None:
    """Read assets/theme.css and inject it as a <style> block.

    HTML's <style> element has CDATA-like content parsing: the browser
    closes it at the first literal "</style>" and ignores CSS comments.
    A stray occurrence inside a /* ... */ block in theme.css will close
    the tag early and dump the rest of the file into the page as text.
    Escape any closing-tag sequences before injection so a future edit
    to theme.css can't reintroduce that footgun."""
    if not THEME_CSS.exists():
        return
    css = THEME_CSS.read_text()
    # Split the literal closing tag with a backslash; CSS treats "\/" inside
    # a comment as harmless, but the HTML parser no longer sees </style>.
    safe_css = css.replace("</style>", "<\\/style>")
    st.html(f"<style>{safe_css}</style>")


# ---------------------------------------------------------------------------
# Sidebar — brand lockup + step indicator
# ---------------------------------------------------------------------------

STEPS = [
    ("upload", "Upload"),
    ("types", "Types"),
    ("problems", "Problems"),
    ("pdf", "PDF"),
]

# Public-facing CHANGELOG.md hosted on GitHub. Opens in a new tab from
# the "What's new" link at the bottom of the sidebar. Update both the
# file and any future link redirect together.
CHANGELOG_URL = (
    "https://github.com/iancowpar/worksheet-generator/"
    "blob/claude/add-skip-permissions-flag-EMWxA/CHANGELOG.md"
)


def _render_sidebar() -> None:
    """Render brand lockup + step indicator with inline styles, plus a
    bottom-anchored "What's new" link to the CHANGELOG on GitHub.

    Hard-learned lesson: Streamlit's HTML rendering is unreliable for
    custom CSS classes. st.markdown(unsafe_allow_html=True) drops class
    attributes on nested divs in some versions; st.html() drops SVG
    children. Inline styles attached directly to elements survive both
    paths, so we lean on those instead of theme.css for these blocks."""
    glacier, charcoal, muted, faint, surface_soft = (
        "#7CC0B8", "#0B1220", "#475569", "#94A3B8", "rgba(11, 18, 32, 0.05)"
    )

    # Pin the "What's new" block to the bottom of the sidebar by making
    # the sidebar's inner content area a flex column at full viewport
    # height, then setting margin-top:auto on the last child. The position-
    # absolute approach was unreliable — Streamlit wraps each block in
    # nested divs whose positioning context isn't the sidebar section.
    # <style> goes through st.html (st.markdown sanitizes it away).
    st.html(
        '<style>'
        'section[data-testid="stSidebar"] > div:first-child {'
        '  display: flex !important;'
        '  flex-direction: column !important;'
        '  min-height: 100vh !important;'
        '}'
        'section[data-testid="stSidebar"] > div:first-child > div {'
        '  display: flex !important;'
        '  flex-direction: column !important;'
        '  flex: 1 1 auto !important;'
        '}'
        'section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],'
        'section[data-testid="stSidebar"] [data-testid*="stVerticalBlock"] {'
        '  display: flex !important;'
        '  flex-direction: column !important;'
        '  flex: 1 1 auto !important;'
        '  height: 100% !important;'
        '}'
        'section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] '
        '  > div:last-child,'
        'section[data-testid="stSidebar"] [data-testid*="stVerticalBlock"] '
        '  > div:last-child {'
        '  margin-top: auto !important;'
        '}'
        '</style>'
    )

    with st.sidebar:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.5rem;'
            f'padding:0.375rem 0.5rem;margin-bottom:1.25rem;font-weight:700;'
            f'font-size:0.9375rem;color:{charcoal};letter-spacing:-0.015em">'
            f'{MARK_SVG}<span>Round Two</span></div>'
            f'<div style="padding:0 0.5rem;margin:0 0 0.5rem 0;font-size:11px;'
            f'font-weight:600;letter-spacing:0.08em;text-transform:uppercase;'
            f'color:{faint}">Steps</div>',
            unsafe_allow_html=True,
        )

        current = st.session_state.get("step", "upload")
        current_idx = next((i for i, (k, _) in enumerate(STEPS) if k == current), 0)

        rows_html = []
        for i, (_key, label) in enumerate(STEPS):
            if i < current_idx:
                icon, icon_color, text_color, weight, bg = (
                    _SIDEBAR_CHECK, glacier, charcoal, "500", "transparent"
                )
            elif i == current_idx:
                icon, icon_color, text_color, weight, bg = (
                    _SIDEBAR_DOT, glacier, charcoal, "600", surface_soft
                )
            else:
                icon, icon_color, text_color, weight, bg = (
                    _SIDEBAR_CIRCLE, faint, muted, "500", "transparent"
                )
            rows_html.append(
                f'<div style="display:flex;align-items:center;gap:0.5rem;'
                f'padding:0.3125rem 0.5rem;border-radius:0.375rem;'
                f'background:{bg};color:{text_color};font-size:0.8125rem;'
                f'font-weight:{weight};line-height:1.25">'
                f'<span style="display:flex;align-items:center;'
                f'color:{icon_color};flex:none">{icon}</span>{label}</div>'
            )
        st.markdown("".join(rows_html), unsafe_allow_html=True)

        # Bottom-anchored "What's new" link. The injected CSS makes this
        # the last child of the sidebar's vertical block and pushes it to
        # the bottom via margin-top:auto. Opens CHANGELOG.md on GitHub in
        # a new tab so long-form release notes stay out of the sidebar.
        st.markdown(
            f'<div style="border-top:1px solid #E5E5E2;padding-top:0.875rem">'
            f'<a href="{CHANGELOG_URL}" target="_blank" rel="noopener" '
            f'style="display:flex;align-items:center;gap:0.375rem;'
            f'padding:0.375rem 0.5rem;border-radius:0.375rem;'
            f'text-decoration:none;color:{muted};font-size:0.8125rem;'
            f'font-weight:500">'
            f'<span style="font-size:11px;font-weight:600;'
            f'letter-spacing:0.08em;text-transform:uppercase;color:{faint}">'
            f'What\'s new</span>'
            f'<span style="margin-left:auto;color:{faint};font-size:0.75rem">'
            f'↗</span>'
            f'</a>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Step 1 — Upload
# ---------------------------------------------------------------------------

def _render_upload_step() -> None:
    # Inject the glacier-wash gradient directly here rather than via
    # .stApp:has(.upload-hero) in theme.css. The :has() rule wasn't
    # showing up reliably on the live deploy; injecting the style only
    # when this step renders gives us the same scoping (upload-only)
    # without depending on browser :has() support or CSS load order.
    st.html(
        '<style>'
        '.stApp { background: '
        'linear-gradient(180deg, '
        'rgba(124,192,184,0.16) 0%, '
        'rgba(124,192,184,0.07) 420px, '
        'rgba(124,192,184,0.00) 720px), '
        '#FFFFFF !important; }'
        '</style>'
    )

    # Hero block — inline styles so nothing depends on .upload-hero/
    # .hero-headline/.eyebrow-loud surviving Streamlit's sanitizer.
    glacier, charcoal, muted, border, surface = (
        "#7CC0B8", "#0B1220", "#475569", "#E5E5E2", "#FFFFFF"
    )
    # Brand lockup above the headline. Mark + "Round Two" wordmark at the
    # same heavy weight as the headline, sized smaller so the headline still
    # reads as the dominant element. Generous bottom margin gives the eyebrow
    # room to breathe before the H1.
    st.markdown(
        f'<div style="padding:2rem 0 0 0">'
        f'<div style="display:flex;align-items:center;gap:0.625rem;'
        f'margin-bottom:2.25rem">'
        f'{_mark_svg(36)}'
        f'<span style="font-weight:700;font-size:1.5rem;color:{charcoal};'
        f'letter-spacing:-0.025em">Round Two</span>'
        f'</div>'
        f'<div style="display:block;color:{glacier};text-transform:uppercase;'
        f'letter-spacing:0.14em;font-size:11px;font-weight:700;'
        f'margin-bottom:1.25rem">Math-verified · Built for special education</div>'
        f'<h1 style="font-size:3rem;line-height:1.04;letter-spacing:-0.035em;'
        f'font-weight:700;color:{charcoal};margin:0 0 1.25rem 0">'
        f'Test on Friday.<br>Practice by Monday.<br>'
        f'<span style="color:{glacier}">Math you can trust.</span></h1>'
        f'<p style="font-size:1.0625rem;line-height:1.55;color:{muted};'
        f'max-width:38rem;margin:0 0 1.5rem 0">Upload the test your students '
        f'just took. Round Two reads it, generates '
        f'<strong style="color:{charcoal};font-weight:600">5 fresh practice '
        f'problems per type</strong>, verifies the math, and renders a '
        f'printable PDF with worked examples and an answer key.</p></div>',
        unsafe_allow_html=True,
    )

    sample_path = ASSETS_DIR / "reference" / "module16_practice_worksheet.pdf"
    if sample_path.exists():
        st.download_button(
            "Download a sample worksheet",
            data=sample_path.read_bytes(),
            file_name="round_two_sample.pdf",
            mime="application/pdf",
            key="sample_download",
        )

    # Feature cards — inline styles for the same reason. SVG icons keep
    # their baked-in width/height so they always render at 22px.
    card_html = []
    for icon_key, title, desc in FEATURES:
        card_html.append(
            f'<div style="border:1px solid {border};border-radius:1rem;'
            f'padding:1.5rem 1.375rem;background:{surface};'
            f'transition:border-color 0.18s ease,transform 0.18s ease">'
            f'<div style="display:flex;align-items:center;justify-content:center;'
            f'width:40px;height:40px;border-radius:0.625rem;'
            f'background:rgba(124,192,184,0.16);color:{glacier};'
            f'margin-bottom:1rem">{_FEATURE_ICONS[icon_key]}</div>'
            f'<div style="font-weight:600;font-size:1rem;color:{charcoal};'
            f'margin-bottom:0.375rem;letter-spacing:-0.01em">{title}</div>'
            f'<div style="font-size:0.875rem;color:{muted};line-height:1.5">'
            f'{desc}</div></div>'
        )
    # repeat(4, minmax(0, 1fr)) forces exactly four equal columns and lets
    # them shrink to fit. auto-fit was wrapping to 3+1 because content
    # widths in the longer description cards exceeded the 1fr calculation.
    st.markdown(
        f'<div style="display:grid;'
        f'grid-template-columns:repeat(4,minmax(0,1fr));'
        f'gap:0.75rem;margin:1.75rem 0 2rem 0">'
        f'{"".join(card_html)}</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("Choose a test PDF", type=["pdf"], label_visibility="collapsed")
    if not uploaded:
        return

    pdf_bytes = uploaded.getvalue()
    file_hash = hashlib.sha256(pdf_bytes).hexdigest()
    st.session_state.pdf_bytes = pdf_bytes
    st.session_state.pdf_hash = file_hash
    st.session_state.pdf_name = uploaded.name
    st.session_state.pdf_size = len(pdf_bytes)

    est = estimate_cost(len(pdf_bytes))
    size_kb = len(pdf_bytes) / 1024
    size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"

    divider_style = (
        f"display:flex;align-items:center;gap:0.875rem;margin:2.25rem 0 1.25rem 0;"
        f"color:{COLOR_FAINT};font-size:11px;text-transform:uppercase;"
        f"letter-spacing:0.12em;font-weight:600"
    )
    ready_card_style = (
        f"background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};"
        f"border-radius:0.75rem;padding:1rem 1.125rem 1.125rem 1.125rem"
    )
    ready_num_style = (
        f"font-size:1.625rem;font-weight:700;letter-spacing:-0.025em;"
        f"color:{COLOR_CHARCOAL};margin:0.5rem 0 0.25rem 0;"
        f"font-feature-settings:'tnum'"
    )
    ready_sub_style = f"font-size:0.8125rem;color:{COLOR_MUTED};line-height:1.45"

    st.markdown(
        f'<div style="{divider_style}">'
        f'<span style="flex:1;height:1px;background:{COLOR_BORDER}"></span>'
        f'Ready to generate'
        f'<span style="flex:1;height:1px;background:{COLOR_BORDER}"></span>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.625rem;'
        f'margin:1.25rem 0">'
        f'<div style="{ready_card_style}">'
        f'<div style="{LABEL_FAINT_STYLE}">Estimated cost</div>'
        f'<div style="{ready_num_style}">${est.dollars_low:.2f} – ${est.dollars_high:.2f}</div>'
        f'<div style="{ready_sub_style}">~{est.input_tokens:,} input + '
        f'{est.output_tokens:,} output tokens across one Opus 4.7 extraction '
        f'call and {est.n_types * est.n_problems_per_type} Sonnet 4.6 '
        f'generation calls.</div>'
        f'</div>'
        f'<div style="{ready_card_style}">'
        f'<div style="{LABEL_FAINT_STYLE}">File</div>'
        f'<div style="{ready_num_style};font-size:1.125rem;'
        f'word-break:break-all;line-height:1.3">{uploaded.name}</div>'
        f'<div style="{ready_sub_style}">{size_str} · SHA-256 {file_hash[:8]}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Worksheet title input — drives both the on-PDF title and the
    # downloaded filename. Reset the seeded default when the upload changes
    # so the field doesn't carry over a stale title from a prior file.
    if st.session_state.get("title_seed_hash") != file_hash:
        st.session_state.worksheet_title = _default_title_from_filename(uploaded.name)
        st.session_state.title_seed_hash = file_hash
    title = st.text_input(
        "Worksheet title",
        value=st.session_state.worksheet_title,
        key="worksheet_title_input",
        help="Appears at the top of the PDF and as the download filename.",
    )
    st.session_state.worksheet_title = title
    if title.strip():
        st.caption(f"Will save as `{_slugify(title)}.pdf`")

    if st.button("Continue →", type="primary"):
        st.session_state.step = "types"
        st.rerun()


# ---------------------------------------------------------------------------
# Step 2 — Extracted types preview
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _cached_extract_types(file_hash: str, pdf_bytes: bytes) -> list[ExtractedTypeSpec]:
    """One Opus call per unique file hash. Streamlit's cache key is the args,
    so passing the hash explicitly keeps cache hits stable across reruns."""
    del file_hash  # only present for the cache key
    return extract_problem_types(pdf_bytes)


def _render_types_step() -> None:
    if "types" not in st.session_state:
        overlay = st.empty()
        _show_overlay(
            overlay,
            "Reading the test…",
            "Round Two is looking at every page and identifying the problem types. "
            "Usually 10–20 seconds.",
        )
        try:
            types = _cached_extract_types(
                st.session_state.pdf_hash,
                st.session_state.pdf_bytes,
            )
            st.session_state.types = types
        except MissingAPIKey as e:
            overlay.empty()
            _render_api_key_error(str(e))
            return
        except Exception as e:
            overlay.empty()
            _render_generic_error("Extraction failed", e)
            return
        overlay.empty()

    types: list[ExtractedTypeSpec] = st.session_state.types
    pdf_name = st.session_state.get("pdf_name", "")
    st.markdown(
        f'<div style="margin-bottom:2rem">'
        + _eyebrow("types", pdf_name)
        + f'<h1 style="{H1_STYLE}">Problem types</h1>'
        f'<p style="{LEAD_STYLE}">We found '
        f'<strong style="{LEAD_STRONG_STYLE}">{len(types)} types</strong> '
        'in this test. Skim each one — open the expander to check the example '
        'we extracted — then continue when it looks right.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    tag_style = (
        f"font-size:0.75rem;font-family:'JetBrains Mono',ui-monospace,monospace;"
        f"color:{COLOR_MUTED};background:{COLOR_SURFACE_SOFT};"
        f"border:1px solid {COLOR_BORDER};border-radius:0.375rem;"
        f"padding:0.1875rem 0.5rem;display:inline-block"
    )
    for spec in types:
        with st.expander(f"Type {spec.number} — {spec.title}"):
            st.markdown(
                f'<div style="margin-bottom:0.875rem">'
                f'<span style="{tag_style}">Layout · {spec.layout}</span></div>'
                f'<div style="{LABEL_FAINT_STYLE}">Pattern</div>'
                f'<div style="margin-bottom:0.875rem">{spec.pattern_description}</div>'
                f'<div style="{LABEL_FAINT_STYLE}">Example body</div>'
                f'<div style="margin-bottom:0.625rem">{spec.example_problem.body}</div>'
                f'<div style="{LABEL_FAINT_STYLE}">Example answer</div>'
                f'<div><code>{spec.example_problem.answer}</code></div>',
                unsafe_allow_html=True,
            )

    # Difficulty knobs — two independent axes. A special-ed student often
    # has a math/reading split, so the teacher can dial math up while
    # keeping language scaffolded (or vice versa). Defaults to "Same".
    # Widget keys equal the session-state keys we read in _render_problems_step,
    # so Streamlit stores selections directly at the right place.
    st.session_state.setdefault("math_difficulty", "Same")
    st.session_state.setdefault("language_difficulty", "Same")
    st.markdown(
        '<div style="margin: 1.5rem 0 0.25rem 0; font-size: 11px; '
        'font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; '
        'color: #94A3B8">Difficulty</div>',
        unsafe_allow_html=True,
    )
    diff_options = ["Easier", "Same", "Harder"]
    st.radio(
        "Math",
        diff_options,
        key="math_difficulty",
        horizontal=True,
        help="Easier: smaller coefficients, fewer terms, cleaner substitutions. "
             "Harder: larger coefficients, an extra term, substitutions that "
             "need real arithmetic.",
    )
    st.radio(
        "Language",
        diff_options,
        key="language_difficulty",
        horizontal=True,
        help="Easier: short sentences, common vocabulary, explicit step cues. "
             "Harder: longer paragraphs, sophisticated vocabulary, embedded "
             "numbers, no scaffolding.",
    )

    col_back, _, col_next = st.columns([2, 4, 3])
    with col_back:
        if st.button("← Re-upload"):
            for k in ("types", "generated"):
                st.session_state.pop(k, None)
            st.session_state.step = "upload"
            st.rerun()
    with col_next:
        if st.button("Generate practice problems →", type="primary",
                     use_container_width=True):
            # Clear any prior generation so a difficulty change here
            # actually triggers fresh problems.
            st.session_state.pop("generated", None)
            st.session_state.pop("pdf_out_bytes", None)
            st.session_state.pop("pdf_out_name", None)
            st.session_state.step = "problems"
            st.rerun()


# ---------------------------------------------------------------------------
# Step 3 — Generate and review
# ---------------------------------------------------------------------------

PROBLEM_LETTERS = "ABCDE"


def _render_problems_step() -> None:
    # Difficulty selections were captured in session_state on the Types step.
    # Convert UI labels ("Same", "Easier", "Harder") to the lowercase enum
    # keys the generator expects.
    math_diff = st.session_state.get("math_difficulty", "Same").lower()
    lang_diff = st.session_state.get("language_difficulty", "Same").lower()

    if "generated" not in st.session_state:
        types: list[ExtractedTypeSpec] = st.session_state.types
        n_total = sum(len(PROBLEM_LETTERS) for _ in types)

        overlay = st.empty()
        _show_overlay(
            overlay,
            f"Generating problem 1 of {n_total}…",
            "Each problem is generated and then verified. This usually "
            "takes 60–90 seconds total.",
            progress=0.0,
        )

        generated_by_type: dict[int, list[GeneratedProblem]] = {}
        idx = 0
        for spec in types:
            generated_by_type[spec.number] = []
            for letter in PROBLEM_LETTERS:
                label = f"{spec.number}-{letter}"
                excluded = [gp.problem for gp in generated_by_type[spec.number]]
                excluded.append(spec.example_problem)
                try:
                    gp = generate_problem_with_retry(
                        spec, label, excluded,
                        math_difficulty=math_diff,
                        language_difficulty=lang_diff,
                    )
                except MissingAPIKey as e:
                    overlay.empty()
                    _render_api_key_error(str(e))
                    return
                except Exception as e:
                    overlay.empty()
                    _render_generic_error(f"Generation failed for {label}", e)
                    return
                generated_by_type[spec.number].append(gp)
                idx += 1
                next_label = f"problem {min(idx + 1, n_total)} of {n_total}" \
                    if idx < n_total else "verifying…"
                _show_overlay(
                    overlay,
                    f"Generating {next_label}",
                    f"On {spec.title}.",
                    progress=idx / n_total,
                )
        overlay.empty()
        st.session_state.generated = generated_by_type

    generated_by_type: dict[int, list[GeneratedProblem]] = st.session_state.generated
    types_by_num = {s.number: s for s in st.session_state.types}

    n_total = sum(len(gps) for gps in generated_by_type.values())
    flagged = sum(
        1 for gps in generated_by_type.values()
        for gp in gps if not gp.verification.ok
    )
    n_verified = n_total - flagged
    status_extra = (
        f"{n_verified} of {n_total} verified"
        if not flagged else f"{flagged} flagged · {n_verified} verified"
    )
    st.markdown(
        '<div style="margin-bottom:2rem">'
        + _eyebrow("problems", status_extra)
        + f'<h1 style="{H1_STYLE}">Review the problems</h1>'
        f'<p style="{LEAD_STYLE}">Each problem was generated to match its '
        'type and then checked algebraically with SymPy. Flagged problems '
        'failed verification — regenerate or accept them manually.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if flagged:
        st.markdown(
            f'<div style="background:{COLOR_WARM_SOFT};'
            f'border:1px solid {COLOR_WARM};border-radius:0.75rem;'
            f'padding:1rem 1.25rem;margin-bottom:1rem;color:{COLOR_CHARCOAL}">'
            f'<strong>⚠️ {flagged} problem{"s" if flagged != 1 else ""} flagged for review.</strong> '
            f'The verifier couldn\'t confirm the answer. Regenerate or accept '
            f'each one before generating the PDF.'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Streamlit's sanitizer was stripping the inline style on the inner
    # <span> badge, leaving "T1Title" mashed together. Switching to a
    # flex layout with sibling <div>s — those keep their inline styles.
    badge_style = (
        f"display:flex;align-items:center;justify-content:center;"
        f"min-width:28px;height:24px;padding:0 0.5rem;border-radius:999px;"
        f"background:{COLOR_ACCENT_SOFT};color:{COLOR_ACCENT};"
        f"font-size:0.6875rem;font-weight:700;"
        f"font-family:JetBrains Mono,ui-monospace,monospace;"
        f"letter-spacing:0.04em;flex:none"
    )
    title_style = (
        f"font-size:1.125rem;font-weight:700;color:{COLOR_CHARCOAL};"
        f"letter-spacing:-0.02em"
    )
    for type_num in sorted(generated_by_type.keys()):
        spec = types_by_num[type_num]
        gps = generated_by_type[type_num]
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.625rem;'
            f'margin-top:1.75rem;margin-bottom:0.5rem">'
            f'<div style="{badge_style}">T{type_num}</div>'
            f'<div style="{title_style}">{spec.title}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for i, gp in enumerate(gps):
            badge = "  ⚠️" if not gp.verification.ok else ""
            with st.expander(f"Problem {gp.problem.label}{badge}", expanded=not gp.verification.ok):
                st.markdown(f"**Body:** {gp.problem.body}")
                st.markdown(f"**Answer:** `{gp.problem.answer}`")
                if gp.problem.options:
                    opts = "  •  ".join(f"({chr(65 + j)}) {o}" for j, o in enumerate(gp.problem.options))
                    st.markdown(f"**Options:** {opts}")
                if not gp.verification.ok:
                    st.warning(f"Verification failed: {gp.verification.reason}")
                btn_regen, btn_accept = st.columns([1, 1])
                with btn_regen:
                    if st.button("Regenerate", key=f"regen_{type_num}_{i}"):
                        excluded = [g.problem for g in gps if g is not gp]
                        excluded.append(spec.example_problem)
                        regen_overlay = st.empty()
                        _show_overlay(
                            regen_overlay,
                            f"Regenerating problem {gp.problem.label}…",
                            "Replacing the flagged problem with a fresh one.",
                        )
                        try:
                            new_gp = generate_problem_with_retry(
                                spec, gp.problem.label, excluded,
                                math_difficulty=math_diff,
                                language_difficulty=lang_diff,
                            )
                        except Exception as e:
                            regen_overlay.empty()
                            _render_generic_error(f"Regeneration failed for {gp.problem.label}", e)
                            return
                        regen_overlay.empty()
                        gps[i] = new_gp
                        st.rerun()
                if not gp.verification.ok:
                    with btn_accept:
                        if st.button("Accept anyway",
                                     key=f"accept_{type_num}_{i}",
                                     help="I've checked the math myself; ship it as-is."):
                            from problem_generator import GeneratedProblem  # local — avoid circular at top
                            from verifier import VerificationResult
                            gps[i] = GeneratedProblem(
                                problem=gp.problem,
                                verification=VerificationResult(
                                    ok=True,
                                    reason="manually accepted by teacher",
                                ),
                                attempts=gp.attempts,
                            )
                            st.rerun()

    # PDF generation gate: any flagged problems block the forward action.
    # The teacher must regenerate or explicitly Accept Anyway each one.
    # This is the cheap version of "wrong math can't ship by accident."
    block_pdf = flagged > 0

    col_back, _, col_next = st.columns([2, 4, 3])
    with col_back:
        if st.button("← Back to types"):
            st.session_state.pop("generated", None)
            st.session_state.step = "types"
            st.rerun()
    with col_next:
        gate_help = (
            f"{flagged} flagged problem{'s' if flagged != 1 else ''} need attention "
            "(regenerate or accept anyway) before generating the PDF."
            if block_pdf else None
        )
        if st.button("Generate PDF →", type="primary",
                     use_container_width=True, disabled=block_pdf,
                     help=gate_help):
            st.session_state.step = "pdf"
            st.rerun()


# ---------------------------------------------------------------------------
# Step 4 — PDF
# ---------------------------------------------------------------------------

def _render_pdf_step() -> None:
    if "pdf_out_bytes" not in st.session_state:
        types_by_num = {s.number: s for s in st.session_state.types}
        worksheet_types = []
        for type_num in sorted(st.session_state.generated.keys()):
            spec = types_by_num[type_num]
            problems = [gp.problem for gp in st.session_state.generated[type_num]]
            worksheet_types.append(spec.to_problem_type(problems))

        # Prefer the teacher-supplied title from the upload step; fall back
        # to the derived title only if they cleared the field.
        title = (st.session_state.get("worksheet_title") or "").strip()
        if not title:
            title = _derive_worksheet_title(
                st.session_state.types, st.session_state.pdf_name
            )

        worksheet = Worksheet(title=title, types=worksheet_types)

        overlay = st.empty()
        _show_overlay(
            overlay,
            "Rendering your worksheet…",
            "Laying out problems, drawing exponents, and stamping the answer key.",
        )
        try:
            tmp = Path("/tmp") / f"round_two_{st.session_state.pdf_hash[:12]}.pdf"
            render_worksheet(worksheet, tmp)
            st.session_state.pdf_out_bytes = tmp.read_bytes()
            st.session_state.pdf_out_name = f"{_slugify(title)}.pdf"
        finally:
            overlay.empty()

    n_types = len(st.session_state.get("types", []))
    n_problems = sum(len(gps) for gps in st.session_state.get("generated", {}).values())
    size_kb = len(st.session_state.pdf_out_bytes) / 1024
    size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"

    done_mark_style = (
        f"display:flex;align-items:center;justify-content:center;"
        f"width:56px;height:56px;border-radius:999px;"
        f"background:{COLOR_SURFACE_SOFT};border:1px solid {COLOR_BORDER};"
        f"margin-bottom:1.125rem"
    )
    ready_card_style = (
        f"background:{COLOR_SURFACE};border:1px solid {COLOR_BORDER};"
        f"border-radius:0.75rem;padding:1rem 1.125rem 1.125rem 1.125rem"
    )
    ready_num_style = (
        f"font-size:1.625rem;font-weight:700;letter-spacing:-0.025em;"
        f"color:{COLOR_CHARCOAL};margin:0.5rem 0 0.25rem 0;"
        f"font-feature-settings:'tnum'"
    )
    ready_sub_style = (
        f"font-size:0.8125rem;color:{COLOR_MUTED};line-height:1.45"
    )

    st.markdown(
        '<div style="margin-bottom:1.5rem">'
        + _eyebrow("pdf", st.session_state.pdf_out_name)
        + f'<div style="display:flex;flex-direction:column;align-items:flex-start">'
        f'<div style="{done_mark_style}">{MARK_SVG_LARGE}</div>'
        f'<h1 style="{H1_STYLE}">Worksheet ready.</h1></div>'
        f'<p style="{LEAD_STYLE}">Print or share — the answer key is the last '
        'page so you can fold it under or remove before handing out copies.</p>'
        '</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.625rem;'
        f'margin:1.25rem 0">'
        f'<div style="{ready_card_style}">'
        f'<div style="{LABEL_FAINT_STYLE}">Contents</div>'
        f'<div style="{ready_num_style}">{n_types} type'
        f'{"s" if n_types != 1 else ""} · {n_problems} problem'
        f'{"s" if n_problems != 1 else ""}</div>'
        f'<div style="{ready_sub_style}">Worked example per type, then 5 '
        'practice problems each, then a full answer key.</div>'
        '</div>'
        f'<div style="{ready_card_style}">'
        f'<div style="{LABEL_FAINT_STYLE}">File</div>'
        f'<div style="{ready_num_style};font-size:1.125rem;'
        f'word-break:break-all;line-height:1.3">'
        f'{st.session_state.pdf_out_name}</div>'
        f'<div style="{ready_sub_style}">{size_str} · PDF</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        "Download PDF",
        data=st.session_state.pdf_out_bytes,
        file_name=st.session_state.pdf_out_name,
        mime="application/pdf",
        type="primary",
    )

    if st.button("Start over"):
        st.session_state.clear()
        st.rerun()


def _derive_worksheet_title(types: list[ExtractedTypeSpec], pdf_name: str) -> str:
    """Build a worksheet title from the type collection. Uses the first type's
    answer_key_title as a topic hint and appends '— Practice Worksheet'."""
    if types and types[0].answer_key_title:
        topic = types[0].answer_key_title
    elif types:
        topic = types[0].title.split("(")[0].strip()
    else:
        topic = Path(pdf_name).stem.replace("_", " ").replace("-", " ").title()
    return f"{topic} — Practice Worksheet"


# ---------------------------------------------------------------------------
# Error surfaces
# ---------------------------------------------------------------------------

def _render_api_key_error(message: str) -> None:
    st.markdown(
        f'<div style="background:{COLOR_WARM_SOFT};'
        f'border:1px solid {COLOR_WARM};border-radius:0.75rem;'
        f'padding:1rem 1.25rem;color:{COLOR_CHARCOAL}">'
        '<strong>Missing API key.</strong>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.info(message)
    st.markdown(
        "If you're running locally: `export ANTHROPIC_API_KEY=sk-ant-...` and rerun. "
        "If you're on Streamlit Community Cloud: open the app settings → Secrets and paste "
        "the value into `ANTHROPIC_API_KEY` (see `.streamlit/secrets.toml.example`)."
    )


def _render_generic_error(prefix: str, exc: BaseException) -> None:
    st.error(f"{prefix}: {exc}")
    with st.expander("Show details"):
        st.code(repr(exc))
    if st.button("Retry"):
        st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _inject_theme()
    _render_sidebar()

    if "step" not in st.session_state:
        st.session_state.step = "upload"

    step = st.session_state.step
    if step == "upload":
        _render_upload_step()
    elif step == "types":
        _render_types_step()
    elif step == "problems":
        _render_problems_step()
    elif step == "pdf":
        _render_pdf_step()
    else:
        st.session_state.step = "upload"
        st.rerun()


if __name__ == "__main__":
    main()
