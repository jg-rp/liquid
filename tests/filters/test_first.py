import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import first
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
        description="lists of strings",
        val=["a", "b"],
        args=[],
        kwargs={},
        expect="a",
    ),
    Case(
        description="lists of things",
        val=["a", "b", 1, [], {}],
        args=[],
        kwargs={},
        expect="a",
    ),
    Case(
        description="empty list",
        val=[],
        args=[],
        kwargs={},
        expect=None,
    ),
    Case(
        description="unexpected argument",
        val=["a", "b"],
        args=[", "],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="value not an array",
        val=12,
        args=[],
        kwargs={},
        expect=None,
    ),
    Case(
        description="first of undefined",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect=None,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_first_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            first(case.val, *case.args, **case.kwargs)
    else:
        assert first(case.val, *case.args, **case.kwargs) == case.expect
