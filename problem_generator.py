"""Round Two — problem generator (Claude API integration).

Three responsibilities:

  extract_problem_types(pdf_bytes)       one Opus 4.7 multimodal call;
                                         returns ExtractedTypeSpec list
  generate_problem(spec, exclude)        one Sonnet 4.6 call per problem
  verify_word_problem(problem, spec)     one Sonnet 4.6 call when the
                                         verifier_kind is claude_second_pass

The retry loop in `generate_problem_with_retry` calls the SymPy verifier
(verifier.verify) for kinds it knows, and falls back to verify_word_problem
for `claude_second_pass`. After max_retries failures the problem is returned
as-is, and the caller can flag it for human review based on the returned
GeneratedProblem.verification.ok status.

ANTHROPIC_API_KEY is read from os.environ. The module raises a friendly
RuntimeError if it's missing — callers (the Streamlit app) should catch
that and surface a setup-the-key message rather than crashing.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache

from anthropic import Anthropic

from prompts import (
    EXTRACT_TYPES_SYSTEM,
    EXTRACT_TYPES_USER,
    GENERATE_PROBLEM_SYSTEM,
    GENERATE_PROBLEM_USER,
    VERIFY_WORD_PROBLEM_SYSTEM,
    VERIFY_WORD_PROBLEM_USER,
)
from verifier import VerificationResult, verify
from worksheet_renderer import Problem, ProblemType


OPUS_MODEL = "claude-opus-4-7"
SONNET_MODEL = "claude-sonnet-4-6"
EXTRACT_MAX_TOKENS = 8192
GENERATE_MAX_TOKENS = 2048
VERIFY_MAX_TOKENS = 1024


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
# Anthropic client
# ---------------------------------------------------------------------------

class MissingAPIKey(RuntimeError):
    """ANTHROPIC_API_KEY isn't set in the environment."""


@lru_cache(maxsize=1)
def _client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise MissingAPIKey(
            "ANTHROPIC_API_KEY is not set. For local dev, export it; for "
            "Streamlit Community Cloud, paste it into the app's Secrets UI. "
            "See .streamlit/secrets.toml.example on the publish-prep branch."
        )
    return Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_problem_types(pdf_bytes: bytes) -> list[ExtractedTypeSpec]:
    """Send the test PDF to Claude Opus and parse the structured response.

    The PDF is passed as a multimodal `document` content block. This handles
    both text-based and scanned PDFs without requiring a separate OCR step."""
    import base64
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("ascii")

    response = _client().messages.create(
        model=OPUS_MODEL,
        max_tokens=EXTRACT_MAX_TOKENS,
        system=EXTRACT_TYPES_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64,
                    },
                },
                {"type": "text", "text": EXTRACT_TYPES_USER},
            ],
        }],
    )
    raw = _response_text(response)
    data = _extract_json(raw)
    if "types" not in data or not isinstance(data["types"], list):
        raise ValueError(f"extract response missing 'types' list: {raw[:300]}")

    return [_parse_type_spec(item) for item in data["types"]]


def generate_problem(spec: ExtractedTypeSpec, label: str, excluded: list[Problem]) -> Problem:
    """Generate one fresh problem variant for `spec`, using `excluded` as
    de-duplication context. The returned Problem carries `label` verbatim."""
    example_json = json.dumps(_problem_to_dict(spec.example_problem), indent=2)
    excluded_bodies = "\n".join(f"  - {p.body}" for p in excluded) or "  (none)"

    user = GENERATE_PROBLEM_USER.format(
        title=spec.title,
        layout=spec.layout,
        pattern_description=spec.pattern_description,
        example_json=example_json,
        excluded_bodies=excluded_bodies,
        label=label,
    )

    response = _client().messages.create(
        model=SONNET_MODEL,
        max_tokens=GENERATE_MAX_TOKENS,
        system=GENERATE_PROBLEM_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    raw = _response_text(response)
    data = _extract_json(raw)
    data["label"] = label  # enforce caller-provided label
    return _parse_problem(data, spec.layout)


def verify_word_problem(problem: Problem, spec: ExtractedTypeSpec) -> VerificationResult:
    """Second-pass Claude verification for word problems and any kind that
    falls through to claude_second_pass."""
    user = VERIFY_WORD_PROBLEM_USER.format(
        body=problem.body,
        answer=problem.answer,
    )
    response = _client().messages.create(
        model=SONNET_MODEL,
        max_tokens=VERIFY_MAX_TOKENS,
        system=VERIFY_WORD_PROBLEM_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    raw = _response_text(response)
    data = _extract_json(raw)
    return VerificationResult(
        ok=bool(data.get("verified", False)),
        reason=str(data.get("explanation", "")),
        details={"computed": data.get("computed")},
    )


def generate_problem_with_retry(
    spec: ExtractedTypeSpec,
    label: str,
    excluded: list[Problem],
    max_retries: int = 2,
) -> GeneratedProblem:
    """Generate then verify, retrying on failure up to `max_retries` times.
    Returns the best-effort result with the verification status attached so
    the caller can flag failures for human review without blocking output."""
    last_problem: Problem | None = None
    last_result: VerificationResult | None = None
    for attempt in range(max_retries + 1):
        problem = generate_problem(spec, label, excluded)
        if spec.verifier_kind == "claude_second_pass":
            result = verify_word_problem(problem, spec)
        else:
            result = verify(problem, spec.verifier_kind)
        if result.ok:
            return GeneratedProblem(problem=problem, verification=result, attempts=attempt + 1)
        last_problem, last_result = problem, result
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

def _response_text(response) -> str:
    """Concatenate text blocks from a messages.create response."""
    parts = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


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
    """Build an ExtractedTypeSpec from the JSON returned by EXTRACT_TYPES."""
    example_data = data.get("example_problem") or {}
    example_problem = _parse_problem(example_data, data.get("layout", "centered"))
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
