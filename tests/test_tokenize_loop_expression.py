import operator
from typing import NamedTuple

import pytest

from liquid import Token
from liquid.builtin.expressions import tokenize
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_WORD


class Case(NamedTuple):
    description: str
    source: str
    expect: list[Token]


TEST_CASES: list[Case] = [
    Case(
        "loop over identifier",
        "product in collection.products",
        [
            Token(TOKEN_WORD, "product", start_index=0, source=""),
            Token(TOKEN_IN, "in", start_index=0, source=""),
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
        ],
    ),
    Case(
        "loop over identifier with limit and offset",
        "product in collection.products limit:4 offset:2",
        [
            Token(TOKEN_WORD, "product", start_index=0, source=""),
            Token(TOKEN_IN, "in", start_index=0, source=""),
            Token(TOKEN_WORD, "collection", start_index=0, source=""),
            Token(TOKEN_DOT, ".", start_index=0, source=""),
            Token(TOKEN_WORD, "products", start_index=0, source=""),
            Token(TOKEN_LIMIT, "limit", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "4", start_index=0, source=""),
            Token(TOKEN_OFFSET, "offset", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "2", start_index=0, source=""),
        ],
    ),
    Case(
        "loop over reversed range",
        "num in (1..10) reversed",
        [
            Token(TOKEN_WORD, "num", start_index=0, source=""),
            Token(TOKEN_IN, "in", start_index=0, source=""),
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=0, source=""),
            Token(TOKEN_INTEGER, "1", start_index=0, source=""),
            Token(TOKEN_RANGE, "..", start_index=0, source=""),
            Token(TOKEN_INTEGER, "10", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
            Token(TOKEN_REVERSED, "reversed", start_index=0, source=""),
        ],
    ),
    Case(
        "loop over range with identifier",
        "i in (1..num)",
        [
            Token(TOKEN_WORD, "i", start_index=0, source=""),
            Token(TOKEN_IN, "in", start_index=0, source=""),
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=0, source=""),
            Token(TOKEN_INTEGER, "1", start_index=0, source=""),
            Token(TOKEN_RANGE, "..", start_index=0, source=""),
            Token(TOKEN_WORD, "num", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
        ],
    ),
    Case(
        "loop over range with float start",
        "i in (2.4..5)",
        [
            Token(TOKEN_WORD, "i", start_index=0, source=""),
            Token(TOKEN_IN, "in", start_index=0, source=""),
            Token(TOKEN_RANGE_LITERAL, "rangeliteral", start_index=0, source=""),
            Token(TOKEN_FLOAT, "2.4", start_index=0, source=""),
            Token(TOKEN_RANGE, "..", start_index=0, source=""),
            Token(TOKEN_INTEGER, "5", start_index=0, source=""),
            Token(TOKEN_RPAREN, ")", start_index=0, source=""),
        ],
    ),
    Case(
        description="loop over named iterable with continue offset",
        source="item in array limit: 3 offset: continue",
        expect=[
            Token(TOKEN_WORD, "item", start_index=0, source=""),
            Token(TOKEN_IN, "in", start_index=0, source=""),
            Token(TOKEN_WORD, "array", start_index=0, source=""),
            Token(TOKEN_LIMIT, "limit", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "3", start_index=0, source=""),
            Token(TOKEN_OFFSET, "offset", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_CONTINUE, "continue", start_index=0, source=""),
        ],
    ),
    Case(
        description="comma separated arguments",
        source="i in array, limit: 4, offset: 2",
        expect=[
            Token(TOKEN_WORD, "i", start_index=0, source=""),
            Token(TOKEN_IN, "in", start_index=0, source=""),
            Token(TOKEN_WORD, "array", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_LIMIT, "limit", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "4", start_index=0, source=""),
            Token(TOKEN_COMMA, ",", start_index=0, source=""),
            Token(TOKEN_OFFSET, "offset", start_index=0, source=""),
            Token(TOKEN_COLON, ":", start_index=0, source=""),
            Token(TOKEN_INTEGER, "2", start_index=0, source=""),
        ],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_tokenize_loop(case: Case) -> None:
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
