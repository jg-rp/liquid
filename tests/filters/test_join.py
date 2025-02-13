import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import join
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
        args=[
            "#",
        ],
        expect="a#b",
    ),
    Case(
        description="join a string",
        val="a, b",
        args=[
            "#",
        ],
        expect="a, b",
    ),
    Case(
        description="lists of integers",
        val=[1, 2],
        args=[
            "#",
        ],
        expect="1#2",
    ),
    Case(
        description="missing argument defaults to space",
        val=["a", "b"],
        args=[],
        expect="a b",
    ),
    Case(
        description="too many arguments",
        val=["a", "b"],
        args=[", ", ""],
        expect=FilterArgumentError,
    ),
    Case(
        description="arguments not a string",
        val=["a", "b"],
        args=[5],
        expect="a5b",
    ),
    Case(
        description="value not an array",
        val=12,
        args=[", "],
        expect="12",
    ),
    Case(
        description="value array contains non string",
        val=["a", "b", 5],
        args=["#"],
        expect="a#b#5",
    ),
    Case(
        description="join an undefined variable with a string",
        val=ENV.undefined("test"),
        args=[", "],
        expect="",
    ),
    Case(
        description="join an array variable with undefined",
        val=["a", "b"],
        args=[ENV.undefined("test")],
        expect="ab",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_join_filter(case: Case) -> None:
    join_ = partial(join, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            join_(case.val, *case.args, **case.kwargs)
    else:
        assert join_(case.val, *case.args, **case.kwargs) == case.expect
