import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import replace_last
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
        description="not a string",
        val=5,
        args=["rain", "foo"],
        kwargs={},
        expect="5",
    ),
    Case(
        description="replace substrings",
        val="Take my protein pills and put my helmet on",
        args=["my", "your"],
        kwargs={},
        expect="Take my protein pills and put your helmet on",
    ),
    Case(
        description="argument not a string",
        val="hello5",
        args=[5, "your"],
        kwargs={},
        expect="helloyour",
    ),
    Case(
        description="missing argument",
        val="hello",
        args=["ll"],
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
        args=["how", "are", "you"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=["my", "your"],
        kwargs={},
        expect="",
    ),
    Case(
        description="undefined first argument",
        val="Take my protein pills and put my helmet on",
        args=[ENV.undefined("test"), "your"],
        kwargs={},
        expect="Take my protein pills and put my helmet onyour",
    ),
    Case(
        description="undefined second argument",
        val="Take my protein pills and put my helmet on",
        args=["my", ENV.undefined("test")],
        kwargs={},
        expect="Take my protein pills and put  helmet on",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_replace_last_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            replace_last(case.val, *case.args, **case.kwargs)
    else:
        assert replace_last(case.val, *case.args, **case.kwargs) == case.expect
