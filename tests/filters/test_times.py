import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.math import times
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
        description="int times int",
        val=5,
        args=[2],
        kwargs={},
        expect=10,
    ),
    Case(
        description="int times float",
        val=5,
        args=[2.1],
        kwargs={},
        expect=10.5,
    ),
    Case(
        description="int times float",
        val=5,
        args=[2.1],
        kwargs={},
        expect=10.5,
    ),
    Case(
        description="float times float",
        val=5.0,
        args=[2.1],
        kwargs={},
        expect=10.5,
    ),
    Case(
        description="string times string",
        val="5.0",
        args=["2.1"],
        kwargs={},
        expect=10.5,
    ),
    Case(
        description="negative multiplication",
        val=-5,
        args=[2],
        kwargs={},
        expect=-10,
    ),
    Case(
        description="missing arg",
        val=5,
        args=[],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="too many args",
        val=5,
        args=[1, 2],
        kwargs={},
        expect=FilterArgumentError,
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
        val=5,
        args=[ENV.undefined("test")],
        kwargs={},
        expect=0,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_times_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            times(case.val, *case.args, **case.kwargs)
    else:
        assert times(case.val, *case.args, **case.kwargs) == case.expect
