import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.math import divided_by
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
        expect=5,
    ),
    Case(
        description="integer value and float arg",
        val=10,
        args=[2.0],
        kwargs={},
        expect=5.0,
    ),
    Case(
        description="integer division",
        val=9,
        args=[2],
        kwargs={},
        expect=4,
    ),
    Case(
        description="float division",
        val=20,
        args=[7.0],
        kwargs={},
        expect=2.857142857142857,
    ),
    Case(
        description="string value and argument",
        val="10",
        args=["2.0"],
        kwargs={},
        expect=5.0,
    ),
    Case(
        description="string not a number",
        val="foo",
        args=["2.0"],
        kwargs={},
        expect=0,
    ),
    Case(
        description="arg string not a number",
        val="10",
        args=["foo"],
        kwargs={},
        expect=FilterArgumentError,
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
        expect=0,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[2],
        kwargs={},
        expect=0,
    ),
    Case(
        description="undefined argument",
        val=10,
        args=[ENV.undefined("test")],
        kwargs={},
        expect=FilterArgumentError,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_divided_by_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            divided_by(case.val, *case.args, **case.kwargs)
    else:
        assert divided_by(case.val, *case.args, **case.kwargs) == case.expect
