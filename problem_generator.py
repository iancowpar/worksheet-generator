"""Round Two — problem generator.

Three responsibilities:

  extract_problem_types(pdf_bytes)       one multimodal extraction call;
                                         returns ExtractedTypeSpec list
  generate_problem(spec, exclude)        one generation call per problem
  verify_word_problem(problem, spec)     one verifier call when the
                                         verifier_kind is claude_second_pass

The retry loop in `generate_problem_with_retry` calls the SymPy verifier
(verifier.verify) for kinds it knows, and falls back to verify_word_problem
for `claude_second_pass`. After max_retries failures the problem is returned
as-is, and the caller can flag it for human review based on the returned
GeneratedProblem.verification.ok status.

Provider-specific client setup lives in llm_provider.py. This module owns the
prompt assembly, JSON parsing, generated problem shape, and retry behavior.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from llm_provider import MissingAPIKey, get_llm_provider
from prompts import (
    ANSWER_FORMAT_GUIDANCE,
    EXTRACT_TYPES_SYSTEM,
    EXTRACT_TYPES_USER,
    GENERATE_PROBLEM_SYSTEM,
    GENERATE_PROBLEM_USER,
    LANGUAGE_DIFFICULTY_GUIDANCE,
    MATH_DIFFICULTY_GUIDANCE,
    VERIFY_WORD_PROBLEM_SYSTEM,
    VERIFY_WORD_PROBLEM_USER,
)


# Difficulty level keys used by generate_problem and the Streamlit UI.
# Default is "same" (mirror the canonical example).
DIFFICULTY_LEVELS = ("easier", "same", "harder")
DEFAULT_DIFFICULTY = "same"
from verifier import VerificationResult, correct_substitution_in_answer, verify
from worksheet_renderer import Problem, ProblemType

_SUPPORTED_LAYOUTS = {
    "centered",
    "word_setup",
    "word_blanks",
    "mc_2col",
    "mc_4row",
    "short_answer_right",
    "short_answer_below",
    "table",
}
_MC_LAYOUTS = {"mc_2col", "mc_4row"}
_UNICODE_SUPERSCRIPT_RE = re.compile(r"[\u00b2\u00b3\u00b9\u2070-\u209f]")


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExtractedTypeSpec:
    """A type's structure extracted from the input test, plus enough metadata
    for the generator and verifier to produce variants."""
    number: int
    title: str
    instruction: str
    layout: str
    verifier_kind: str
    pattern_description: str
    example_lines: list[str]
    example_problem: Problem
    answer_key_title: str | None = None
    table_columns: list[str] | None = None

    def to_problem_type(self, problems: list[Problem]) -> ProblemType:
        """Pair this spec with a list of generated problems to produce a
        renderer-ready ProblemType."""
        return ProblemType(
            number=self.number,
            title=self.title,
            instruction=self.instruction,
            example_lines=self.example_lines,
            problems=problems,
            answer_key_title=self.answer_key_title,
            layout=self.layout,
            table_columns=self.table_columns,
        )


@dataclass(frozen=True)
class GeneratedProblem:
    """A generated problem and the result of its verification."""
    problem: Problem
    verification: VerificationResult
    attempts: int


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_problem_types(pdf_bytes: bytes) -> list[ExtractedTypeSpec]:
    """Send the test PDF to the configured AI provider and parse the response.

    The PDF is passed as a multimodal `document` content block. This handles
    both text-based and scanned PDFs when the provider supports PDF input."""
    raw = get_llm_provider().extract_problem_types(
        pdf_bytes, EXTRACT_TYPES_SYSTEM, EXTRACT_TYPES_USER
    )
    data = _extract_json(raw)
    if "types" not in data or not isinstance(data["types"], list):
        raise ValueError(f"extract response missing 'types' list: {raw[:300]}")

    return [_parse_type_spec(item) for item in data["types"]]


def generate_problem(
    spec: ExtractedTypeSpec,
    label: str,
    excluded: list[Problem],
    math_difficulty: str = DEFAULT_DIFFICULTY,
    language_difficulty: str = DEFAULT_DIFFICULTY,
) -> Problem:
    """Generate one fresh problem variant for `spec`, using `excluded` as
    de-duplication context. `math_difficulty` and `language_difficulty` are
    independent axes — special-ed students often have a math/reading split
    so the teacher can dial them separately. The returned Problem carries
    `label` verbatim."""
    example_json = json.dumps(_problem_to_dict(spec.example_problem), indent=2)
    excluded_bodies = "\n".join(f"  - {p.body}" for p in excluded) or "  (none)"

    # Only include the difficulty-calibration block when at least one axis
    # is non-default. For "same/same" the prompt collapses back to the
    # original text — adding redundant "mirror the example exactly" prose
    # was hurting generation quality.
    calibration_lines = []
    if math_difficulty != DEFAULT_DIFFICULTY:
        calibration_lines.append(f"- Math: {MATH_DIFFICULTY_GUIDANCE[math_difficulty]}")
    if language_difficulty != DEFAULT_DIFFICULTY:
        calibration_lines.append(
            f"- Language: {LANGUAGE_DIFFICULTY_GUIDANCE[language_difficulty]}"
        )
    calibration_block = ""
    if calibration_lines:
        calibration_block = (
            "\nDifficulty calibration:\n" + "\n".join(calibration_lines) + "\n"
        )

    # Pin the exact answer format the verifier for this kind expects, so a
    # correct answer in an off-spec format doesn't get flagged downstream.
    format_guidance = ANSWER_FORMAT_GUIDANCE.get(spec.verifier_kind)
    answer_format_block = (
        f"Answer format (must follow exactly):\n{format_guidance}\n\n"
        if format_guidance else ""
    )

    user = GENERATE_PROBLEM_USER.format(
        title=spec.title,
        layout=spec.layout,
        pattern_description=spec.pattern_description,
        example_json=example_json,
        excluded_bodies=excluded_bodies,
        answer_format_block=answer_format_block,
        calibration_block=calibration_block,
        label=label,
    )

    raw = get_llm_provider().generate_problem(GENERATE_PROBLEM_SYSTEM, user)
    data = _extract_json(raw)
    data["label"] = label  # enforce caller-provided label
    return _parse_problem(data, spec.layout)


def verify_word_problem(problem: Problem, spec: ExtractedTypeSpec) -> VerificationResult:
    """Second-pass provider verification for word problems and any kind that
    falls through to claude_second_pass."""
    user = VERIFY_WORD_PROBLEM_USER.format(
        body=problem.body,
        answer=problem.answer,
    )
    raw = get_llm_provider().verify_word_problem(VERIFY_WORD_PROBLEM_SYSTEM, user)
    data = _extract_json(raw)
    return VerificationResult(
        ok=bool(data.get("verified", False)),
        reason=str(data.get("explanation", "")),
        details={"computed": data.get("computed")},
    )


def _merge_unverified(
    sympy_result: VerificationResult, claude_result: VerificationResult
) -> VerificationResult:
    """Combine a SymPy 'couldn't check' result with a failing provider second
    pass into one flag with a reason that helps the teacher understand why a
    problem needs review — neither checker could confirm the answer."""
    parts = []
    if claude_result.reason:
        parts.append(f"second-pass check: {claude_result.reason}")
    if sympy_result.reason:
        parts.append(f"auto-check: {sympy_result.reason}")
    return VerificationResult(
        ok=False,
        reason="; ".join(parts) or "could not verify answer",
        details={**sympy_result.details, **claude_result.details},
        checked=claude_result.checked,
    )


def generate_problem_with_retry(
    spec: ExtractedTypeSpec,
    label: str,
    excluded: list[Problem],
    max_retries: int = 2,
    math_difficulty: str = DEFAULT_DIFFICULTY,
    language_difficulty: str = DEFAULT_DIFFICULTY,
) -> GeneratedProblem:
    """Generate then verify, retrying on failure up to `max_retries` times.

    Two safeguards beyond the literal retry:
      1. For word-blank answers (e.g. "Profit = ...; at x = N, profit = $K"),
         recompute K with SymPy before verifying. Claude is unreliable for
         multi-digit polynomial arithmetic, and a wrong dollar amount is
         the highest-stakes failure mode — wife-won't-use-it territory.
      2. Failed attempts get appended to the excluded list so the next
         retry doesn't regenerate the same wrong body.
    """
    last_problem: Problem | None = None
    last_result: VerificationResult | None = None
    seen = list(excluded)  # local copy — don't mutate the caller's list

    for attempt in range(max_retries + 1):
        problem = generate_problem(
            spec, label, seen,
            math_difficulty=math_difficulty,
            language_difficulty=language_difficulty,
        )

        structure_result = _validate_generated_problem(problem, spec, label, seen)
        if not structure_result.ok:
            last_problem, last_result = problem, structure_result
            seen.append(problem)
            continue

        problem, status = correct_substitution_in_answer(problem)

        if spec.verifier_kind == "claude_second_pass":
            result = verify_word_problem(problem, spec)
        else:
            result = verify(problem, spec.verifier_kind)
            # When the SymPy verifier couldn't actually evaluate the answer
            # (couldn't parse the expression, extract the sequence, or match
            # the answer format — `checked=False`), it has NOT found a math
            # error. Flagging here was the main source of false "can't verify
            # the answer" failures: a correct answer in a slightly-off format
            # would block the whole worksheet. Defer to the Claude second-pass
            # for a real solve-from-scratch check instead.
            #
            # A `checked=True` failure means SymPy solved it and the claim is
            # genuinely wrong — that we trust, and let the retry loop handle.
            if not result.ok and not result.checked:
                claude_result = verify_word_problem(problem, spec)
                # Preserve the SymPy diagnostic if Claude also can't confirm,
                # so the flagged reason stays useful for human review.
                result = claude_result if claude_result.ok else _merge_unverified(
                    sympy_result=result, claude_result=claude_result
                )

        if result.ok:
            return GeneratedProblem(problem=problem, verification=result, attempts=attempt + 1)

        last_problem, last_result = problem, result
        seen.append(problem)

    return GeneratedProblem(
        problem=last_problem,  # type: ignore[arg-type]
        verification=last_result,  # type: ignore[arg-type]
        attempts=max_retries + 1,
    )


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

@dataclass
class CostEstimate:
    """Rough per-worksheet cost in US dollars, based on published 2026 prices.

    Pricing (input / output per million tokens):
      Opus 4.7 (extraction): $15 / $75
      Sonnet 4.6 (generation, verification): $3 / $15
    """
    input_tokens: int
    output_tokens: int
    n_types: int
    n_problems_per_type: int
    dollars_low: float
    dollars_high: float


def estimate_cost(pdf_size_bytes: int, n_types: int = 4, n_problems_per_type: int = 5) -> CostEstimate:
    """Rough estimate for the upcoming worksheet generation. Used to surface
    a cost preview in the UI before the user commits to the generate step."""
    # Extraction: the PDF dominates. Anthropic counts ~750 input tokens per page
    # for a typical document; a 9-MB scanned PDF tends to be 2-4 pages.
    pages = max(1, pdf_size_bytes // (3 * 1024 * 1024))
    extract_in = 1500 + 750 * pages  # system prompt + PDF
    extract_out = 2000  # the JSON response

    # Per-problem generation
    gen_in = 600  # type spec + exclusions + system prompt
    gen_out = 400  # the problem JSON

    # Verification (Claude second-pass: assume ~30% of problems fall here)
    verify_calls = int(n_types * n_problems_per_type * 0.3)
    verify_in = 200
    verify_out = 200

    n = n_types * n_problems_per_type
    total_in = extract_in + n * gen_in + verify_calls * verify_in
    total_out = extract_out + n * gen_out + verify_calls * verify_out

    # Mix: extraction is Opus; generation+verification is Sonnet.
    opus_cost = (extract_in / 1_000_000 * 15.0) + (extract_out / 1_000_000 * 75.0)
    sonnet_in = total_in - extract_in
    sonnet_out = total_out - extract_out
    sonnet_cost = (sonnet_in / 1_000_000 * 3.0) + (sonnet_out / 1_000_000 * 15.0)
    base = opus_cost + sonnet_cost

    # Retries can roughly double the generation cost in pathological cases.
    return CostEstimate(
        input_tokens=total_in,
        output_tokens=total_out,
        n_types=n_types,
        n_problems_per_type=n_problems_per_type,
        dollars_low=round(base, 2),
        dollars_high=round(base * 2.0, 2),
    )


# ---------------------------------------------------------------------------
# Response parsing helpers
# ---------------------------------------------------------------------------

def _validate_generated_problem(
    problem: Problem,
    spec: ExtractedTypeSpec,
    expected_label: str,
    excluded: list[Problem],
) -> VerificationResult:
    """Catch malformed generation before math verification.

    The SymPy verifier can prove an answer, but it cannot tell us that a
    multiple-choice problem forgot its options, a word setup omitted the setup
    line, or Claude used Unicode superscripts that render as black boxes in
    Helvetica. Those are trust failures too, so they trigger a retry.
    """
    failures: list[str] = []

    if spec.layout not in _SUPPORTED_LAYOUTS:
        failures.append(f"unsupported layout '{spec.layout}'")
    if problem.label != expected_label:
        failures.append(f"label '{problem.label}' != expected '{expected_label}'")
    if not problem.body.strip():
        failures.append("body is empty")
    if not problem.answer.strip():
        failures.append("answer is empty")
    if _body_matches_any(problem, excluded):
        failures.append("body duplicates an excluded/example problem")

    superscript_fields = _fields_with_unicode_superscripts(problem)
    if superscript_fields:
        failures.append(
            "unicode superscripts found in " + ", ".join(sorted(superscript_fields))
        )

    if spec.layout == "centered" and not problem.prompt.strip():
        failures.append("centered layout requires prompt")
    elif spec.layout == "word_setup" and not (problem.setup or "").strip():
        failures.append("word_setup layout requires setup")
    elif spec.layout == "word_blanks":
        if not problem.blanks or len([b for b in problem.blanks if b.strip()]) < 2:
            failures.append("word_blanks layout requires at least two blank labels")
    elif spec.layout in _MC_LAYOUTS:
        failures.extend(_validate_mc_shape(problem))
    elif spec.layout == "short_answer_below" and not (problem.answer_label or "").strip():
        failures.append("short_answer_below layout requires answer_label")
    elif spec.layout == "table":
        if problem.options or problem.correct_letter:
            failures.append("table layout should not include multiple-choice fields")

    if failures:
        return VerificationResult(
            ok=False,
            reason="invalid generated problem: " + "; ".join(failures),
            details={"layout": spec.layout, "label": expected_label},
            checked=True,
        )
    return VerificationResult(ok=True, reason="generated problem structure is valid")


def _validate_mc_shape(problem: Problem) -> list[str]:
    failures: list[str] = []
    if not problem.options or len(problem.options) != 4:
        failures.append("MC layout requires exactly four options")
        return failures
    if any(not option.strip() for option in problem.options):
        failures.append("MC options must be nonempty")
    normalized_options = [_normalize_problem_text(option) for option in problem.options]
    if len(set(normalized_options)) != 4:
        failures.append("MC options must be distinct")
    if problem.correct_letter not in ("A", "B", "C", "D"):
        failures.append(f"MC correct_letter must be A-D, got '{problem.correct_letter}'")
    return failures


def _body_matches_any(problem: Problem, excluded: list[Problem]) -> bool:
    body = _normalize_problem_text(problem.body)
    return any(body == _normalize_problem_text(other.body) for other in excluded)


def _normalize_problem_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _fields_with_unicode_superscripts(problem: Problem) -> set[str]:
    fields: dict[str, str] = {
        "body": problem.body,
        "answer": problem.answer,
        "prompt": problem.prompt,
        "setup": problem.setup or "",
        "answer_label": problem.answer_label or "",
    }
    if problem.blanks:
        fields.update({f"blank[{i}]": value for i, value in enumerate(problem.blanks)})
    if problem.options:
        fields.update({f"option[{i}]": value for i, value in enumerate(problem.options)})
    return {name for name, value in fields.items() if _UNICODE_SUPERSCRIPT_RE.search(value)}


def _extract_json(text: str) -> dict:
    """Best-effort JSON extraction from a Claude response. Tolerates leading
    commentary, markdown fences, and trailing prose — but the prompts ask for
    JSON-only output, so the direct path should hit most of the time."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        candidate = text[start : end + 1]
        return json.loads(candidate)
    raise ValueError(f"couldn't extract JSON from response: {text[:300]}")


def _parse_type_spec(data: dict) -> ExtractedTypeSpec:
    """Build an ExtractedTypeSpec from the JSON returned by EXTRACT_TYPES.

    Runs the extracted example_problem through correct_substitution_in_answer
    so the worked example shown to students has correct arithmetic — wrong
    example math is the most visible failure (it sits in a tan-bordered box
    at the top of the section labelled "Look at this before you begin")."""
    example_data = data.get("example_problem") or {}
    example_problem = _parse_problem(example_data, data.get("layout", "centered"))
    example_problem, _ = correct_substitution_in_answer(example_problem)
    return ExtractedTypeSpec(
        number=int(data["number"]),
        title=str(data["title"]),
        instruction=str(data["instruction"]),
        layout=str(data["layout"]),
        verifier_kind=str(data["verifier_kind"]),
        pattern_description=str(data["pattern_description"]),
        example_lines=list(data.get("example_lines") or []),
        example_problem=example_problem,
        answer_key_title=data.get("answer_key_title"),
        table_columns=list(data["table_columns"]) if data.get("table_columns") else None,
    )


def _parse_problem(data: dict, layout: str) -> Problem:
    """Build a Problem from the JSON returned by EXTRACT_TYPES (example_problem)
    or GENERATE_PROBLEM. Layout-specific fields are pulled in only if present."""
    return Problem(
        label=str(data.get("label", "")),
        body=str(data.get("body", "")),
        answer=str(data.get("answer", "")),
        prompt=str(data.get("prompt", "")),
        setup=data.get("setup"),
        blanks=list(data["blanks"]) if data.get("blanks") else None,
        options=list(data["options"]) if data.get("options") else None,
        correct_letter=data.get("correct_letter"),
        answer_label=data.get("answer_label"),
    )


def _problem_to_dict(p: Problem) -> dict:
    """Inverse of _parse_problem. Used to serialize the example_problem into
    the user-message body for GENERATE_PROBLEM."""
    out: dict = {"label": p.label, "body": p.body, "answer": p.answer}
    if p.prompt:
        out["prompt"] = p.prompt
    if p.setup:
        out["setup"] = p.setup
    if p.blanks:
        out["blanks"] = list(p.blanks)
    if p.options:
        out["options"] = list(p.options)
    if p.correct_letter:
        out["correct_letter"] = p.correct_letter
    if p.answer_label:
        out["answer_label"] = p.answer_label
    return out
