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

st.set_page_config(
    page_title="Round Two",
    page_icon=str(BRAND_DIR / "favicon.svg"),
    layout="centered",
    initial_sidebar_state="expanded",
)


def _inject_theme() -> None:
    """Read assets/theme.css and inject it as a <style> block. Uses st.html
    rather than st.markdown(unsafe_allow_html=True) because Streamlit's
    markdown sanitizer strips <style>/<script>/<iframe> tags even with the
    flag set (the CSS leaks through as plain Markdown text otherwise)."""
    if THEME_CSS.exists():
        css = THEME_CSS.read_text()
        st.html(f"<style>{css}</style>")


# ---------------------------------------------------------------------------
# Sidebar — brand lockup + step indicator
# ---------------------------------------------------------------------------

STEPS = [
    ("upload", "Upload"),
    ("types", "Types"),
    ("problems", "Problems"),
    ("pdf", "PDF"),
]


def _render_sidebar() -> None:
    with st.sidebar:
        logo_path = BRAND_DIR / "logo.svg"
        if logo_path.exists():
            # Inline the SVG so DM Sans (loaded by assets/theme.css) drives the
            # wordmark, and we control exact pixel size in the sidebar column.
            svg = logo_path.read_text()
            st.markdown(
                f'<div style="margin-bottom: 0.5rem">{svg}</div>',
                unsafe_allow_html=True,
            )
        st.markdown('<div class="label-faint" style="margin-top: 1.25rem">Steps</div>',
                    unsafe_allow_html=True)
        current = st.session_state.get("step", "upload")
        current_idx = next((i for i, (k, _) in enumerate(STEPS) if k == current), 0)
        chips_html = ""
        for i, (key, label) in enumerate(STEPS):
            cls = "step"
            if i < current_idx:
                cls += " is-done"
            elif i == current_idx:
                cls += " is-active"
            chips_html += f'<div class="{cls}"><div class="step-dot"></div>{label}</div>'
        st.markdown(chips_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Step 1 — Upload
# ---------------------------------------------------------------------------

def _render_upload_step() -> None:
    st.markdown(
        '<div style="margin-bottom: 1.5rem">'
        '<h1 style="margin-bottom: 0.25rem">Practice worksheet from a test</h1>'
        '<p style="color: var(--text-muted); margin-top: 0">'
        'Upload the test your students just took. Round Two reads it, generates '
        '5 fresh practice problems per type, and renders a printable PDF with '
        'worked examples and an answer key.'
        '</p></div>',
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
    st.markdown(
        '<div class="card" style="margin: 1rem 0">'
        f'<div class="label-faint">Estimated cost</div>'
        f'<div style="font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem">'
        f'${est.dollars_low:.2f} – ${est.dollars_high:.2f}'
        f'</div>'
        f'<div style="color: var(--text-muted); font-size: 0.875rem">'
        f'~{est.input_tokens:,} input + {est.output_tokens:,} output tokens '
        f'across one Opus 4.7 extraction call and {est.n_types * est.n_problems_per_type} '
        f'Sonnet 4.6 generation calls'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    if st.button("Continue", type="primary"):
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
    st.markdown('<h1>Problem types</h1>', unsafe_allow_html=True)

    if "types" not in st.session_state:
        try:
            with st.spinner("Reading the test..."):
                types = _cached_extract_types(
                    st.session_state.pdf_hash,
                    st.session_state.pdf_bytes,
                )
            st.session_state.types = types
        except MissingAPIKey as e:
            _render_api_key_error(str(e))
            return
        except Exception as e:
            _render_generic_error("Extraction failed", e)
            return

    types: list[ExtractedTypeSpec] = st.session_state.types
    st.markdown(
        f'<p style="color: var(--text-muted)">Found <strong>{len(types)} types</strong>. '
        'Skim them to confirm the extraction looks right, then continue.</p>',
        unsafe_allow_html=True,
    )

    for spec in types:
        with st.expander(f"Type {spec.number} — {spec.title}"):
            st.markdown(
                f'<div class="label-faint">Layout</div>'
                f'<div style="margin-bottom: 0.75rem"><code>{spec.layout}</code></div>'
                f'<div class="label-faint">Pattern</div>'
                f'<div style="margin-bottom: 0.75rem">{spec.pattern_description}</div>'
                f'<div class="label-faint">Example body</div>'
                f'<div style="margin-bottom: 0.5rem">{spec.example_problem.body}</div>'
                f'<div class="label-faint">Example answer</div>'
                f'<div><code>{spec.example_problem.answer}</code></div>',
                unsafe_allow_html=True,
            )

    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Re-upload"):
            for k in ("types", "generated"):
                st.session_state.pop(k, None)
            st.session_state.step = "upload"
            st.rerun()
    with col_next:
        if st.button("Generate practice problems →", type="primary"):
            st.session_state.step = "problems"
            st.rerun()


# ---------------------------------------------------------------------------
# Step 3 — Generate and review
# ---------------------------------------------------------------------------

PROBLEM_LETTERS = "ABCDE"


def _render_problems_step() -> None:
    st.markdown('<h1>Review problems</h1>', unsafe_allow_html=True)

    if "generated" not in st.session_state:
        types: list[ExtractedTypeSpec] = st.session_state.types
        n_total = sum(len(PROBLEM_LETTERS) for _ in types)
        progress = st.progress(0.0, text=f"Generating 0/{n_total}...")

        generated_by_type: dict[int, list[GeneratedProblem]] = {}
        idx = 0
        for spec in types:
            generated_by_type[spec.number] = []
            for letter in PROBLEM_LETTERS:
                label = f"{spec.number}-{letter}"
                excluded = [gp.problem for gp in generated_by_type[spec.number]]
                excluded.append(spec.example_problem)
                try:
                    gp = generate_problem_with_retry(spec, label, excluded)
                except MissingAPIKey as e:
                    progress.empty()
                    _render_api_key_error(str(e))
                    return
                except Exception as e:
                    progress.empty()
                    _render_generic_error(f"Generation failed for {label}", e)
                    return
                generated_by_type[spec.number].append(gp)
                idx += 1
                progress.progress(idx / n_total, text=f"Generating {idx}/{n_total}...")
        progress.empty()
        st.session_state.generated = generated_by_type

    generated_by_type: dict[int, list[GeneratedProblem]] = st.session_state.generated
    types_by_num = {s.number: s for s in st.session_state.types}

    flagged = sum(
        1 for gps in generated_by_type.values()
        for gp in gps if not gp.verification.ok
    )
    if flagged:
        st.markdown(
            f'<div class="card" style="background: var(--warm-soft); border-color: var(--warm); margin-bottom: 1rem">'
            f'<strong>⚠️ {flagged} problem{"s" if flagged != 1 else ""} flagged for review.</strong> '
            f'The verifier couldn\'t confirm the answer. Regenerate or accept manually.'
            f'</div>',
            unsafe_allow_html=True,
        )

    for type_num in sorted(generated_by_type.keys()):
        spec = types_by_num[type_num]
        gps = generated_by_type[type_num]
        st.markdown(
            f'<h3 style="margin-top: 1.5rem">Type {type_num} — {spec.title}</h3>',
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
                if st.button("Regenerate", key=f"regen_{type_num}_{i}"):
                    excluded = [g.problem for g in gps if g is not gp]
                    excluded.append(spec.example_problem)
                    with st.spinner(f"Regenerating {gp.problem.label}..."):
                        try:
                            new_gp = generate_problem_with_retry(spec, gp.problem.label, excluded)
                        except Exception as e:
                            _render_generic_error(f"Regeneration failed for {gp.problem.label}", e)
                            return
                    gps[i] = new_gp
                    st.rerun()

    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Back to types"):
            st.session_state.pop("generated", None)
            st.session_state.step = "types"
            st.rerun()
    with col_next:
        if st.button("Generate PDF →", type="primary"):
            st.session_state.step = "pdf"
            st.rerun()


# ---------------------------------------------------------------------------
# Step 4 — PDF
# ---------------------------------------------------------------------------

def _render_pdf_step() -> None:
    st.markdown('<h1>Download worksheet</h1>', unsafe_allow_html=True)

    if "pdf_out_bytes" not in st.session_state:
        types_by_num = {s.number: s for s in st.session_state.types}
        worksheet_types = []
        for type_num in sorted(st.session_state.generated.keys()):
            spec = types_by_num[type_num]
            problems = [gp.problem for gp in st.session_state.generated[type_num]]
            worksheet_types.append(spec.to_problem_type(problems))

        worksheet = Worksheet(
            title=_derive_worksheet_title(st.session_state.types, st.session_state.pdf_name),
            types=worksheet_types,
        )

        with st.spinner("Rendering PDF..."):
            buf = io.BytesIO()
            tmp = Path("/tmp") / f"round_two_{st.session_state.pdf_hash[:12]}.pdf"
            render_worksheet(worksheet, tmp)
            st.session_state.pdf_out_bytes = tmp.read_bytes()
            st.session_state.pdf_out_name = (
                Path(st.session_state.pdf_name).stem + "_practice.pdf"
            )

    st.markdown(
        '<div class="card" style="margin: 1rem 0">'
        '<strong>Worksheet ready.</strong> Print or share — the answer key is the '
        'last page so you can fold it under or remove before handing out copies.'
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
        '<div class="card" style="background: var(--warm-soft); border-color: var(--warm)">'
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
