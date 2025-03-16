import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import strip_newlines
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
        description="newline and other whitespace",
        val="hello there\nyou",
        args=[],
        kwargs={},
        expect="hello thereyou",
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
        val="hello",
        args=[5],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="reference implementation test 1",
        val="a\nb\nc",
        args=[],
        kwargs={},
        expect="abc",
    ),
    Case(
        description="reference implementation test 2",
        val="a\r\nb\nc",
        args=[],
        kwargs={},
        expect="abc",
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
def test_strip_newlines_filter(case: Case) -> None:
    strip_newlines_ = partial(strip_newlines, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            strip_newlines_(case.val, *case.args, **case.kwargs)
    else:
        assert strip_newlines_(case.val, *case.args, **case.kwargs) == case.expect
