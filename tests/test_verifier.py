"""Verifier test suite — five passing cases and five failing cases, exercising
five of the eight verifier kinds. The failing cases are real plausible bugs
the generator could produce (sign errors, arithmetic-vs-geometric mix-ups,
wrong substitution values, MC letter swaps, polynomial typos)."""

from __future__ import annotations

import sys
from pathlib import Path

# Make project root importable when pytest is run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from verifier import correct_substitution_in_answer, verify  # noqa: E402
from worksheet_renderer import Problem  # noqa: E402


# ---------------------------------------------------------------------------
# Passing cases
# ---------------------------------------------------------------------------

def test_combine_like_terms_passes_polynomial_addition():
    p = Problem(
        label="1-A",
        prompt="Find the sum.",
        body="(3xy + 2xz - 4yz) + (-xy + 5xz + 2yz)",
        answer="2xy + 7xz - 2yz",
    )
    result = verify(p, "combine_like_terms")
    assert result.ok, result.reason


def test_combine_like_terms_passes_with_exponents():
    p = Problem(
        label="1-C",
        prompt="Find the sum.",
        body="(4m^2n - 3mn^2 + 2mn) + (-m^2n + 5mn^2 - 7mn)",
        answer="3m^2n + 2mn^2 - 5mn",
    )
    result = verify(p, "combine_like_terms")
    assert result.ok, result.reason


def test_geometric_ratio_passes():
    p = Problem(
        label="7-A",
        body="What is the common ratio of the sequence 81, 27, 9, 3, 1, ...?",
        answer="r = 1/3",
        answer_label="r =",
    )
    result = verify(p, "geometric_ratio")
    assert result.ok, result.reason


def test_classify_arith_geom_passes_arithmetic():
    p = Problem(
        label="6-A",
        body="78, 69, 60, 51, 42, ...",
        answer="Arithmetic (d = -9)",
    )
    result = verify(p, "classify_arith_geom")
    assert result.ok, result.reason


def test_mc_match_passes():
    p = Problem(
        label="1-A",
        body="Which exponential function passes through the points (0, 18) and (1, 6)?",
        options=["y = 6(1/3)^x", "y = 18(1/3)^x", "y = 18(3)^x", "y = 6(3)^x"],
        correct_letter="B",
        answer="(B) y = 18(1/3)^x",
    )
    result = verify(p, "mc_match")
    assert result.ok, result.reason


# ---------------------------------------------------------------------------
# Failing cases — each exercises a different real-world bug pattern
# ---------------------------------------------------------------------------

def test_combine_like_terms_fails_on_sign_error():
    """The generator dropped a negative sign in the answer."""
    p = Problem(
        label="bug-1",
        prompt="Find the sum.",
        body="(3xy + 2xz - 4yz) + (-xy + 5xz + 2yz)",
        answer="2xy + 7xz + 2yz",  # should be -2yz
    )
    result = verify(p, "combine_like_terms")
    assert not result.ok


def test_geometric_ratio_fails_on_arithmetic_sequence():
    """The generator labeled an arithmetic sequence with a 'common ratio'."""
    p = Problem(
        label="bug-2",
        body="What is the common ratio of the sequence 1, 2, 3, 4, 5, ...?",
        answer="r = 2",  # there is no constant ratio for this sequence
        answer_label="r =",
    )
    result = verify(p, "geometric_ratio")
    assert not result.ok


def test_classify_arith_geom_fails_on_misclassification():
    """The generator called a geometric sequence 'arithmetic'."""
    p = Problem(
        label="bug-3",
        body="1, 2, 4, 8, 16, ...",
        answer="Arithmetic (d = 1)",  # actually geometric with r = 2
    )
    result = verify(p, "classify_arith_geom")
    assert not result.ok


def test_evaluate_at_x_fails_on_wrong_substitution():
    """The generator did 2*3 instead of 2^3."""
    p = Problem(
        label="bug-4",
        body="If f(x) = 2^x, what is the value of f(3)?",
        answer="f(3) = 6",  # actually 8
    )
    result = verify(p, "evaluate_at_x")
    assert not result.ok


def test_mc_match_fails_when_letter_and_text_disagree():
    """The generator picked letter B but pasted option A's text after it."""
    p = Problem(
        label="bug-5",
        body="Which exponential function passes through the points (0, 18) and (1, 6)?",
        options=["y = 6(1/3)^x", "y = 18(1/3)^x", "y = 18(3)^x", "y = 6(3)^x"],
        correct_letter="B",
        answer="(B) y = 6(1/3)^x",  # text is option A, not B
    )
    result = verify(p, "mc_match")
    assert not result.ok


# ---------------------------------------------------------------------------
# Format-robustness — correct answers in off-spec formats must still verify.
# These are the false-negative cases that previously flagged good problems
# and blocked the worksheet (the "can't verify the answers" trust-killer).
# ---------------------------------------------------------------------------

def test_combine_like_terms_accepts_factored_answer():
    """A correct but factored answer should verify (expand/simplify equality)."""
    p = Problem(
        label="ok",
        prompt="Find the product.",
        body="(x + 2)(x + 3)",
        answer="x^2 + 5x + 6",
    )
    assert verify(p, "combine_like_terms").ok


def test_combine_like_terms_handles_multidigit_exponent():
    p = Problem(label="ok", body="(x^10 + 2x) + (3x^10 - 2x)", answer="4x^10")
    assert verify(p, "combine_like_terms").ok


def test_classify_accepts_comma_format():
    """'Arithmetic, d = -9' (comma, no parens) must verify."""
    p = Problem(label="ok", body="78, 69, 60, 51, 42, ...", answer="Arithmetic, d = -9")
    assert verify(p, "classify_arith_geom").ok


def test_classify_accepts_bare_word():
    """A bare 'Geometric' with no ratio value still classifies correctly."""
    p = Problem(label="ok", body="2, 6, 18, 54, ...", answer="Geometric")
    assert verify(p, "classify_arith_geom").ok


def test_geometric_ratio_accepts_bare_fraction():
    p = Problem(label="ok", body="81, 27, 9, 3, ...", answer="1/3", answer_label="r =")
    assert verify(p, "geometric_ratio").ok


def test_geometric_term_accepts_sentence_answer():
    p = Problem(label="ok", body="The sequence 2, 6, 18, 54, ... — find the fifth term.",
                answer="The fifth term is 162.")
    assert verify(p, "geometric_term").ok


def test_explicit_rule_accepts_middot_format():
    """'f(n) = 5 · 3^{n-1}' (middot, no parens) must verify."""
    p = Problem(
        label="ok",
        body="Write an explicit rule for a sequence with a first term of 5 and a common ratio of 3.",
        answer="f(n) = 5 · 3^{n-1}",
        answer_label="f(n) =",
    )
    assert verify(p, "explicit_rule").ok


def test_recursive_rule_accepts_asterisk_format():
    p = Problem(
        label="ok",
        body="f(n) = 5(3)^{n-1}",
        answer="f(1) = 5, f(n) = 3 * f(n-1)",
    )
    assert verify(p, "recursive_rule").ok


def test_mc_match_accepts_letter_only_answer():
    p = Problem(
        label="ok",
        body="Which function decreases?",
        options=["y = 6(1/3)^x", "y = 18(1/3)^x", "y = 18(3)^x", "y = 6(3)^x"],
        correct_letter="B",
        answer="(B)",
    )
    assert verify(p, "mc_match").ok


def test_mc_match_accepts_spacing_difference():
    """Option stored compact, answer restated with spaces — must still match."""
    p = Problem(
        label="ok",
        body="Which function?",
        options=["y=6(1/3)^x", "y=18(1/3)^x", "y=18(3)^x", "y=6(3)^x"],
        correct_letter="B",
        answer="(B) y = 18(1/3)^x",
    )
    assert verify(p, "mc_match").ok


# ---------------------------------------------------------------------------
# `checked` flag — separates "didn't evaluate" from "evaluated and wrong".
# Couldn't-parse failures set checked=False (caller defers to Claude);
# genuine math errors set checked=True (caller trusts the flag).
# ---------------------------------------------------------------------------

def test_checked_false_when_cannot_parse_answer():
    """A combine answer with a syntax error → never evaluated, so not 'checked'."""
    p = Problem(label="x", body="(x + 1) + (x + 2)", answer="2x + 3 +")
    result = verify(p, "combine_like_terms")
    assert not result.ok
    assert not result.checked


def test_checked_false_when_sequence_missing():
    p = Problem(label="x", body="Find the common ratio.", answer="r = 2")
    result = verify(p, "geometric_ratio")
    assert not result.ok
    assert not result.checked


def test_checked_true_on_real_math_error():
    """A genuine sign error was evaluated — checked stays True so it's trusted."""
    p = Problem(
        label="x",
        body="(3xy + 2xz - 4yz) + (-xy + 5xz + 2yz)",
        answer="2xy + 7xz + 2yz",  # should be -2yz
    )
    result = verify(p, "combine_like_terms")
    assert not result.ok
    assert result.checked


def test_mc_letter_text_mismatch_is_checked():
    """A letter/text disagreement is a real detected bug, not a parse failure."""
    p = Problem(
        label="x",
        body="Which function?",
        options=["y = 6(1/3)^x", "y = 18(1/3)^x", "y = 18(3)^x", "y = 6(3)^x"],
        correct_letter="B",
        answer="(B) y = 6(1/3)^x",  # text is option A
    )
    result = verify(p, "mc_match")
    assert not result.ok
    assert result.checked


# ---------------------------------------------------------------------------
# Misc sanity
# ---------------------------------------------------------------------------

def test_unknown_kind_returns_failure_not_exception():
    p = Problem(label="x", body="foo", answer="bar")
    result = verify(p, kind="not_a_real_kind")
    assert not result.ok
    assert "unknown verifier kind" in result.reason
    # Unknown kind means we never checked — caller should defer, not flag.
    assert not result.checked


# ---------------------------------------------------------------------------
# correct_substitution_in_answer — the deterministic fix for word-blank math
# ---------------------------------------------------------------------------

def _profit_problem(answer: str) -> Problem:
    return Problem(
        label="3-A",
        body="The revenue ... cost ... If the company sold 5 products, how much profit?",
        answer=answer,
    )


def test_correct_substitution_rewrites_wrong_amount():
    # From production: 20(1000) - 45(100) - 1300 = 14200, not 15200.
    p = _profit_problem("Profit = 20x^3 - 45x^2 - 1300; at x = 10, profit = $15,200")
    fixed, status = correct_substitution_in_answer(p)
    assert status == "corrected"
    assert "$14,200" in fixed.answer


def test_correct_substitution_rewrites_negative_profit():
    # From production: 12(125) - 40(25) - 600 = -100. Earlier this signaled
    # 'regen' but that ate retry budget and shipped flagged problems whenever
    # Claude picked coefficients with revenue < cost at the chosen x.
    # Negative profit is correct math; just format and ship as "-$100".
    p = _profit_problem("Profit = 12x^3 - 40x^2 - 600; at x = 5, profit = $400")
    fixed, status = correct_substitution_in_answer(p)
    assert status == "corrected"
    assert "-$100" in fixed.answer


def test_correct_substitution_keeps_correct_answer():
    # 5(16) + 100 = 180 — already correct.
    p = Problem(
        label="3-A",
        body="...",
        answer="Total Cost = 5x^2 + 100; at x = 4, total cost = $180",
    )
    fixed, status = correct_substitution_in_answer(p)
    assert status == "already_correct"
    assert fixed.answer == p.answer


def test_correct_substitution_noop_for_unrelated_answer():
    # A simple combine-like-terms answer; no substitution to recompute.
    p = Problem(label="1-A", body="3x + 5 + 2x", answer="5x + 5")
    fixed, status = correct_substitution_in_answer(p)
    assert status == "noop"
    assert fixed is p
