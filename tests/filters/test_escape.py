import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import escape
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import LiquidError


@dataclass
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


ENV = Environment()

TEST_CASES = [
    Case(
        description="make HTML-safe",
        val="<p>test</p>",
        args=[],
        kwargs={},
        expect="&lt;p&gt;test&lt;/p&gt;",
    ),
    Case(
        description="not a string",
        val=5,
        args=[],
        kwargs={},
        expect="5",
    ),
    Case(
        description="unexpected argument",
        val="HELLO",
        args=[5],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect="",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_escape_filter(case: Case) -> None:
    escape_ = partial(escape, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            escape_(case.val, *case.args, **case.kwargs)
    else:
        assert escape_(case.val, *case.args, **case.kwargs) == case.expect
