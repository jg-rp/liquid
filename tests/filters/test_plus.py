import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.math import plus
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
        description="integer value and integer arg",
        val=10,
        args=[2],
        kwargs={},
        expect=12,
    ),
    Case(
        description="integer value and float arg",
        val=10,
        args=[2.0],
        kwargs={},
        expect=12.0,
    ),
    Case(
        description="float value and float arg",
        val=10.1,
        args=[2.2],
        kwargs={},
        expect=12.3,
    ),
    Case(
        description="string value and string arg",
        val="10.1",
        args=["2.2"],
        kwargs={},
        expect=12.3,
    ),
    Case(
        description="string not a number",
        val="foo",
        args=["2.0"],
        kwargs={},
        expect=2.0,
    ),
    Case(
        description="arg string not a number",
        val="10",
        args=["foo"],
        kwargs={},
        expect=10,
    ),
    Case(
        description="too many args",
        val=5,
        args=[1, "5"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="not a string, int or float",
        val=object(),
        args=[1],
        kwargs={},
        expect=1,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[2],
        kwargs={},
        expect=2,
    ),
    Case(
        description="undefined argument",
        val=10,
        args=[ENV.undefined("test")],
        kwargs={},
        expect=10,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_plus_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            plus(case.val, *case.args, **case.kwargs)
    else:
        assert plus(case.val, *case.args, **case.kwargs) == case.expect
