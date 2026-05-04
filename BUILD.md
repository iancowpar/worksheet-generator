# Round Two — what we built

A tour of every file and piece of the system, organized by responsibility.
Companion to `CLAUDE.md` (the spec) and `README.md` (the user-facing
landing page). This file is the map: what each module is, what it does,
and how the pieces fit together.

## The product, in one paragraph

Round Two is a Streamlit web app for a special-education math teacher.
She uploads the math test her students just took; the app extracts the
distinct problem types, generates five practice variants per type with
verified answers, and renders a printable PDF worksheet — worked
example per type, five practice problems, and an answer key. She
reviews the extracted types and generated problems before the PDF
renders so she can catch errors before printing.

## End-to-end flow

```
Upload PDF                     →  app.py / _render_upload_step
  hash file, show cost preview

Extract types                  →  problem_generator.extract_problem_types
  one Opus 4.7 multimodal call      (prompts.EXTRACT_TYPES_*)
  returns ExtractedTypeSpec[]

Review types                   →  app.py / _render_types_step
  expanders showing each type's example

Generate problems              →  problem_generator.generate_problem_with_retry
  N × Sonnet 4.6 calls              (prompts.GENERATE_PROBLEM_*)
  → verifier.verify (SymPy)
  → fallback: problem_generator.verify_word_problem (Sonnet)
  → correct_substitution_in_answer for word-blank arithmetic
  retry up to 2× then flag

Review problems                →  app.py / _render_problems_step
  Approve / Regenerate / Edit per problem; ⚠️ on flagged

Render PDF                     →  worksheet_renderer.render_worksheet
  ReportLab canvas-direct
  one page per type + answer-key page(s)

Download                       →  app.py / _render_pdf_step
```

## Modules

### `worksheet_renderer.py` — the PDF

ReportLab canvas-direct renderer that reproduces the canonical visual
style from `reference/`. Step 4 of the build added the eight layout
variants needed to cover both reference outputs end-to-end:

| Layout | Used by | What it draws |
|---|---|---|
| `centered` | module 16 Types 1, 2 | Bold label + prompt row, centered math expression below |
| `word_setup` | module 16 Type 3 | Paragraph stem + indented pre-filled `P = ...` setup line |
| `word_blanks` | module 16 Type 4 | Paragraph stem + two-column bold answer cues, no fill-in lines |
| `mc_2col` | module 13/14 Types 1, 2, 3, 5 | 4 short MC options laid out in 2 columns (A,B left · C,D right) |
| `mc_4row` | module 13/14 Type 4 | 4 long MC options stacked vertically with wrapping |
| `short_answer_right` | module 13/14 Types 7, 8 | Right-aligned `r = ____` blank on the same row as label |
| `short_answer_below` | module 13/14 Type 9 | Full-width `f(n) = ____` blank beneath the paragraph |
| `table` | module 13/14 Type 6 | Single multi-row classification grid (Arithmetic vs. Geometric) |

Other responsibilities:
- **Even problem distribution** — `_draw_problems` divides the available
  vertical space by problem count, with `PAD_TOP = 28` separator
  clearance so the gray `#cccccc` rules sit in whitespace and never
  collide with problem headers.
- **Manual exponent rendering** — `_draw_text_with_exponents` parses
  `^N` and `^{...}` markup and draws the exponent at 65% font size
  raised by 40%, because Helvetica renders Unicode superscripts
  (², ³, ⁴) as black boxes.
- **Page anatomy** — `_draw_page_header` (title + Name/Date/Period
  blanks), `_draw_section_header` (NAVY 12pt bold + horizontal rule),
  `_draw_example_box` (LIGHT fill, TAN border, "EXAMPLE — Look at
  this before you begin").
- **Multi-page answer key** — `_render_answer_key_pages` flows answers
  with automatic page breaks when a type's answer block won't fit.
- **Color constants** — `NAVY #1B2B5E`, `BLACK #111111`,
  `LIGHT #f0f0eb`, `TAN #d8cfc4`, `GRAY_RULE #cccccc`. These are
  CLAUDE.md-pinned and shouldn't be changed.

Data shapes: `Problem`, `ProblemType`, `Worksheet` (all frozen
dataclasses).

### `verifier.py` — SymPy-based answer correctness

Routes a generated `Problem` to one of eight verifier functions by
`verifier_kind`. Eighth one (`claude_second_pass`) lives in
`problem_generator.py` since it requires an API call.

| Verifier kind | Pattern | Method |
|---|---|---|
| `combine_like_terms` | Polynomial sum/diff/perimeter | `simplify(body - answer) == 0` |
| `evaluate_at_x` | "If f(x) = …, what is f(N)?" | Substitute x=N, compare to claim |
| `geometric_ratio` | "Common ratio of 81, 27, 9, …" | Compute r, compare to claim |
| `geometric_term` | "What is f(4)?" given a, r | Compute `a · r^(n-1)`, compare |
| `classify_arith_geom` | "Is this arithmetic or geometric?" | Check both diffs and ratios |
| `explicit_rule` | "Write f(n) = a(r)^{n-1}" | Match a, r against body |
| `recursive_rule` | "Write f(1)=a, f(n)=r·f(n-1)" | Same, recursive form |
| `mc_match` | Any MC | Verify chosen letter's option text matches answer |

Plus **`correct_substitution_in_answer`** — a deterministic SymPy fix
for the highest-stakes generator failure mode. For word-problem
answers like `"Profit = 12x^3 - 40x^2 - 600; at x = 5, profit = $400"`,
it recomputes the dollar amount from the polynomial expression and
rewrites the answer if Claude's claimed value is wrong. This caught
real bugs where Claude correctly simplified the polynomial but
flubbed the multi-digit substitution arithmetic.

Markup translation (`_normalize`): `^N` → `**N`, Unicode minus
variants → ASCII `-`, curly-quote artifacts removed.

Test suite at `tests/test_verifier.py` — five passing cases and five
failing cases across five verifier kinds, with the failures modeling
real plausible generator bugs (sign errors, arith/geo mix-ups, wrong
substitution values, MC letter swaps, polynomial typos).

### `prompts.py` — Claude prompts as constants

Three prompt families:

- **`EXTRACT_TYPES_*`** — Opus 4.7, multimodal. Receives the test PDF as
  a `document` content block (handles both text and scanned PDFs
  without separate OCR), returns one JSON object with a `types` list.
  Each type carries `number`, `title`, `answer_key_title`,
  `instruction`, `layout`, `verifier_kind`, `pattern_description`,
  `example_problem`, `example_lines`, and (for `table`) `table_columns`.
- **`GENERATE_PROBLEM_*`** — Sonnet 4.6. Generates one fresh problem
  variant given the type spec, the canonical example, and the list of
  already-generated problems to avoid. Constraints baked into the
  system prompt: no Unicode superscripts, MC correct-letter shuffle,
  mathematical distinctness from excluded examples.
- **`VERIFY_WORD_PROBLEM_*`** — Sonnet 4.6. Solves a problem from
  scratch and reports whether the claimed answer matches. Used as the
  fallback for `claude_second_pass` and as a recovery path when the
  SymPy verifier raised a parse error (signal that `verifier_kind`
  was misassigned during extraction).
- **`MATH_DIFFICULTY_GUIDANCE` / `LANGUAGE_DIFFICULTY_GUIDANCE`** —
  Per-level guidance text injected into the generation prompt when the
  teacher dials Math or Language away from the default ("same"). The
  two axes are deliberately independent — special-ed students often
  have a math/reading split, so she can tune each one.

### `problem_generator.py` — Claude API integration

Public surface:

- `extract_problem_types(pdf_bytes) -> list[ExtractedTypeSpec]` — one
  Opus call, base64-encoded PDF as multimodal document.
- `generate_problem(spec, label, excluded, math_difficulty, language_difficulty) -> Problem`
  — one Sonnet call per problem.
- `verify_word_problem(problem, spec) -> VerificationResult` — one
  Sonnet call when the SymPy verifier doesn't apply.
- `generate_problem_with_retry(...)` — orchestrates generate +
  arithmetic correction + verify, retrying up to 2× with failed
  attempts appended to the excluded list (so the next retry won't
  regenerate the same wrong body).
- `estimate_cost(pdf_size_bytes, n_types, n_problems_per_type) -> CostEstimate`
  — surfaces a $low–$high range in the UI before the user commits to
  generation. Pricing baked in: Opus 4.7 at $15/$75 per 1M input/output;
  Sonnet 4.6 at $3/$15.

Two safeguards beyond the literal retry:
1. `correct_substitution_in_answer` runs before verification so a
   wrong dollar amount gets fixed deterministically rather than
   eating the retry budget.
2. SymPy parse errors on the verifier (Claude tends to misassign
   `combine_like_terms` to word problems whose body is a sentence)
   silently fall back to `verify_word_problem` instead of flagging.

`MissingAPIKey` raised early with a friendly message pointing the
user at the env var or the Streamlit Secrets UI.

`@lru_cache(maxsize=1)` on the Anthropic client so we don't
re-instantiate per call.

### `app.py` — Streamlit UI

Four-step state machine driven by `st.session_state.step`:

| Step | Function | What happens |
|---|---|---|
| Upload | `_render_upload_step` | File uploader, hash bytes, cost preview, "Continue" |
| Types | `_render_types_step` | Cached `extract_problem_types` (keyed on file hash so reruns don't re-bill), preview each type in an expander |
| Problems | `_render_problems_step` | Loop `generate_problem_with_retry` per (type, A–E), Approve / Regenerate / Edit per problem, ⚠️ on flagged |
| PDF | `_render_pdf_step` | Hand off to `render_worksheet`, serve via `st.download_button` |

Other UI elements:
- **Sidebar** (`_render_sidebar`) — brand mark + wordmark + step
  pill list. Each step row is one of three states: ✓ done, ● active,
  ○ pending.
- **Theme injection** — `assets/theme.css` loaded via `st.html` (not
  `st.markdown(unsafe_allow_html=True)` — newer Streamlit versions
  sanitize the latter). Literal `</style>` strings escaped before
  injection so the style block doesn't close early.
- **Inline styles for everything that has to look right** — Streamlit's
  HTML sanitizer drops class attributes on nested divs in some
  versions, so cards, hero gradients, and feature tiles bake colors
  into `style="..."` rather than relying on classes.
- **Two-tier visual hierarchy** — Step 1 (upload) gets a glacier-wash
  gradient hero with an oversized headline (the only marketing
  surface). Steps 2–4 stay Notion-quiet — 1px borders, no shadows,
  calm typography.
- **Difficulty knobs** — Math and Language sliders (Easier / Same /
  Harder) on the Problems step, threaded through into
  `generate_problem_with_retry`.
- **Worksheet title input** — teacher can override the default title
  before PDF render.
- **Loading overlay + PDF gate** — long generations get a full-screen
  spinner; the PDF step refuses to render if any problem is still
  unapproved unless the teacher hits "Accept anyway".
- **Friendly error surfaces** — `_render_api_key_error` and
  `_render_generic_error` for the two failure modes that should never
  crash the app.

### `tests/test_verifier.py`

10 pytest cases (5 pass, 5 fail) covering `combine_like_terms`,
`evaluate_at_x`, `geometric_ratio`, `classify_arith_geom`, and
`mc_match`. The failing cases are real plausible generator bugs —
this is the regression net for verifier behavior.

### Smoke tests

- `smoke_test_module16.py` (162 lines) — hand-built `Worksheet` for
  module 16 (polynomials), renders to `smoke_module16.pdf`. Exercises
  `centered`, `word_setup`, `word_blanks` layouts.
- `smoke_test_module13_14.py` (390 lines) — hand-built worksheet for
  modules 13/14 (exponential functions & geometric sequences),
  renders to `smoke_module13_14.pdf`. Exercises `mc_2col`, `mc_4row`,
  `short_answer_right`, `short_answer_below`, `table`.

Both are end-to-end PDF renders without any Claude API calls — they
verify the renderer in isolation against the canonical reference
PDFs.

## Brand & theme

### `brand/`

| File | Purpose |
|---|---|
| `mark.svg` | Glacier-teal checkmark with charcoal dot at upstroke tip, 64×64 viewBox |
| `mark-dark.svg` | Same mark, white dot, for dark backgrounds |
| `wordmark.svg` | "Round Two" in DM Sans Bold, 180×40 viewBox |
| `logo.svg` | Lockup: mark + wordmark side-by-side (canonical sidebar lockup) |
| `logo-dark.svg` | Dark-surface lockup |
| `favicon.svg`, `favicon-16/32/180.png`, `favicon.ico` | Favicons |
| `candidates/` | The three mark options proposed before selection — kept for record |

Mark geometry: 10pt stroke, round caps and joins, 4.5-radius dot.
Path: `M 16 34 L 27 46 L 50 18`.

### `assets/theme.css`

618 lines of CSS that:
- Loads DM Sans (400/500/600/700) and JetBrains Mono via Google Fonts
- Defines color tokens as CSS variables mirroring
  `reference/tailwind.config.js`
- Overrides Streamlit chrome (sidebar, buttons, inputs, expanders,
  file uploader, progress bar) to read as Notion-adjacent
- Provides utility classes (`.chip`, `.btn`, `.card`, `.label-faint`,
  `.wordmark`, `.step`)

Design rules pinned in CLAUDE.md and enforced here:
- 1px borders, never drop shadows on cards
- Primary CTAs are charcoal, never glacier or indigo
- No third color, no extra typeface
- Two-tier hierarchy: bold landing, quiet workflow

### `.streamlit/config.toml`

Streamlit's native theme tokens (charcoal primary, white background,
soft surface for sidebar). The CSS file extends this — Streamlit's
native theme can't express typography or component shapes.

### `.streamlit/secrets.toml.example`

Template showing where to paste `ANTHROPIC_API_KEY` for Streamlit
Community Cloud deployments.

## Reference materials

`reference/` contains the canonical input/output pairs (read-only):

- `module16_test.pdf` + `module16_practice_worksheet.pdf` — polynomials
  module. 4 types, all centered-expression layout plus two word
  problems.
- `module13_14_test.pdf` + `module13_14_practice_worksheet.pdf` —
  exponential functions & geometric sequences. 9 types covering
  multiple-choice (2-col and 4-row), classification table, and
  short-answer layouts.
- `tailwind.config.js` + `index.css` + `Logo.jsx` — design tokens
  inherited from Cold Open (the sibling project).

## Publish-prep artifacts

- `LICENSE` — MIT
- `README.md` — public-facing landing
- `requirements.txt` — pinned dependency floors (streamlit≥1.36,
  anthropic≥0.39, reportlab≥4.2, pdfplumber≥0.11, sympy≥1.13,
  pillow≥10.4, pytest≥8.0)
- `runtime.txt` — `python-3.11` (for Streamlit Community Cloud)
- `.gitignore` — standard Python + Streamlit + venv exclusions

## Build history

Roughly the order things landed:

1. **Brand** (`bf72ec6`) — three mark candidates, then selection,
   wordmark, lockup, and favicon set.
2. **Step 1 — renderer skeleton** (`03a0fab`) — minimal
   `worksheet_renderer.py`, smoke test against module 16.
3. **Typography fix** (`0490eb2`) — Helvetica weights and sizes
   matched against reference exactly.
4. **Step 2 — 5-problem distribution + exponent parser**
   (`26f2014`) — even-distribution math, separator clearance,
   `^N` and `^{...}` rendering.
5. **Step 3 — multi-page support + answer key** (`5e1f979`).
6. **Defer graphs** (`00de2ea`) — no graphs until a reference example
   exists; spec moved to CLAUDE.md.
7. **Step 4 — seven layout variants** (`84714e1`) — full reproduction
   of both reference PDFs.
8. **Publish prep** (`9e996dd`) — LICENSE, README, runtime, secrets
   template.
9. **Step 5a — verifier** (`b869a28`) — SymPy-based, eight kinds,
   test suite.
10. **Step 5b/5c — prompts + generator** (`54bbb77`).
11. **Step 5d — Streamlit app wiring it together** (`3adb42a`).
12. **CSS injection robustness** (`2466108`, `b09fb00`, `bd3c19e`) —
    survive sanitization quirks.
13. **UI redesign** (`d6f3400`) — Notion-style sidebar, Steps 2–4 quiet.
14. **Upload feature tiles** (`09b4620`, `b1f2bc0`).
15. **Worksheet title input + button-color fixes**
    (`d4a7230`, `6b41f73`).
16. **Inline-style hardening** (`bfa7d99`, `03ba2af`, `74e3b07`,
    `98ae05e`) — survive sanitization on the live deploy.
17. **Two-tier visual** (`81efd12`, `29e1f12`) — glacier-wash hero on
    upload, quiet internal steps.
18. **Word-blank work-area + arithmetic auto-correct**
    (`6aa9794`, `3a95e5b`, `90090a2`).
19. **Difficulty knobs** (`db08abf`) — Math and Language axes,
    Easier / Same / Harder.
20. **PDF gate + Accept-anyway + loading overlay** (`27039a5`).
21. **Verifier-kind misassignment fallback + brand lockup polish**
    (`776c479`).

## Out of scope (for now)

From CLAUDE.md, deliberately not built:

- User accounts / login
- Database / persistence of past worksheets
- Per-worksheet color or font customization
- Multi-language support
- Mobile-optimized UI
- Coordinate-grid graph rendering (deferred until a reference example
  arrives)
