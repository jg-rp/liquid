import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import reverse
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
        description="lists of strings",
        val=["b", "a", "B", "A"],
        args=[],
        kwargs={},
        expect=["A", "B", "a", "b"],
    ),
    Case(
        description="lists of things",
        val=["a", "b", 1, [], {}],
        args=[],
        kwargs={},
        expect=[{}, 1, "b", "a"],
    ),
    Case(
        description="empty list",
        val=[],
        args=[],
        kwargs={},
        expect=[],
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
        val=123,
        args=[],
        kwargs={},
        expect=[123],
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect=[],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_reverse_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            reverse(case.val, *case.args, **case.kwargs)
    else:
        assert reverse(case.val, *case.args, **case.kwargs) == case.expect
