# Round Two — Project Context

## What this project is

**Round Two** is a Streamlit web app that lets a special education
teacher upload a math test her students just took and generates a
printable practice worksheet PDF — worked examples, 5 practice
problems per problem type, and an answer key — for them to rehearse
before retaking the test.

The teacher reviews extracted problem types and generated problems
before the final PDF renders, so she can catch errors before printing.

## Reference

Two known-good input/output PDF pairs are checked into `reference/`:

- `module16_test.pdf` + `module16_practice_worksheet.pdf` — polynomials
  (add/subtract, perimeter word problems, real-world applications).
  4 types, all centered-expression layout.
- `module13_14_test.pdf` + `module13_14_practice_worksheet.pdf` —
  exponential functions & geometric sequences. 9 types covering
  multiple-choice (2-col and 4-row), classification table, and
  short-answer layouts.

Treat the approved-output PDFs as the canonical visual targets. Match
them exactly: colors, spacing, fonts, example-box geometry, exponent
rendering.

## Tech stack (don't substitute without asking)

- Python 3.11+
- streamlit — UI
- anthropic — Claude API client. Two models:
  - `claude-opus-4-7` for type extraction (one orchestration call per upload)
  - `claude-sonnet-4-6` for per-problem generation and any
    word-problem second-pass verification (~5× cheaper, similar
    quality on this scoped task)
- reportlab — PDF generation (canvas-direct, NOT Platypus)
- pdfplumber — extract text from uploaded PDFs
- sympy — algebraic verification of generated answers
- pillow — for any image handling

Read `ANTHROPIC_API_KEY` from `os.environ`. Never hardcode it.

## File structure

```
app.py                  Streamlit UI, multi-step flow
worksheet_renderer.py   ReportLab template — preserves the canonical style
problem_generator.py    Claude API calls (extract types + generate problems)
verifier.py             SymPy algebraic verification
prompts.py              Claude prompts as constants
requirements.txt
CLAUDE.md               This file
.streamlit/config.toml  Streamlit native theme (color tokens)
assets/theme.css        Custom CSS injected into the app (typography, components)
brand/                  Logo, wordmark, lockups, favicons (see brand/README.md)
reference/              Input/output PDF pairs + cold-open style reference (read-only)
```

## Brand & UI

Round Two shares its visual language with Cold Open (a sibling project
the teacher and I built earlier). The app should read as a quiet,
Notion-adjacent dashboard.

**Brand assets** live in `brand/`. The mark is a single glacier-teal
checkmark with a charcoal dot at the tip of the upstroke; the wordmark
is "Round Two" in DM Sans Bold. Use `brand/logo.svg` as the canonical
sidebar lockup, `brand/favicon.svg` for the page icon, and the
matching `*-dark.svg` variants on dark surfaces.

**Design tokens** (mirror `reference/tailwind.config.js`):

```
glacier   #7CC0B8   primary brand color (mark stroke, brand surfaces)
charcoal  #0B1220   text-primary, primary CTA fill, mark dot
indigo    #4338CA   accent — focus rings only, never primary actions
amber     #F59E0B   "wins" — gentle celebrations, not alerts
white     #FFFFFF   bg, surface
F7F7F5    surface-soft (sidebar)
E5E5E2    border (defines blocks without shouting)
font-sans "DM Sans", system-ui, sans-serif
font-mono "JetBrains Mono"
```

**Streamlit theming** is two layers:
- `.streamlit/config.toml` sets the native color tokens.
- `assets/theme.css` is injected at the top of `app.py` via
  `st.markdown('<style>...</style>', unsafe_allow_html=True)` to load
  DM Sans, override Streamlit's chrome (buttons, inputs, expanders,
  sidebar, file uploader), and provide utility classes (`.chip`,
  `.btn`, `.card`, `.label-faint`, `.step`).

Do not introduce a third color, additional typeface, or shadow
elevation beyond what `tailwind.config.js` defines. Cards use a 1px
border, never a drop shadow. Primary CTAs are charcoal, never glacier
or indigo (the brand color is reserved for the mark and brand
surfaces).

## Visual style rules — DO NOT modify these

These came from real failures. Breaking them ships unusable PDFs.

> Note: this section governs the **PDF worksheet** style (NAVY etc.),
> not the app UI. The app UI follows the Brand & UI section above.

### 1. Never use Unicode superscripts

Helvetica renders ², ³, ⁴, etc. as black boxes. All exponents in problem
data MUST use `^2` or `^{10}` notation. The renderer parses this markup
and draws exponents as smaller raised text manually with
`canvas.drawString`.

### 2. Distribute problems evenly across the full page

Calculate `block_h = avail / num_problems` so problems fill the page
with working room. Never cluster problems at the top with empty space
at the bottom.

### 3. Separator clearance

Add `PAD_TOP = 28` so separators sit in whitespace and never intersect
problem headers:
- Draw content at `y - (PAD_TOP if i > 0 else 0)`
- Draw separator at `y - (i+1) * block_h - PAD_TOP/2`
- Use light gray `#cccccc`, line width 0.5

### 4. Color palette (constants)

```python
NAVY  = colors.HexColor("#1B2B5E")
BLACK = colors.HexColor("#111111")
LIGHT = colors.HexColor("#f0f0eb")  # example box fill
TAN   = colors.HexColor("#d8cfc4")  # example box border
```

### 5. Page anatomy

- Every page: header with title + Name/Date/Period blanks
- Each type's first page: section header (NAVY 12pt bold + horizontal
  rule), then example box (LIGHT fill, TAN border, "EXAMPLE — Look at
  this before you begin")
- 5 practice problems per type, distributed evenly
- Final page(s): answer key

### 6. Coordinate grids (for graph problems)

**Deferred until a reference example arrives.** Graph problems are rare
in the teacher's actual workload (seen once, example not available),
and there's no visual target in `reference/` — both PDF pairs are
graph-free. Don't build the coordinate-grid renderer speculatively.

When a graph-bearing test comes in, drop the input PDF + an approved
output PDF (even hand-marked) into `reference/` like the other pairs,
then implement to match. Spec to follow if needed: 178×178 pt, x_range
(-10, 10), y_range (-10, 10), gridlines every 1, labels every 2,
arrows on positive x and y axes — but don't trust the spec alone.

## Math correctness — non-negotiable

For every generated problem, run SymPy verification:

| Problem pattern | Method |
|---|---|
| Solve linear/quadratic | `parse_expr` + `solve()`, compare to claimed answer |
| System of equations | `solve()`, compare ordered pair |
| Substitute pair into inequality | Evaluate, compare truthiness |
| Polynomial multiplication | `expand()` both sides, check equality |
| Combine like terms | `simplify()` both sides, check equality |
| Word problem / graph | Second-pass Claude call: "Solve from scratch. Does answer match?" |

If verification fails, regenerate up to 2 times. If still failing,
flag with ⚠️ for human review in the UI. Never silently ship a
wrong answer.

## Streamlit UX requirements

- 4 steps via `st.session_state`: Upload → Types → Problems → PDF
- Sidebar progress indicator
- `@st.cache_data` keyed on file hash so reruns don't re-bill
- Show estimated cost before the generate step
- `st.spinner` during all Claude calls
- On JSON parse failure, show raw response and a Retry button — don't crash
- Each generated problem in an `st.expander` with Approve / Regenerate /
  Edit controls

## Out of scope

Don't build these unless I ask:
- User accounts / login
- Database / persistence of past worksheets
- Per-worksheet color or font customization
- Multi-language support
- Mobile-optimized UI

## How I want to work

- Build incrementally. Don't dump 800 lines at once.
- Suggested order: renderer first (port from reference), then verifier,
  then problem_generator, then app.py wiring it together.
- After each module, run a quick smoke test before moving on.
- Ask before adding new dependencies.
- Ask before changing anything in `reference/`.

## Acceptance test

When done, I'll upload a math test PDF. Output must:

1. Have Name/Date/Period header on every page
2. Show one worked example per type in a tan-bordered cream box
3. Contain exactly 5 practice problems per type
4. Distribute problems evenly down each page
5. Render exponents correctly (no black boxes, no Unicode superscripts)
6. Include a final answer key page
7. Open cleanly in Preview/Adobe with no errors
