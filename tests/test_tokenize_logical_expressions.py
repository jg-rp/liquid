import operator
from typing import NamedTuple

import pytest

from liquid import Token
from liquid.builtin.expressions import tokenize
from liquid.exceptions import LiquidSyntaxError
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_EQ
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_GE
from liquid.token import TOKEN_GT
from liquid.token import TOKEN_WORD
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LE
from liquid.token import TOKEN_LG
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_NE
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE


class Case(NamedTuple):
    description: str
    source: str
    expect: list[Token]


TEST_CASES: list[Case] = [
    Case(
        "literal boolean",
        "false == true",
        [
            Token(TOKEN_FALSE, "false", start_index=0, source=""),
            Token(TOKEN_EQ, "==", start_index=6, source=""),
            Token(TOKEN_TRUE, "true", start_index=9, source=""),
        ],
    ),
    Case(
        "not nil identifier",
        "user != nil",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_NE, "!=", start_index=5, source=""),
            Token(TOKEN_NIL, "nil", start_index=8, source=""),
        ],
    ),
    Case(
        "not null identifier",
        "user != null",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_NE, "!=", start_index=5, source=""),
            Token(TOKEN_NULL, "null", start_index=8, source=""),
        ],
    ),
    Case(
        "alternate not nil",
        "user <> nil",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_LG, "<>", start_index=5, source=""),
            Token(TOKEN_NIL, "nil", start_index=8, source=""),
        ],
    ),
    Case(
        "identifier equals string literal",
        "user.name == 'brian'",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=4, source=""),
            Token(TOKEN_WORD, "name", start_index=5, source=""),
            Token(TOKEN_EQ, "==", start_index=10, source=""),
            Token(TOKEN_STRING, "brian", start_index=13, source=""),
        ],
    ),
    Case(
        "equality with or",
        "user.name == 'bill' or user.name == 'bob'",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=4, source=""),
            Token(TOKEN_WORD, "name", start_index=5, source=""),
            Token(TOKEN_EQ, "==", start_index=10, source=""),
            Token(TOKEN_STRING, "bill", start_index=13, source=""),
            Token(TOKEN_OR, "or", start_index=20, source=""),
            Token(TOKEN_WORD, "user", start_index=23, source=""),
            Token(TOKEN_DOT, ".", start_index=27, source=""),
            Token(TOKEN_WORD, "name", start_index=28, source=""),
            Token(TOKEN_EQ, "==", start_index=33, source=""),
            Token(TOKEN_STRING, "bob", start_index=36, source=""),
        ],
    ),
    Case(
        "equality with and",
        "user.name == 'bob' and user.age > 45",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=4, source=""),
            Token(TOKEN_WORD, "name", start_index=5, source=""),
            Token(TOKEN_EQ, "==", start_index=10, source=""),
            Token(TOKEN_STRING, "bob", start_index=13, source=""),
            Token(TOKEN_AND, "and", start_index=19, source=""),
            Token(TOKEN_WORD, "user", start_index=23, source=""),
            Token(TOKEN_DOT, ".", start_index=27, source=""),
            Token(TOKEN_WORD, "age", start_index=28, source=""),
            Token(TOKEN_GT, ">", start_index=32, source=""),
            Token(TOKEN_INTEGER, "45", start_index=34, source=""),
        ],
    ),
    Case(
        "greater than or equal to integer literal",
        "user.age >= 21",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=4, source=""),
            Token(TOKEN_WORD, "age", start_index=5, source=""),
            Token(TOKEN_GE, ">=", start_index=9, source=""),
            Token(TOKEN_INTEGER, "21", start_index=12, source=""),
        ],
    ),
    Case(
        "less than or equal to integer literal",
        "user.age <= 21",
        [
            Token(TOKEN_WORD, "user", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=4, source=""),
            Token(TOKEN_WORD, "age", start_index=5, source=""),
            Token(TOKEN_LE, "<=", start_index=9, source=""),
            Token(TOKEN_INTEGER, "21", start_index=12, source=""),
        ],
    ),
    Case(
        "identifier contains string",
        "product.tags contains 'sale'",
        [
            Token(TOKEN_WORD, "product", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=7, source=""),
            Token(TOKEN_WORD, "tags", start_index=8, source=""),
            Token(TOKEN_CONTAINS, "contains", start_index=13, source=""),
            Token(TOKEN_STRING, "sale", start_index=22, source=""),
        ],
    ),
    Case(
        "identifier equals blank",
        "product.title == blank",
        [
            Token(TOKEN_WORD, "product", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=7, source=""),
            Token(TOKEN_WORD, "title", start_index=8, source=""),
            Token(TOKEN_EQ, "==", start_index=14, source=""),
            Token(TOKEN_BLANK, "blank", start_index=17, source=""),
        ],
    ),
    Case(
        "identifier equals empty",
        "product.title == empty",
        [
            Token(TOKEN_WORD, "product", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=7, source=""),
            Token(TOKEN_WORD, "title", start_index=8, source=""),
            Token(TOKEN_EQ, "==", start_index=14, source=""),
            Token(TOKEN_EMPTY, "empty", start_index=17, source=""),
        ],
    ),
    Case(
        "literal boolean not true",
        "false == not true",
        [
            Token(TOKEN_FALSE, "false", start_index=0, source=""),
            Token(TOKEN_EQ, "==", start_index=6, source=""),
            Token(TOKEN_NOT, "not", start_index=9, source=""),
            Token(TOKEN_TRUE, "true", start_index=13, source=""),
        ],
    ),
    Case(
        "literal boolean not false",
        "false == not false",
        [
            Token(TOKEN_FALSE, "false", start_index=0, source=""),
            Token(TOKEN_EQ, "==", start_index=6, source=""),
            Token(TOKEN_NOT, "not", start_index=9, source=""),
            Token(TOKEN_FALSE, "false", start_index=13, source=""),
        ],
    ),
    Case(
        "parens",
        "(false and false)",
        [
            Token(TOKEN_LPAREN, "(", start_index=0, source=""),
            Token(TOKEN_FALSE, "false", start_index=1, source=""),
            Token(TOKEN_AND, "and", start_index=7, source=""),
            Token(TOKEN_FALSE, "false", start_index=11, source=""),
            Token(TOKEN_RPAREN, ")", start_index=16, source=""),
        ],
    ),
    Case(
        "range literals",
        "(1..3) == (1..3)",
        [
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=0, source=""),
            Token(TOKEN_LPAREN, "(", start_index=0, source=""),
            Token(TOKEN_INTEGER, "1", start_index=1, source=""),
            Token(TOKEN_RANGE, "..", start_index=2, source=""),
            Token(TOKEN_INTEGER, "3", start_index=4, source=""),
            Token(TOKEN_RPAREN, ")", start_index=5, source=""),
            Token(TOKEN_EQ, "==", start_index=7, source=""),
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=10, source=""),
            Token(TOKEN_LPAREN, "(", start_index=10, source=""),
            Token(TOKEN_INTEGER, "1", start_index=11, source=""),
            Token(TOKEN_RANGE, "..", start_index=12, source=""),
            Token(TOKEN_INTEGER, "3", start_index=14, source=""),
            Token(TOKEN_RPAREN, ")", start_index=15, source=""),
        ],
    ),
    Case(
        "nested grouped boolean with logic operators",
        "((true or false) or (false)) and true",
        [
            Token(TOKEN_LPAREN, "(", start_index=0, source=""),
            Token(TOKEN_LPAREN, "(", start_index=1, source=""),
            Token(TOKEN_TRUE, "true", start_index=2, source=""),
            Token(TOKEN_OR, "or", start_index=7, source=""),
            Token(TOKEN_FALSE, "false", start_index=10, source=""),
            Token(TOKEN_RPAREN, ")", start_index=15, source=""),
            Token(TOKEN_OR, "or", start_index=17, source=""),
            Token(TOKEN_LPAREN, "(", start_index=20, source=""),
            Token(TOKEN_FALSE, "false", start_index=21, source=""),
            Token(TOKEN_RPAREN, ")", start_index=26, source=""),
            Token(TOKEN_RPAREN, ")", start_index=27, source=""),
            Token(TOKEN_AND, "and", start_index=29, source=""),
            Token(TOKEN_TRUE, "true", start_index=33, source=""),
        ],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_tokenize_logical(case: Case) -> None:
    expect = [
        Token(t.kind, t.value, t.start_index, source=case.source) for t in case.expect
    ]
    assert (
        list(
            tokenize(
                case.source,
                parent_token=Token(TOKEN_EXPRESSION, case.source, 0, case.source),
            )
        )
        == expect
    )


def test_illegal_character() -> None:
    source = "} == %"
    with pytest.raises(LiquidSyntaxError):
        list(tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source)))


def test_unknown_operator() -> None:
    source = "x >< y"
    with pytest.raises(LiquidSyntaxError):
        list(tokenize(source, Token(TOKEN_EXPRESSION, source, 0, source)))
