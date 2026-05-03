# Worksheet Generator — Project Context

## What this project is

A Streamlit web app that lets a special education teacher upload a math
test PDF and generates a printable practice worksheet PDF with worked
examples, 5 practice problems per problem type, and an answer key.

The teacher reviews extracted problem types and generated problems
before the final PDF renders, so she can catch errors before printing.

## Reference implementation

`reference/make_worksheet_mod10.py` is a known-good ReportLab worksheet
the teacher has refined over many iterations. Treat its visual style as
canonical. `reference/module10_practice_worksheet.pdf` is its output —
match this look exactly.

When implementing the renderer, port helpers from the reference file
rather than reinventing them.

## Tech stack (don't substitute without asking)

- Python 3.11+
- streamlit — UI
- anthropic — Claude API client, model `claude-opus-4-7`
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
reference/              Module 10 reference files (read-only, don't edit)
```

## Visual style rules — DO NOT modify these

These came from real failures. Breaking them ships unusable PDFs.

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

178×178 pt, x_range (-10, 10), y_range (-10, 10), gridlines every 1,
labels every 2, arrows on positive x and y axes. Port directly from
the reference file.

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
