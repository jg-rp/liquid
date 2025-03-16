import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.math import at_least
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
        description="positive integer < arg",
        val=5,
        args=[8],
        kwargs={},
        expect=8,
    ),
    Case(
        description="positive integer > arg",
        val=8,
        args=[5],
        kwargs={},
        expect=8,
    ),
    Case(
        description="negative integer < arg",
        val=-8,
        args=[5],
        kwargs={},
        expect=5,
    ),
    Case(
        description="positive integer == arg",
        val=5,
        args=[5],
        kwargs={},
        expect=5,
    ),
    Case(
        description="positive float < arg",
        val=5.4,
        args=[8.9],
        kwargs={},
        expect=8.9,
    ),
    Case(
        description="positive float > arg",
        val=8.4,
        args=[5.9],
        kwargs={},
        expect=8.4,
    ),
    Case(
        description="positive string > arg",
        val="9",
        args=["8"],
        kwargs={},
        expect=9,
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
        args=[5],
        kwargs={},
        expect=5,
    ),
    Case(
        description="undefined argument",
        val=5,
        args=[ENV.undefined("test")],
        kwargs={},
        expect=5,
    ),
    Case(
        description="unacceptable left value",
        val="abc",
        args=[2],
        kwargs={},
        expect=2,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_at_least_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            at_least(case.val, *case.args, **case.kwargs)
    else:
        assert at_least(case.val, *case.args, **case.kwargs) == case.expect
