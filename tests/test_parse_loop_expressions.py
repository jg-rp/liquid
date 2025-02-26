from __future__ import annotations

import operator
from typing import NamedTuple
from typing import Optional

import pytest

from liquid import Environment
from liquid import Token
from liquid import TokenStream
from liquid.builtin.expressions import LoopExpression
from liquid.builtin.expressions import tokenize
from liquid.exceptions import LiquidSyntaxError
from liquid.token import TOKEN_EXPRESSION


class Case(NamedTuple):
    description: str
    source: str
    expect: Optional[str] = None


TEST_CASES: list[Case] = [
    Case("path", "product in collection.products"),
    Case("limit", "product in collection.products limit:5"),
    Case("limit, path", "product in collection.products limit:max.num"),
    Case("offset", "product in collection.products offset:2"),
    Case("limit and offset", "product in collection.products limit:5 offset:2"),
    Case(
        "offset and limit",
        "product in collection.products offset:2 limit:5",
        "product in collection.products limit:5 offset:2",
    ),
    Case("reversed", "product in collection.products reversed"),
    Case("kitchen sink", "product in collection.products limit:5 offset:2 reversed"),
    Case("range", "product in (1..10)"),
    Case("range, path", "product in (1..collection.products.size)"),
    Case("range with options", "product in (1..10) limit:5 offset:2 reversed"),
    Case(
        "multiple lines",
        "product\n in \ncollections[0]['tags']",
        "product in collections[0].tags",
    ),
    Case(
        "comma separated arguments",
        "i in array, limit: 4, offset: 2",
        "i in array limit:4 offset:2",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_parse_filtered(case: Case) -> None:
    env = Environment()
    tokens = tokenize(case.source, Token(TOKEN_EXPRESSION, case.source, 0, case.source))
    expr = LoopExpression.parse(env, TokenStream(tokens))
    if case.expect is not None:
        assert str(expr) == case.expect
    else:
        assert str(expr) == case.source
