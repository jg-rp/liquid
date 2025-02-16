import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.math import round_
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
        description="float round down",
        val=5.1,
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="float round up",
        val=5.6,
        args=[],
        kwargs={},
        expect=6,
    ),
    Case(
        description="float as a string",
        val="5.6",
        args=[],
        kwargs={},
        expect=6,
    ),
    Case(
        description="string argument",
        val=5.666,
        args=["1"],
        kwargs={},
        expect=5.7,
    ),
    Case(
        description="decimal places",
        val="5.666666",
        args=[2],
        kwargs={},
        expect=5.67,
    ),
    Case(
        description="integer",
        val=5,
        args=[],
        kwargs={},
        expect=5,
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
        val=5.666,
        args=[ENV.undefined("test")],
        kwargs={},
        expect=6,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_round_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            round_(case.val, *case.args, **case.kwargs)
    else:
        assert round_(case.val, *case.args, **case.kwargs) == case.expect
