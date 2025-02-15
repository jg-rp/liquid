import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.string import strip
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError


@dataclass
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)


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
        expect="hello",
    ),
    Case(
        description="left and right padded",
        val=" \t\r\n  hello  \t\r\n ",
        args=[],
        kwargs={},
        expect="hello",
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
def test_strip_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            strip(case.val, *case.args, **case.kwargs)
    else:
        assert strip(case.val, *case.args, **case.kwargs) == case.expect
