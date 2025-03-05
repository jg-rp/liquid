from __future__ import annotations

import operator
from typing import NamedTuple
from typing import Optional

import pytest

from liquid import Environment
from liquid import Mode
from liquid import Token
from liquid import TokenStream
from liquid.builtin.expressions import FilteredExpression
from liquid.builtin.expressions import tokenize
from liquid.exceptions import LiquidSyntaxError
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
    Case(
        "path, two segments, bracket notation",
        "collection['products']",
        "collection.products",
    ),
    Case(
        "path, bracket notation followed by dot",
        "collection['products'].first",
        "collection.products.first",
    ),
    Case(
        "path, double quoted bracket notation",
        'collection["products"]',
        "collection.products",
    ),
    Case("path, index selector", "a[0]"),
    Case("path, index selector, negative", "a[-2]"),
    Case("path, variable selector", "a.b[x]"),
    Case("path, multi-segment variable selector", "a.b[x.y['z']]", "a.b[x.y.z]"),
    Case("range, int literals", "(1..4)"),
    Case("range, paths", "(a..b.c)"),
    Case("filter, string literal", "'foo' | upcase"),
    Case("filter, string literal argument", "'foo' | append: 'bar'"),
    Case("filter, path", "collection.title | upcase"),
    Case("filter, integer", "4 | at_least: 5"),
    Case("filter, float", "4.1 | divided_by: 5.2"),
    Case("filter, path argument", "'foo' | append: collection.title"),
    Case(
        "filter, multiple arguments", '"Liquid" | slice: 2, 5', "'Liquid' | slice: 2, 5"
    ),
    Case(
        "filter, extra whitespace",
        '"Liquid"    | slice: 2,     5',
        "'Liquid' | slice: 2, 5",
    ),
    Case("filter, named argument", "thing | default: 'hello', allow_false:true"),
    Case("inline condition", "'foo' if true"),
    Case("inline condition with alternative", "'foo' if true else 'bar'"),
    Case(
        "inline condition, filtered, with alternative",
        "'foo' | upcase if true else 'bar'",
    ),
    Case(
        "inline condition, with filtered alternative",
        "'foo' if true else 'bar' | upcase",
    ),
    Case(
        "inline condition, with tail filters",
        "'foo' if true else 'bar' || append: 'bar' | upcase",
    ),
    Case("inline condition, negation", "'foo' if not true"),
    Case(
        "inline condition, logical operators",
        "'foo' if true and false and false else 'bar'",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_parse_filtered(case: Case) -> None:
    env = Environment()
    tokens = tokenize(case.source, Token(TOKEN_EXPRESSION, case.source, 0, case.source))
    expr = FilteredExpression.parse(env, TokenStream(tokens))
    if case.expect is not None:
        assert str(expr) == case.expect
    else:
        assert str(expr) == case.source


def test_double_pipe() -> None:
    source = "'hello' || upcase"
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        FilteredExpression.parse(env, TokenStream(tokens))


def test_double_colon() -> None:
    source = '"hello" | slice:: 2'
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        FilteredExpression.parse(env, TokenStream(tokens))


def test_missing_colon() -> None:
    source = '"hello" | slice 2, 6'
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        FilteredExpression.parse(env, TokenStream(tokens))


def test_double_comma() -> None:
    source = '"hello" | slice: 2,, 4'
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        FilteredExpression.parse(env, TokenStream(tokens))


def test_missing_comma() -> None:
    source = '"hello" | slice: 2 4'
    env = Environment(tolerance=Mode.STRICT)
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        FilteredExpression.parse(env, TokenStream(tokens))


def test_invalid_filter_name() -> None:
    source = '"hello" | £%1 '
    env = Environment()
    tokens = tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source))

    with pytest.raises(LiquidSyntaxError):
        FilteredExpression.parse(env, TokenStream(tokens))
