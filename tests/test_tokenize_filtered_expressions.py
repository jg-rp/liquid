import operator
from typing import NamedTuple

import pytest

from liquid import Token
from liquid.builtin.expressions import tokenize
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_DPIPE
from liquid.token import TOKEN_ELSE
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_IF
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_LT
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_WORD


class Case(NamedTuple):
    description: str
    source: str
    expect: list[Token]


TEST_CASES: list[Case] = [
    Case(
        "string literal single quotes",
        "'foobar'",
        [Token(TOKEN_STRING, "foobar", start_index=0, source="")],
    ),
    Case(
        "string literal double quotes",
        "'foobar'",
        [Token(TOKEN_STRING, "foobar", start_index=0, source="")],
    ),
    Case(
        "integer literal",
        "7",
        [Token(TOKEN_INTEGER, "7", start_index=0, source="")],
    ),
    Case(
        "negative integer literal",
        "-7",
        [
            Token(TOKEN_INTEGER, "-7", start_index=0, source=""),
        ],
    ),
    Case(
        "float literal",
        "3.14",
        [Token(TOKEN_FLOAT, "3.14", start_index=0, source="")],
    ),
    Case(
        "negative float literal",
        "-3.14",
        [
            Token(TOKEN_FLOAT, "-3.14", start_index=0, source=""),
        ],
    ),
    Case(
        "lone identifier",
        "collection",
        [Token(TOKEN_WORD, "collection", start_index=0, source="")],
    ),
    Case(
        "lone identifier with a hyphen",
        "main-collection",
        [Token(TOKEN_WORD, "main-collection", start_index=0, source="")],
    ),
    Case(
        "chained identifier",
        "collection.products",
        [
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
        ],
    ),
    Case(
        "chained identifier by double quoted key",
        'collection["products"]',
        [
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
        ],
    ),
    Case(
        "chained identifier by single quoted key",
        "collection['products']",
        [
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
        ],
    ),
    Case(
        "chained identifier with array index",
        "collection.products[0]",
        [
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
            Token(TOKEN_IDENTINDEX, "0", start_index=0, source=""),
        ],
    ),
    Case(
        "chained identifier with array index from identifier",
        "collection.products[i]",
        [
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
            Token(TOKEN_LBRACKET, "[", start_index=0, source=""),
            Token(TOKEN_WORD, "i", start_index=0, source=""),
            Token(TOKEN_RBRACKET, "]", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal with filter",
        "'foo' | upcase",
        [
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
        ],
    ),
    Case(
        "identifier with filter",
        "collection.title | upcase",
        [
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "title", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
        ],
    ),
    Case(
        "integer literal with filter and integer argument",
        "4 | at_least: 5",
        [
            Token(TOKEN_INTEGER, "4", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "at_least", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "5", start_index=0, source=""),
        ],
    ),
    Case(
        "float literal with filter and float argument",
        "4.1 | divided_by: 5.2",
        [
            Token(TOKEN_FLOAT, "4.1", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "divided_by", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_FLOAT, "5.2", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal with filter and string argument",
        "'foo' | append: 'bar'",
        [
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "append", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal with filter and identifier argument",
        "'foo' | append: collection.title",
        [
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "append", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "title", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal with filter and multiple arguments",
        '"Liquid" | slice: 2, 5',
        [
            Token(TOKEN_STRING, "Liquid", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "slice", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "2", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_INTEGER, "5", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal with multiple filters",
        '"Liquid" | slice: 2, 5 | upcase',
        [
            Token(TOKEN_STRING, "Liquid", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "slice", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "2", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_INTEGER, "5", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
        ],
    ),
    Case(
        "inconsistent whitespace",
        ' "Liquid"   |slice: 2,5',
        [
            Token(TOKEN_STRING, "Liquid", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "slice", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "2", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_INTEGER, "5", start_index=0, source=""),
        ],
    ),
    Case(
        "range literal",
        "(1..5)",
        [
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=0, source=""),
            Token(TOKEN_INTEGER, "1", start_index=0, source=""),
            Token(TOKEN_RANGE, "..", start_index=0, source=""),
            Token(TOKEN_INTEGER, "5", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
        ],
    ),
    Case(
        "range literal with float literal start",
        "(2.4..5)",
        [
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=0, source=""),
            Token(TOKEN_FLOAT, "2.4", start_index=0, source=""),
            Token(TOKEN_RANGE, "..", start_index=0, source=""),
            Token(TOKEN_INTEGER, "5", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
        ],
    ),
    Case(
        "range literal with identifiers",
        "(a..b)",
        [
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=0, source=""),
            Token(TOKEN_WORD, "a", start_index=0, source=""),
            Token(TOKEN_RANGE, "..", start_index=0, source=""),
            Token(TOKEN_WORD, "b", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
        ],
    ),
    Case(
        description="simple condition",
        source="'foo' if true",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
        ],
    ),
    Case(
        description="comparison operator",
        source="'foo' if x < y",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_WORD, "x", start_index=0, source=""),
            Token(TOKEN_LT, "<", start_index=0, source=""),
            Token(TOKEN_WORD, "y", start_index=0, source=""),
        ],
    ),
    Case(
        description="simple condition with alternative",
        source="'foo' if true else 'bar'",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
        ],
    ),
    Case(
        description="condition with preceding filter",
        source="'foo' | upcase if true else 'bar'",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
        ],
    ),
    Case(
        description="condition with alternative filter",
        source="'foo' if true else 'bar' | upcase",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
        ],
    ),
    Case(
        description="condition with tail filter",
        source="'foo' if true else 'bar' || upcase",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
            Token(TOKEN_DPIPE, "||", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
        ],
    ),
    Case(
        description="multi-line condition with tail filter",
        source="'foo'\nif true\nelse 'bar' || upcase",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
            Token(TOKEN_DPIPE, "||", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
        ],
    ),
    Case(
        description="negated condition",
        source="'foo' if not true",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_NOT, "not", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
        ],
    ),
    Case(
        description="negated condition with alternative",
        source="'foo' if not true else 'bar'",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_NOT, "not", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
        ],
    ),
    Case(
        description="grouped condition with alternative",
        source="'foo' if not (false and false) else 'bar'",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_NOT, "not", start_index=0, source=""),
            Token(TOKEN_LPAREN, "(", start_index=0, source=""),
            Token(TOKEN_FALSE, "false", start_index=0, source=""),
            Token(TOKEN_AND, "and", start_index=0, source=""),
            Token(TOKEN_FALSE, "false", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
        ],
    ),
    Case(
        description="condition with preceding filter",
        source="'foo' | upcase if not true else 'bar'",
        expect=[
            Token(TOKEN_STRING, "foo", start_index=0, source=""),
            Token(TOKEN_PIPE, "|", start_index=0, source=""),
            Token(TOKEN_WORD, "upcase", start_index=0, source=""),
            Token(TOKEN_IF, "if", start_index=0, source=""),
            Token(TOKEN_NOT, "not", start_index=0, source=""),
            Token(TOKEN_TRUE, "true", start_index=0, source=""),
            Token(TOKEN_ELSE, "else", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
        ],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_tokenize_filtered(case: Case) -> None:
    tokens = list(
        tokenize(
            case.source,
            parent_token=Token(TOKEN_EXPRESSION, case.source, 0, case.source),
        )
    )

    assert len(tokens) == len(case.expect)

    for token, expect in zip(tokens, case.expect, strict=True):
        assert token.kind == expect.kind
        assert token.value == expect.value
