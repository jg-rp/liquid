import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.array import uniq
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError


@dataclass
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: List[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


ENV = Environment()

TEST_CASES = [
    Case(
        description="lists of strings",
        val=["a", "b", "b", "a"],
        args=[],
        kwargs={},
        expect=["a", "b"],
    ),
    Case(
        description="lists of things",
        val=["a", "b", 1, 1],
        args=[],
        kwargs={},
        expect=["a", "b", 1],
    ),
    Case(
        description="empty list",
        val=[],
        args=[],
        kwargs={},
        expect=[],
    ),
    Case(
        description="unhashable items",
        val=["a", "b", [], {}, {}],
        args=[],
        kwargs={},
        expect=["a", "b", {}],
    ),
    Case(
        description="unexpected argument",
        val=["a", "b"],
        args=["foo", "bar"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="value not an array",
        val="a, b",
        args=[],
        kwargs={},
        expect=["a, b"],
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
def test_uniq_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            uniq(case.val, *case.args, **case.kwargs)
    else:
        assert uniq(case.val, *case.args, **case.kwargs) == case.expect
