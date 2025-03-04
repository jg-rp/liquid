import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import sort_natural
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError


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
        expect=["a", "A", "b", "B", "C"],
    ),
    Case(
        description="lists of strings with a None",
        val=["b", "a", None, "C", "B", "A"],
        args=[],
        kwargs={},
        expect=["a", "A", "b", "B", "C", None],
    ),
    Case(
        description="lists of objects with key",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
        args=["title"],
        kwargs={},
        expect=[{"title": "bar"}, {"title": "Baz"}, {"title": "foo"}],
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
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
        args=["title", "heading"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="value not an array",
        val=1234,
        args=[],
        kwargs={},
        expect=[1234],
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
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
        args=[ENV.undefined("test")],
        kwargs={},
        expect=[{"title": "bar"}, {"title": "Baz"}, {"title": "foo"}],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_sort_natural_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            sort_natural(case.val, *case.args, **case.kwargs)
    else:
        assert sort_natural(case.val, *case.args, **case.kwargs) == case.expect
