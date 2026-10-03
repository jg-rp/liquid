"""String-to-number coercion in math filters, matching Ruby's `Utils.to_number`.

Values verified against Ruby Liquid 5.13.0. See docs/known_issues.md and #49.
"""

from decimal import Decimal

import pytest

from liquid import render
from liquid.filter import decimal_arg
from liquid.filter import num_arg

# (arg string, Ruby Utils.to_number result)
COERCE_CASES = [
    # loosen: String#to_i ignores trailing junk
    ("7,42", 7),
    ("10 apples", 10),
    ("7.5abc", 7),
    ("-5xyz", -5),
    ("+5", 5),
    ("  42  ", 42),
    ("1_000", 1000),
    # tighten: only a full -?\d+\.\d+ is a float
    ("1e3", 1),
    (".5", 0),
    ("3.", 3),
    ("1.2.3", 1),
    # no leading digits -> 0
    ("foo", 0),
    ("", 0),
    # genuine floats stay floats
    ("3.14", 3.14),
    ("-3.14", -3.14),
]


@pytest.mark.parametrize(
    ("arg", "expect"), COERCE_CASES, ids=[c[0] for c in COERCE_CASES]
)
def test_num_arg_matches_ruby(arg: str, expect: object) -> None:
    result = num_arg(arg, default=0)
    assert result == expect
    assert isinstance(result, type(expect))


def test_known_issue_49_examples() -> None:
    # The maintainer's own hand-computed values from docs/known_issues.md.
    assert render("{{ 3.14 | plus: '7,42' }}") == "10.14"
    assert render("{{ '123abcdef45' | plus: '1,,,,..!@qwerty' }}") == "124"


MATH_TEMPLATES = [
    ("{{ 10 | plus: a }}", "17"),
    ("{{ 10 | minus: a }}", "3"),
    ("{{ 10 | times: a }}", "70"),
    ("{{ 42 | divided_by: a }}", "6"),
    ("{{ 10 | modulo: a }}", "3"),
    ("{{ 3 | at_least: a }}", "7"),
    ("{{ 99 | at_most: a }}", "7"),
]


@pytest.mark.parametrize(
    ("template", "expect"), MATH_TEMPLATES, ids=[t[0] for t in MATH_TEMPLATES]
)
def test_math_family_coerces_arg(template: str, expect: str) -> None:
    # '7,42' -> 7 across the whole num_arg-backed filter family.
    assert render(template, a="7,42") == expect


def test_decimal_arg_coerces_like_ruby() -> None:
    assert decimal_arg("7,42", 0) == 7
    assert decimal_arg("1.5", 0) == Decimal("1.5")
    assert decimal_arg("abc", 0) == 0  # previously raised InvalidOperation
