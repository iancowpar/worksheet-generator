"""Round Two — Claude prompts as constants.

Three prompt families:

  EXTRACT_TYPES_*        Opus 4.7, multimodal: read a math test PDF and emit
                         structured ExtractedTypeSpec objects for the renderer
                         and generator to consume.
  GENERATE_PROBLEM_*     Sonnet 4.6: generate ONE fresh problem in the pattern
                         of a given type spec, avoiding any already-generated
                         duplicates.
  VERIFY_WORD_PROBLEM_*  Sonnet 4.6: solve a problem from scratch and report
                         whether the claimed answer matches. Used as the
                         fallback verifier for word problems and anything that
                         doesn't have a SymPy-based check.

These will need real-world iteration after the first end-to-end run. v1 is
the load-bearing skeleton — fields, layouts, verifier kinds — phrased to
keep Claude's outputs strictly machine-parseable.
"""

# --- Layouts and verifier kinds, kept here so the prompts and the renderer
# stay in lockstep. Order matters for human readability in the prompt text. ---

_LAYOUTS = """
  centered            A centered math expression like (3xy + 2xz - 4yz) + (-xy + 5xz + 2yz)
                      with a bold "Problem" label and a short prompt ("Find the sum.").
  word_setup          A word problem paragraph followed by a pre-filled setup line
                      indented from the margin, e.g., "P = (3x + 2) + (5x - 1) + (2x + 4)".
  word_blanks         A word problem paragraph followed by two-column inline blanks,
                      each blank labeled (e.g., "Profit expression:" and "If x = 5, profit =").
  mc_2col             4-option multiple choice in a 2-column 2-row grid (short options).
                      Order is A top-left, B bottom-left, C top-right, D bottom-right.
  mc_4row             4-option multiple choice with each option on its own row
                      (used when option text is too long for 2-col).
  short_answer_right  Short answer where the answer label (e.g., "r =") and a blank
                      sit on the same row as the Problem label, right-aligned.
  short_answer_below  Short answer where the answer label (e.g., "f(n) =") and a blank
                      sit on their own row beneath the problem paragraph.
  table               A single classification grid (e.g., Arithmetic vs Geometric).
                      Each row holds one sequence; the student marks the right cell.
""".strip()

_VERIFIER_KINDS = """
  combine_like_terms   Polynomial simplification — body simplifies to answer.
  evaluate_at_x        "If f(x) = ..., what is f(N)?" — substitute and compare.
  geometric_ratio      Find the common ratio of a sequence.
  geometric_term       Find the nth term of a geometric sequence.
  classify_arith_geom  Identify a sequence as arithmetic or geometric.
  recursive_rule       Recursive sequence rule, e.g., f(1) = a, f(n) = r·f(n-1).
  explicit_rule        Explicit sequence formula, e.g., f(n) = a(r)^{n-1}.
  mc_match             Any MC type — generic check that the chosen letter's option text
                       matches the canonical answer.
  claude_second_pass   Word problems or anything not covered above. Falls back to a
                       Claude solver call.
""".strip()


# ---------------------------------------------------------------------------
# Extract problem types from a test PDF
# ---------------------------------------------------------------------------

EXTRACT_TYPES_SYSTEM = f"""\
You are a math curriculum analyst. Given a high school math test PDF, you
identify groups of similar problems ("types") and extract a structured
description of each type so a downstream tool can generate practice
variants and render them onto a printable worksheet.

For each type, return:
  - number: 1-based index in the order the types appear on the test
  - title: a concise type title (e.g., "Adding Polynomials (Find the Sum)")
  - answer_key_title: a short form of the title for use in the answer key
                      (e.g., "Adding Polynomials")
  - instruction: the directive students see above the problems
                 (e.g., "Find each sum. Show all work. Circle your final answer.")
  - layout: one of these renderer-recognized layouts:
{_LAYOUTS}
  - verifier_kind: one of:
{_VERIFIER_KINDS}
  - pattern_description: 1-2 sentences detailed enough for a generator to
    produce a fresh variant. Specify variable names, coefficient ranges,
    and any structural constraints. Example:
    "Sum of two trinomials in variables drawn from {{a,b,c,m,n,r,s,x,y,z}}
     with integer coefficients between -12 and 12 inclusive, no zero terms."
  - example_problem: ONE representative problem from the test with these fields,
    used as the worked example in the rendered worksheet:
      label: a placeholder like "EX" (the renderer ignores this)
      body: the problem text with `^N` / `^{{...}}` exponent markup
            (NEVER use Unicode superscripts like ², ³, ⁴ — they render as black boxes)
      answer: the canonical answer
      // layout-specific fields below as relevant
      prompt: for `centered` only (e.g., "Find the sum.")
      options: for `mc_2col` and `mc_4row` (4-element list, A,B,C,D order)
      correct_letter: for MC layouts ("A"|"B"|"C"|"D")
      setup: for `word_setup` only (the pre-filled equation line)
      blanks: for `word_blanks` only (list of blank label strings)
      answer_label: for `short_answer_*` (e.g., "r =", "f(n) =")
  - example_lines: list of strings — the worked example shown in the cream/tan
    box at the top of each type's page. Walk through the solution step by step.
    Last line is the bold "Answer:" line.
  - table_columns: only for `table` layout (e.g., ["Arithmetic", "Geometric"]).
    Omit otherwise.

Output ONE JSON object with a single key "types" whose value is the list of
type objects in the order they appear on the test. Do not wrap the JSON in
markdown fences. Do not output any commentary before or after the JSON.

If the test contains graph-bearing problems (coordinate planes, function
plots), set verifier_kind to "claude_second_pass" — the renderer can't draw
graphs yet, so the teacher will need to handle those manually."""


EXTRACT_TYPES_USER = """\
Read the attached test PDF and extract every distinct problem type. Return
the JSON described above with no surrounding text."""


# ---------------------------------------------------------------------------
# Generate one problem variant for a given type
# ---------------------------------------------------------------------------

GENERATE_PROBLEM_SYSTEM = """\
You are a math problem generator for high school practice worksheets. Given
a type specification and a list of already-generated examples to avoid, you
produce ONE new problem in the same pattern with a correct, canonical answer.

Output a single JSON object with these fields (omit fields that don't apply
to the type's layout):

  label                 (provided in the user message; use it verbatim)
  body                  problem text — use `^N` / `^{...}` for exponents,
                        NEVER Unicode superscripts like ², ³, ⁴
  answer                canonical answer string
  prompt                centered layout only (e.g., "Find the sum.")
  options               MC only — 4-element list in A,B,C,D order
  correct_letter        MC only — single letter "A" | "B" | "C" | "D"
  setup                 word_setup only — pre-filled setup equation line
  blanks                word_blanks only — list of blank label strings
  answer_label          short_answer_* only (e.g., "r =", "f(n) =")

Constraints:
  - Output ONLY the JSON object. No markdown fences, no commentary.
  - The new problem must be mathematically distinct from every excluded
    example. Re-labelings or trivial coefficient swaps are NOT distinct.
  - The answer must be correct. If you make even a small mistake the
    downstream verifier will catch it and your work will be wasted.
  - Use the same coefficient style and complexity as the type's example.
  - For MC problems: shuffle the option positions so the correct answer
    isn't always (A) — distribute correct letters across the worksheet.
  - For exponents: x^2, m^{n-1}, NEVER x² or mⁿ⁻¹."""


GENERATE_PROBLEM_USER = """\
Type: {title}
Layout: {layout}
Pattern: {pattern_description}

Example (for reference only — do not reproduce or trivially modify):
{example_json}

Already generated for this type (avoid duplicating):
{excluded_bodies}
{answer_format_block}{calibration_block}
Generate problem {label} as JSON only."""


# Per-verifier answer-format contracts, injected into GENERATE_PROBLEM_USER.
# These exist because the downstream verifier matches the answer against a
# specific canonical shape; if Claude answers correctly but in a different
# format, the auto-check can't confirm it and the problem gets flagged. Pinning
# the exact format the verifier expects removes that whole class of false
# failures at the source. Keep these in lockstep with verifier.py.
ANSWER_FORMAT_GUIDANCE = {
    "combine_like_terms": (
        "The `answer` must be ONLY the fully simplified expression, e.g. "
        "\"2x^2 + 7x - 5\". No \"Answer:\" prefix, no prose, no restating the "
        "problem. Use `^` exponent markup, never Unicode superscripts."
    ),
    "evaluate_at_x": (
        "The `body` must literally contain \"f(x) = <expression>\" and ask for "
        "\"f(N)\" with a specific integer N. The `answer` must be "
        "\"f(N) = <value>\" with the SAME N, e.g. \"f(3) = 8\"."
    ),
    "geometric_ratio": (
        "The `body` must contain the sequence as comma-separated numbers ending "
        "in \"...\". The `answer` must be \"r = <value>\", e.g. \"r = 1/3\" "
        "(fractions allowed; reduce them)."
    ),
    "geometric_term": (
        "The `body` must give the sequence (or an explicit formula) and ask for a "
        "specific term. The `answer` must be ONLY that term's value, e.g. \"162\"."
    ),
    "classify_arith_geom": (
        "The `body` must be a comma-separated sequence ending in \"...\". The "
        "`answer` must be EXACTLY \"Arithmetic (d = <value>)\" or "
        "\"Geometric (r = <value>)\" — the correct classification with its "
        "common difference or common ratio."
    ),
    "recursive_rule": (
        "The `answer` must be EXACTLY \"f(1) = <a>, f(n) = <r> * f(n-1)\", e.g. "
        "\"f(1) = 5, f(n) = 3 * f(n-1)\". Use `*` for multiplication."
    ),
    "explicit_rule": (
        "The `answer` must be EXACTLY \"f(n) = <a>(<r>)^{{n-1}}\", e.g. "
        "\"f(n) = 5(3)^{{n-1}}\", where <a> is the first term and <r> the common "
        "ratio named in the body."
    ),
    "mc_match": (
        "Provide all 4 `options` (A,B,C,D order) and set `correct_letter`. The "
        "`answer` must be EXACTLY \"(<correct_letter>) <verbatim text of that "
        "option>\" — the text after the letter must match the chosen option "
        "character-for-character."
    ),
    "claude_second_pass": (
        "Make the `answer` self-contained and unambiguous: state the final "
        "result clearly (include units or a labeled value where the problem "
        "asks for one) so it can be checked by re-solving from scratch."
    ),
}


# Per-level guidance text injected into the difficulty calibration block
# in GENERATE_PROBLEM_USER. The "same" guidance instructs the model to
# mirror the canonical example; "easier" and "harder" describe concrete
# adjustments. Two axes (math + language) are deliberately independent
# because special-ed students often have a math/reading split — they can
# do the math but the wordy stems trip them up, or vice versa.

MATH_DIFFICULTY_GUIDANCE = {
    "easier": (
        "Make the math gentler than the example. Use single-digit coefficients "
        "where possible, fewer terms, and substitution values (typically x = 2, "
        "5, or 10) that yield clean integer answers. Skip cubic terms when a "
        "quadratic would teach the same concept. Avoid negative leading terms."
    ),
    "same": (
        "Mirror the example's mathematical complexity exactly — same coefficient "
        "magnitudes, same number of terms, same substitution-value range, same "
        "sign distribution. The student should feel the test's difficulty."
    ),
    "harder": (
        "Push slightly past the example's difficulty. Use 2-digit coefficients "
        "freely, include one extra term where natural, pick substitution values "
        "(say x = 7, 12, or 15) that demand real arithmetic, and use negative "
        "leading terms occasionally. Don't go to absurd numbers — this is a "
        "stretch, not a different course."
    ),
}

LANGUAGE_DIFFICULTY_GUIDANCE = {
    "easier": (
        "Use short sentences (under 12 words). Stick to common vocabulary — "
        "say 'cost' not 'operating expense', 'price' not 'unit revenue'. State "
        "every number explicitly rather than burying it in narrative. Cue the "
        "steps the student should take ('First, find the profit expression. "
        "Then evaluate at x = 5.'). One idea per sentence."
    ),
    "same": (
        "Match the example's reading level — sentence length, vocabulary, and "
        "scaffolding density should feel like the same author."
    ),
    "harder": (
        "Use longer multi-clause sentences. Reach for more sophisticated "
        "vocabulary ('revenue stream', 'operating expenses', 'net profit') "
        "where it fits naturally. Embed numbers in the story rather than "
        "calling them out. Drop scaffolding cues — the student must identify "
        "what to compute on their own. Don't introduce unfamiliar contexts."
    ),
}


# ---------------------------------------------------------------------------
# Second-pass verification for word problems / unhandled patterns
# ---------------------------------------------------------------------------

VERIFY_WORD_PROBLEM_SYSTEM = """\
You are a math correctness checker. Given a problem body and a claimed
answer, you solve the problem from scratch and report whether the claimed
answer matches your computation.

Output a single JSON object with these fields:
  verified      boolean — true if your computed answer matches the claim
  computed      your computed answer in the same canonical form as the claim
  explanation   one sentence describing your reasoning

Output ONLY the JSON. No markdown fences, no commentary."""


VERIFY_WORD_PROBLEM_USER = """\
Problem:
{body}

Claimed answer:
{answer}

Solve from scratch and report whether the claim is correct."""
