"""Round Two — answer verification.

Routes a generated Problem to the appropriate SymPy-based check based on a
`verifier_kind` string (assigned to each ProblemType during type extraction).
The full set covers the eight non-graph patterns observed across the two
reference modules. The Claude second-pass verifier for word problems lives in
`problem_generator.py` since it requires an API call.

Usage:
    from verifier import verify
    result = verify(problem, kind="combine_like_terms")
    if not result.ok:
        # regenerate or flag for human review
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from sympy import Rational, simplify
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from worksheet_renderer import Problem


@dataclass
class VerificationResult:
    ok: bool
    reason: str
    details: dict = field(default_factory=dict)


# --- Public entry point -----------------------------------------------------

def verify(problem: Problem, kind: str) -> VerificationResult:
    """Route to a specific verifier function by `kind`. Returns a result that
    callers can use to retry, accept, or flag a problem."""
    fn = _VERIFIERS.get(kind)
    if fn is None:
        return VerificationResult(ok=False, reason=f"unknown verifier kind: {kind}")
    try:
        return fn(problem)
    except Exception as e:
        return VerificationResult(
            ok=False,
            reason=f"verifier raised {type(e).__name__}: {e}",
        )


# --- Markup → SymPy translation --------------------------------------------

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _normalize(s: str) -> str:
    """Translate worksheet markup into a SymPy-parseable string.

    - `^N` / `^{...}` → `**N` / `**(...)`
    - Unicode minus signs (− ‒ –) → ASCII `-`
    - Curly quote artifacts removed
    """
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
    s = re.sub(r"\^\{([^}]+)\}", r"**(\1)", s)
    s = re.sub(r"\^([A-Za-z0-9])", r"**\1", s)
    return s


def _parse(s: str):
    """Parse a worksheet expression into a SymPy expression with implicit `*`
    so multi-letter variables like `xy` are interpreted as `x*y`."""
    return parse_expr(_normalize(s), transformations=_TRANSFORMATIONS)


def _equal(a, b) -> bool:
    """Symbolic equality that survives factoring/rearrangement."""
    return simplify(a - b) == 0


def _parse_rational(s: str) -> Rational:
    """Parse a number string that may include `/` or a decimal."""
    s = s.strip().replace(",", "")
    if "/" in s:
        num, den = s.split("/", 1)
        return Rational(int(num.strip()), int(den.strip()))
    return Rational(s)


# --- Individual verifiers --------------------------------------------------

def _verify_combine_like_terms(problem: Problem) -> VerificationResult:
    """The body, simplified, equals the answer (after simplification).
    Covers polynomial addition, subtraction, perimeter sums, and the
    'simplified expression' part of word problems."""
    body_expr = _parse(problem.body)
    ans_text = problem.answer

    # If the answer carries a leading prefix like "P = " or "Profit = ", strip it
    # so we compare the math expressions on both sides of the equals sign.
    m = re.match(r"^\s*[A-Za-z][A-Za-z0-9_]*\s*=\s*(.*)$", ans_text)
    rhs = m.group(1) if m else ans_text
    # If the answer is "Profit = ...; at x=5: $525", drop the trailing evaluation hint.
    rhs = rhs.split(";")[0].strip()

    ans_expr = _parse(rhs)
    if _equal(body_expr, ans_expr):
        return VerificationResult(ok=True, reason="body simplifies to answer")
    return VerificationResult(
        ok=False,
        reason="body does not simplify to answer",
        details={"body_simplified": str(simplify(body_expr)),
                 "answer_simplified": str(simplify(ans_expr))},
    )


def _verify_evaluate_at_x(problem: Problem) -> VerificationResult:
    """Pattern: body of the form 'If f(x) = <expr>, what is f(N)?'; answer
    of the form 'f(N) = <value>' (or just '<value>'). Verify by substituting."""
    fdef = re.search(r"f\(\s*x\s*\)\s*=\s*(.+?)(?:,|\?|\.)", problem.body)
    if not fdef:
        return VerificationResult(ok=False, reason="couldn't find 'f(x) = ...' in body")
    sub = re.search(r"f\(\s*(\d+(?:\.\d+)?)\s*\)", problem.body[fdef.end():])
    if not sub:
        return VerificationResult(ok=False, reason="couldn't find 'f(N)' substitution in body")

    expr_str = fdef.group(1).strip()
    n_str = sub.group(1)
    expr = _parse(expr_str)
    from sympy.abc import x  # noqa: F401  imported for substitution use
    from sympy import Symbol
    computed = expr.subs(Symbol("x"), Rational(n_str.replace(",", "")))
    computed_simplified = simplify(computed)

    # Extract claimed value from answer. Accepts "f(4) = 16" or just "16".
    m = re.search(r"f\(\s*\d+\s*\)\s*=\s*([^\s]+)", problem.answer)
    claimed_str = m.group(1) if m else problem.answer.strip()
    try:
        claimed = _parse_rational(claimed_str)
    except (ValueError, ZeroDivisionError):
        try:
            claimed = simplify(_parse(claimed_str))
        except Exception:
            return VerificationResult(ok=False, reason=f"couldn't parse claimed value '{claimed_str}'")
    if simplify(computed_simplified - claimed) == 0:
        return VerificationResult(ok=True, reason=f"f({n_str}) = {computed_simplified}")
    return VerificationResult(
        ok=False,
        reason=f"value mismatch: computed {computed_simplified}, claimed {claimed}",
        details={"f": expr_str, "n": n_str},
    )


def _verify_geometric_ratio(problem: Problem) -> VerificationResult:
    """Verify the claimed common ratio of a sequence in the body."""
    nums = _extract_sequence(problem.body)
    if nums is None or len(nums) < 2:
        return VerificationResult(ok=False, reason="couldn't extract sequence from body")
    r = nums[1] / nums[0]
    for i in range(2, len(nums)):
        if nums[i] / nums[i - 1] != r:
            return VerificationResult(ok=False, reason="sequence is not geometric")

    m = re.search(r"r\s*=\s*([\-]?[0-9./]+)", problem.answer)
    if not m:
        return VerificationResult(ok=False, reason="couldn't find 'r = ...' in answer")
    try:
        claimed = _parse_rational(m.group(1))
    except (ValueError, ZeroDivisionError):
        return VerificationResult(ok=False, reason=f"couldn't parse claimed r '{m.group(1)}'")
    if claimed == r:
        return VerificationResult(ok=True, reason=f"r = {r}")
    return VerificationResult(ok=False, reason=f"r mismatch: computed {r}, claimed {claimed}")


def _verify_geometric_term(problem: Problem) -> VerificationResult:
    """Verify the nth term of a geometric sequence, given either a formula
    `f(n) = a(r)^{n-1}` or a sequence-style body. Answer is a number or '<value>'."""
    n_target = _find_nth_request(problem.body)
    if n_target is None:
        return VerificationResult(ok=False, reason="couldn't find which nth-term is asked")

    a, r = _extract_a_r(problem.body)
    if a is None or r is None:
        return VerificationResult(ok=False, reason="couldn't extract a and r from body")

    computed = a * r ** (n_target - 1)
    computed = simplify(computed)

    claimed_str = problem.answer.strip()
    try:
        claimed = _parse_rational(claimed_str)
    except (ValueError, ZeroDivisionError):
        try:
            claimed = simplify(_parse(claimed_str))
        except Exception:
            return VerificationResult(ok=False, reason=f"couldn't parse '{claimed_str}'")
    if simplify(computed - claimed) == 0:
        return VerificationResult(ok=True, reason=f"term = {computed}")
    return VerificationResult(ok=False, reason=f"term mismatch: computed {computed}, claimed {claimed}")


def _verify_classify_arith_geom(problem: Problem) -> VerificationResult:
    """Body is a sequence; answer says 'Arithmetic (d = X)' or 'Geometric (r = Y)'."""
    nums = _extract_sequence(problem.body)
    if nums is None or len(nums) < 3:
        return VerificationResult(ok=False, reason="couldn't extract a 3+ term sequence")

    diffs = [nums[i + 1] - nums[i] for i in range(len(nums) - 1)]
    is_arith = all(d == diffs[0] for d in diffs)
    ratios = []
    is_geo = True
    for i in range(len(nums) - 1):
        if nums[i] == 0:
            is_geo = False
            break
        ratios.append(nums[i + 1] / nums[i])
    if is_geo:
        is_geo = all(r == ratios[0] for r in ratios)

    ans = problem.answer
    arith_claim = re.search(r"Arithmetic\s*\(\s*d\s*=\s*([+\-]?[0-9./]+)", ans)
    geo_claim = re.search(r"Geometric\s*\(\s*r\s*=\s*([+\-]?[0-9./]+)", ans)

    if arith_claim and is_arith:
        claimed = _parse_rational(arith_claim.group(1))
        if claimed == diffs[0]:
            return VerificationResult(ok=True, reason=f"arithmetic, d = {diffs[0]}")
        return VerificationResult(ok=False, reason=f"d mismatch: computed {diffs[0]}, claimed {claimed}")
    if geo_claim and is_geo:
        claimed = _parse_rational(geo_claim.group(1))
        if claimed == ratios[0]:
            return VerificationResult(ok=True, reason=f"geometric, r = {ratios[0]}")
        return VerificationResult(ok=False, reason=f"r mismatch: computed {ratios[0]}, claimed {claimed}")
    if arith_claim and is_geo:
        return VerificationResult(ok=False, reason="claimed arithmetic but sequence is geometric")
    if geo_claim and is_arith:
        return VerificationResult(ok=False, reason="claimed geometric but sequence is arithmetic")
    return VerificationResult(ok=False, reason="couldn't classify or parse claim")


def _verify_explicit_rule(problem: Problem) -> VerificationResult:
    """Answer of the form 'f(n) = a(r)^{n-1}'. Verify a and r match what the
    body asks for ('first term of A and a common ratio of R')."""
    body = problem.body
    a_match = re.search(r"first term of\s+([+\-]?[0-9./]+)", body, re.IGNORECASE)
    r_match = re.search(r"common ratio of\s+([+\-]?[0-9./]+)", body, re.IGNORECASE)
    if not (a_match and r_match):
        return VerificationResult(ok=False, reason="couldn't find first term / common ratio in body")
    a = _parse_rational(a_match.group(1))
    r = _parse_rational(r_match.group(1))

    ans = re.sub(r"\s", "", problem.answer)
    # f(n)=a(r)^{n-1} → check the captured a and r
    m = re.match(r"f\(n\)=([+\-]?[0-9./]+)\(([+\-]?[0-9./]+)\)\^?\{?n-1\}?", ans)
    if not m:
        return VerificationResult(ok=False, reason=f"answer doesn't match f(n)=a(r)^{{n-1}}: '{problem.answer}'")
    claimed_a = _parse_rational(m.group(1))
    claimed_r = _parse_rational(m.group(2))
    if claimed_a == a and claimed_r == r:
        return VerificationResult(ok=True, reason=f"a={a}, r={r}")
    return VerificationResult(ok=False, reason=f"a/r mismatch: body wants a={a}, r={r}; answer says a={claimed_a}, r={claimed_r}")


def _verify_recursive_rule(problem: Problem) -> VerificationResult:
    """For Type 3 / Type 5 module 13/14. The answer carries the canonical form
    '(B) f(1) = a, f(n) = r · f(n-1)' or similar. Verify a and r against either:
      - explicit formula in body: f(n) = a(r)^{n-1}
      - sequence in body
    """
    a_target, r_target = _extract_a_r(problem.body)
    if a_target is None or r_target is None:
        return VerificationResult(ok=False, reason="couldn't extract a and r from body")

    ans = problem.answer
    a_m = re.search(r"f\(1\)\s*=\s*([+\-]?[0-9./]+)", ans)
    r_m = re.search(r"f\(n\)\s*=\s*([+\-]?[0-9./]+)\s*[·*]\s*f\(n-1\)", ans)
    if not (a_m and r_m):
        return VerificationResult(ok=False, reason=f"answer doesn't match recursive form: '{ans}'")
    a_claim = _parse_rational(a_m.group(1))
    r_claim = _parse_rational(r_m.group(1))
    if a_claim == a_target and r_claim == r_target:
        return VerificationResult(ok=True, reason=f"a={a_target}, r={r_target}")
    return VerificationResult(
        ok=False,
        reason=f"a/r mismatch: target a={a_target}, r={r_target}; answer a={a_claim}, r={r_claim}",
    )


def _verify_mc_match(problem: Problem) -> VerificationResult:
    """Generic MC verifier: the canonical answer string '(B) <text>' must list a
    valid option letter, and the listed text must equal options[letter_index]
    after whitespace-and-markup normalization."""
    if not problem.options or len(problem.options) < 4:
        return VerificationResult(ok=False, reason="MC problem missing 4 options")
    if not problem.correct_letter or problem.correct_letter not in "ABCD":
        return VerificationResult(ok=False, reason=f"invalid correct_letter '{problem.correct_letter}'")
    idx = "ABCD".index(problem.correct_letter)
    expected_option = problem.options[idx]
    m = re.match(r"^\(([A-D])\)\s*(.+)$", problem.answer.strip())
    if not m:
        return VerificationResult(ok=False, reason=f"answer doesn't start with '(X) ': '{problem.answer}'")
    if m.group(1) != problem.correct_letter:
        return VerificationResult(ok=False, reason=f"answer letter '{m.group(1)}' != correct_letter '{problem.correct_letter}'")
    answer_text = m.group(2).strip()
    if _normalize_for_compare(answer_text) == _normalize_for_compare(expected_option):
        return VerificationResult(ok=True, reason=f"MC ({problem.correct_letter}) verified")
    return VerificationResult(
        ok=False,
        reason="answer text doesn't match the chosen option's text",
        details={"option": expected_option, "answer_text": answer_text},
    )


def _normalize_for_compare(s: str) -> str:
    """Squash whitespace and remove non-essential characters for option comparison."""
    return re.sub(r"\s+", " ", s).strip()


# --- Sequence / formula extraction helpers --------------------------------

def _extract_sequence(text: str) -> list[Rational] | None:
    """Find the first comma-separated number sequence in `text`. Tolerates the
    'sequence X, Y, Z, ...' framing or a bare 'X, Y, Z, ...' string."""
    for pattern in (
        r"sequence\s+([0-9.\-,/\s]+?)\s*\.\.\.",
        r"f\(n\):\s*([0-9.\-,/\s]+?)$",
        r"^\s*([0-9.\-,/\s]+?)\s*\.\.\.",
    ):
        m = re.search(pattern, text, re.MULTILINE)
        if m:
            return _split_to_rationals(m.group(1))
    return None


def _split_to_rationals(s: str) -> list[Rational] | None:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    try:
        return [_parse_rational(p) for p in parts]
    except (ValueError, ZeroDivisionError):
        return None


def _find_nth_request(text: str) -> int | None:
    """Map 'fourth' / 'fifth' / 'nth' words, or 'f(N)' patterns, to an integer."""
    word_to_n = {
        "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
    }
    for word, n in word_to_n.items():
        if re.search(rf"\b{word}\s+term", text, re.IGNORECASE):
            return n
    m = re.search(r"f\(\s*(\d+)\s*\)", text)
    if m:
        return int(m.group(1))
    return None


def _extract_a_r(text: str) -> tuple[Rational | None, Rational | None]:
    """Pull `a` and `r` from either an explicit formula `f(n) = a(r)^{n-1}` or a
    leading sequence."""
    m = re.search(r"f\(n\)\s*=\s*([+\-]?[0-9./]+)\(([+\-]?[0-9./]+)\)\^\{?n-1\}?", text)
    if m:
        return _parse_rational(m.group(1)), _parse_rational(m.group(2))
    nums = _extract_sequence(text)
    if nums and len(nums) >= 2 and nums[0] != 0:
        a = nums[0]
        r = nums[1] / nums[0]
        return a, r
    return None, None


# --- Dispatch table --------------------------------------------------------

_VERIFIERS: dict[str, Callable[[Problem], VerificationResult]] = {
    "combine_like_terms": _verify_combine_like_terms,
    "evaluate_at_x": _verify_evaluate_at_x,
    "geometric_ratio": _verify_geometric_ratio,
    "geometric_term": _verify_geometric_term,
    "classify_arith_geom": _verify_classify_arith_geom,
    "explicit_rule": _verify_explicit_rule,
    "recursive_rule": _verify_recursive_rule,
    "mc_match": _verify_mc_match,
}
