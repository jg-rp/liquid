import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import lstrip
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError


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
        description="left padded",
        val=" \t\r\n  hello",
        args=[],
        kwargs={},
        expect="hello",
    ),
    Case(
        description="right padded",
        val="hello \t\r\n  ",
        args=[],
        kwargs={},
        expect="hello \t\r\n  ",
    ),
    Case(
        description="left and right padded",
        val=" \t\r\n  hello  \t\r\n ",
        args=[],
        kwargs={},
        expect="hello  \t\r\n ",
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
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect="",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_lstrip_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            lstrip(case.val, *case.args, **case.kwargs)
    else:
        assert lstrip(case.val, *case.args, **case.kwargs) == case.expect
