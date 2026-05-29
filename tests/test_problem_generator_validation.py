"""Generation-shape validation tests.

These checks protect the trust layer around the LLM: a mathematically correct
answer is not enough if the generated object is malformed for the renderer or
contains glyphs that print as boxes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import problem_generator as pg  # noqa: E402
from problem_generator import ExtractedTypeSpec  # noqa: E402
from worksheet_renderer import Problem  # noqa: E402


def _spec(layout: str = "centered", verifier_kind: str = "combine_like_terms") -> ExtractedTypeSpec:
    return ExtractedTypeSpec(
        number=1,
        title="Adding Polynomials",
        instruction="Find each sum.",
        layout=layout,
        verifier_kind=verifier_kind,
        pattern_description="Add two binomials.",
        example_lines=["(x + 1) + (x + 2)", "Answer: 2x + 3"],
        example_problem=Problem(
            label="EX",
            prompt="Find the sum.",
            body="(x + 1) + (x + 2)",
            answer="2x + 3",
        ),
    )


def test_validation_rejects_unicode_superscripts():
    problem = Problem(
        label="1-A",
        prompt="Find the sum.",
        body="x² + 2x",
        answer="x² + 2x",
    )
    result = pg._validate_generated_problem(problem, _spec(), "1-A", [])
    assert not result.ok
    assert "unicode superscripts" in result.reason


def test_validation_rejects_duplicate_body():
    excluded = [Problem(label="EX", prompt="Find the sum.", body="x + 1", answer="x + 1")]
    problem = Problem(label="1-A", prompt="Find the sum.", body="  X   + 1  ", answer="x + 1")
    result = pg._validate_generated_problem(problem, _spec(), "1-A", excluded)
    assert not result.ok
    assert "duplicates" in result.reason


def test_validation_rejects_missing_word_setup():
    problem = Problem(label="1-A", body="Find the perimeter.", answer="P = 2x + 4")
    result = pg._validate_generated_problem(problem, _spec("word_setup"), "1-A", [])
    assert not result.ok
    assert "requires setup" in result.reason


def test_validation_rejects_bad_mc_shape():
    problem = Problem(
        label="1-A",
        body="Which function is increasing?",
        answer="(E) y = 2^x",
        options=["y = 2^x", "y = 2^x", "y = 3^x"],
        correct_letter="E",
    )
    result = pg._validate_generated_problem(problem, _spec("mc_2col", "mc_match"), "1-A", [])
    assert not result.ok
    assert "exactly four options" in result.reason


def test_retry_recovers_from_structurally_invalid_generation(monkeypatch):
    spec = _spec()
    generated = [
        Problem(label="1-A", prompt="", body="x² + 1", answer="x² + 1"),
        Problem(label="1-A", prompt="Find the sum.", body="(x + 3) + (x + 4)", answer="2x + 7"),
    ]

    def fake_generate_problem(*args, **kwargs):
        return generated.pop(0)

    monkeypatch.setattr(pg, "generate_problem", fake_generate_problem)
    result = pg.generate_problem_with_retry(spec, "1-A", [], max_retries=1)
    assert result.verification.ok
    assert result.problem.body == "(x + 3) + (x + 4)"
    assert result.attempts == 2
