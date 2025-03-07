import operator
from typing import NamedTuple

import pytest

from liquid import Token
from liquid.builtin.expressions import tokenize
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_WORD


class Case(NamedTuple):
    description: str
    source: str
    expect: list[Token]


TEST_CASES: list[Case] = [
    Case(
        "string literal name no local variable",
        "'product'",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
        ],
    ),
    Case(
        "name from identifier and no local variable",
        "section.name",
        [
            Token(TOKEN_WORD, "section", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "name", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal name with identifier local variable",
        "'product' with products[0]",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
            Token(TOKEN_WITH, "with", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
            Token(TOKEN_IDENTINDEX, "0", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal name with keyword arguments",
        "'product', foo: 'bar', some: other.tags",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_WORD, "foo", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_STRING, "bar", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_WORD, "some", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_WORD, "other", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "tags", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal name with keyword arguments including a range literal",
        "'product', foo: (1..3)",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_WORD, "foo", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_RANGE_LITERAL, "(", start_index=0, source=""),
            Token(TOKEN_INTEGER, "1", start_index=0, source=""),
            Token(TOKEN_RANGE, "..", start_index=0, source=""),
            Token(TOKEN_INTEGER, "3", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal name with identifier aliased local variable",
        "'product' with products[0] as foo",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
            Token(TOKEN_WITH, "with", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
            Token(TOKEN_IDENTINDEX, "0", start_index=0, source=""),
            Token(TOKEN_AS, "as", start_index=0, source=""),
            Token(TOKEN_WORD, "foo", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal name with iterable local variable",
        "'product' for products",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
            Token(TOKEN_FOR, "for", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
        ],
    ),
    Case(
        "string literal name with aliased iterable local variable",
        "'product' for products as foo",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
            Token(TOKEN_FOR, "for", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
            Token(TOKEN_AS, "as", start_index=0, source=""),
            Token(TOKEN_WORD, "foo", start_index=0, source=""),
        ],
    ),
    Case(
        "literal name with identifier aliased local variable and arguments",
        "'product' with products[0] as foo, bar: 42, baz: 'hello'",
        [
            Token(TOKEN_STRING, "product", start_index=0, source=""),
            Token(TOKEN_WITH, "with", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
            Token(TOKEN_IDENTINDEX, "0", start_index=0, source=""),
            Token(TOKEN_AS, "as", start_index=0, source=""),
            Token(TOKEN_WORD, "foo", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_WORD, "bar", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "42", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_WORD, "baz", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_STRING, "hello", start_index=0, source=""),
        ],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_tokenize_include(case: Case) -> None:
    tokens = list(
        tokenize(
            case.source,
            parent_token=Token(TOKEN_EXPRESSION, case.source, 0, case.source),
        )
    )

    assert len(tokens) == len(case.expect)

    for token, expect in zip(tokens, case.expect):
        assert token.kind == expect.kind
        assert token.value == expect.value
