import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.math import abs_
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
        description="positive integer",
        val=5,
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="negative integer",
        val=-5,
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="positive float",
        val=5.4,
        args=[],
        kwargs={},
        expect=5.4,
    ),
    Case(
        description="negative float",
        val=-5.4,
        args=[],
        kwargs={},
        expect=5.4,
    ),
    Case(
        description="zero",
        val=0,
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="positive string integer",
        val="5",
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="negative string integer",
        val="-5",
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="positive string float",
        val="5.1",
        args=[],
        kwargs={},
        expect=5.1,
    ),
    Case(
        description="negative string float",
        val="-5.1",
        args=[],
        kwargs={},
        expect=5.1,
    ),
    Case(
        description="unexpected argument",
        val=-3,
        args=[1],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="string not a number",
        val="hello",
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="not a string, int or float",
        val=object(),
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect=0,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_abs_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            abs_(case.val, *case.args, **case.kwargs)
    else:
        assert abs_(case.val, *case.args, **case.kwargs) == case.expect
