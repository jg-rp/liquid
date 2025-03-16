import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import slice_
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
        description="zero",
        val="hello",
        args=[0],
        kwargs={},
        expect="h",
    ),
    Case(
        description="one",
        val="hello",
        args=[1],
        kwargs={},
        expect="e",
    ),
    Case(
        description="one length three",
        val="hello",
        args=[1, 3],
        kwargs={},
        expect="ell",
    ),
    Case(
        description="out of range",
        val="hello",
        args=[99],
        kwargs={},
        expect="",
    ),
    Case(
        description="not a string",
        val=5,
        args=[0],
        kwargs={},
        expect="5",
    ),
    Case(
        description="first argument not an integer",
        val="hello",
        args=["foo"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="second argument not an integer",
        val="hello",
        args=[5, "foo"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="missing arguments",
        val="hello",
        args=[],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="too many arguments",
        val="hello",
        args=[1, 2, 3],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="unexpected keyword arguments",
        val="hello",
        args=[1, 2],
        kwargs={"x": "y"},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[1, 3],
        kwargs={},
        expect="",
    ),
    Case(
        description="undefined first argument",
        val="hello",
        args=[ENV.undefined("test"), 3],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined second argument",
        val="hello",
        args=[1, ENV.undefined("test")],
        kwargs={},
        expect="e",
    ),
    Case(
        description="big negative second argument",
        val="foobar",
        args=[0, -(1 << 64)],
        kwargs={},
        expect="",
    ),
    Case(
        description="big positive second argument",
        val="foobar",
        args=[0, 1 << 63],
        kwargs={},
        expect="foobar",
    ),
    Case(
        description="big positive first argument",
        val="foobar",
        args=[1 << 63, 6],
        kwargs={},
        expect="",
    ),
    Case(
        description="big negative first argument",
        val="foobar",
        args=[-(1 << 63), 6],
        kwargs={},
        expect="",
    ),
    Case(
        description="array input",
        val=["f", "o", "o", "b", "a", "r"],
        args=[1, 3],
        kwargs={},
        expect=["o", "o", "b"],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_slice_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            slice_(case.val, *case.args, **case.kwargs)
    else:
        assert slice_(case.val, *case.args, **case.kwargs) == case.expect
