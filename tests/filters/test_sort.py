import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import sort
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterError
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
        val=["b", "a", "C", "B", "A"],
        args=[],
        kwargs={},
        expect=["A", "B", "C", "a", "b"],
    ),
    Case(
        description="lists of objects with key",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
        args=["title"],
        kwargs={},
        expect=[{"title": "Baz"}, {"title": "bar"}, {"title": "foo"}],
    ),
    Case(
        description="lists of objects with missing key",
        val=[{"title": "foo"}, {"title": "bar"}, {"heading": "Baz"}],
        args=["title"],
        kwargs={},
        expect=[{"title": "bar"}, {"title": "foo"}, {"heading": "Baz"}],
    ),
    Case(
        description="empty list",
        val=[],
        args=[],
        kwargs={},
        expect=[],
    ),
    Case(
        description="too many arguments",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
        args=["title", "heading"],
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
    Case(
        description="undefined argument",
        val=[{"z": "z", "title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
        args=[ENV.undefined("test")],
        kwargs={},
        expect=FilterError,
    ),
    Case(
        description="sort by key targeting an array of strings",
        val=["Z", "b", "a", "C", "A", "B"],
        args=["title"],
        kwargs={},
        expect=["Z", "b", "a", "C", "A", "B"],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_sort_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            sort(case.val, *case.args, **case.kwargs)
    else:
        assert sort(case.val, *case.args, **case.kwargs) == case.expect
