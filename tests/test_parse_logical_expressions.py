from __future__ import annotations

import operator
from typing import TYPE_CHECKING
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
    Case(
        description="string, double quoted",
        source='"foobar"',
    )
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_parse_logical(case: Case) -> None:
    env = Environment()
    tokens = tokenize(case.source, Token(TOKEN_EXPRESSION, case.source, 0, case.source))
    expr = BooleanExpression.parse(env, TokenStream(tokens))
    assert str(expr) == case.expect or case.source
