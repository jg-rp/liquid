import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import last
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError


@dataclass(kw_only=True)
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
        expect="b",
    ),
    Case(
        description="lists of things",
        val=["a", "b", 1, [], {}],
        args=[],
        kwargs={},
        expect={},
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
        description="last of undefined",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect=None,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_last_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            last(case.val, *case.args, **case.kwargs)
    else:
        assert last(case.val, *case.args, **case.kwargs) == case.expect
