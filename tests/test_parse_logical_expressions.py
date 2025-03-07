from __future__ import annotations

import operator
from typing import NamedTuple
from typing import Optional

import pytest

from liquid import Environment
from liquid import Token
from liquid import TokenStream
from liquid.builtin.expressions import BooleanExpression
from liquid.builtin.expressions import tokenize
from liquid.token import TOKEN_EXPRESSION


class Case(NamedTuple):
    description: str
    source: str
    expect: Optional[str] = None


TEST_CASES: list[Case] = [
    Case("string, double quoted", '"foobar"', "'foobar'"),
    Case("string, single quoted", "'foobar'"),
    Case("integer", "7"),
    Case("integer, negative", "-7"),
    Case("float", "3.14"),
    Case("float, negative", "-3.14"),
    Case("true", "true"),
    Case("false", "false"),
    Case("nil", "nil", ""),
    Case("null", "null", ""),
    Case("path, single segment", "collection"),
    Case("path, two segments", "collection.products"),
    Case("equality", "true == true"),
    Case("inequality", "true != true"),
    Case("inequality, alternative", "true <> true", "true != true"),
    Case("greater than", "user.age > 21"),
    Case("less than", "age < 18"),
    Case("greater than or equal to", "age >= 18"),
    Case("less than or equal to", "age <= 18"),
    Case("logical or", "false or true"),
    Case("logical and", "false and true"),
    Case("membership, contains", "product.tags contains 'sale'"),
    Case("path equals range", "foo.bar == (1..3)"),
    Case("path, index selector", "users[0]"),
    Case("path, name selector, bracket notation", "users[0]['age']", "users[0].age"),
    Case("multiple lines", "users[0]['age'] \n>  \n21", "users[0].age > 21"),
    Case(
        "right associative",
        "true and false and false or true",
        "true and false and (false or true)",
    ),
    Case(
        "right associative",
        "user.name == 'bob' and user.age < 50 or collection.title == 'offers'",
        "user.name == 'bob' and (user.age < 50 or collection.title == 'offers')",
    ),
    Case("not", "not true"),
    Case("grouped", "true and false and (false or true)"),
]


class MockEnv(Environment):
    logical_parentheses = True
    logical_not_operator = True


ENV = MockEnv()


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_parse_logical(case: Case) -> None:
    tokens = tokenize(case.source, Token(TOKEN_EXPRESSION, case.source, 0, case.source))
    expr = BooleanExpression.parse(ENV, TokenStream(tokens))
    if case.expect is not None:
        assert str(expr) == case.expect
    else:
        assert str(expr) == case.source
