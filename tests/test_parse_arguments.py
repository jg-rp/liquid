from __future__ import annotations

import operator
from typing import NamedTuple
from typing import Optional

import pytest

from liquid import Environment
from liquid import Token
from liquid import TokenStream
from liquid.builtin.expressions import KeywordArgument
from liquid.builtin.expressions import tokenize
from liquid.exceptions import LiquidSyntaxError
from liquid.token import TOKEN_EXPRESSION


class Case(NamedTuple):
    description: str
    source: str
    expect: Optional[str] = None


TEST_CASES: list[Case] = [
    Case("empty", ""),
    Case("string value", "val: 'hello'", "val:'hello'"),
    Case("no whitespace", "val:'hello'"),
    Case("extra whitespace", " val  :\n  'hello'", "val:'hello'"),
    Case("leading comma", ", val: 'hello'", "val:'hello'"),
    Case("trailing comma", ", val: 'hello',", "val:'hello'"),
    Case(
        "multiple arguments",
        "a: 'foo', b: 'bar', c: 'baz'",
        "a:'foo', b:'bar', c:'baz'",
    ),
    Case(
        "multiple arguments, double quotes",
        'a: "foo", b: "bar", c: "baz"',
        "a:'foo', b:'bar', c:'baz'",
    ),
    Case(
        "primitive values",
        "a: 'hello', b: false, c: true, d: nil, e: 1, f: 1.1",
        "a:'hello', b:false, c:true, d:, e:1, f:1.1",
    ),
    Case(
        "paths",
        "a: products[0], b: products['foo'].title",
        "a:products[0], b:products.foo.title",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_parse_arguments(case: Case) -> None:
    env = Environment()
    tokens = tokenize(case.source, Token(TOKEN_EXPRESSION, case.source, 0, case.source))
    args = KeywordArgument.parse(env, TokenStream(tokens))
    expr = ", ".join(str(arg) for arg in args)
    if case.expect is not None:
        assert str(expr) == case.expect
    else:
        assert str(expr) == case.source


def test_double_colon() -> None:
    source = "a: 'foo', b:: 'bar', c: 'baz'"
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        KeywordArgument.parse(env, TokenStream(tokens))


def test_missing_colon() -> None:
    source = "a 'foo', b: 'bar', c: 'baz'"
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        KeywordArgument.parse(env, TokenStream(tokens))


def test_double_comma() -> None:
    source = "a: 'foo',, b: 'bar', c: 'baz'"
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        KeywordArgument.parse(env, TokenStream(tokens))


def test_missing_comma() -> None:
    source = "a: 'foo' b: 'bar', c: 'baz'"
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        KeywordArgument.parse(env, TokenStream(tokens))
