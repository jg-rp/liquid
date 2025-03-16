import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import append
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
        description="concat",
        val="hello",
        args=["there"],
        kwargs={},
        expect="hellothere",
    ),
    Case(
        description="not a string",
        val=5,
        args=["there"],
        kwargs={},
        expect="5there",
    ),
    Case(
        description="argument not a string",
        val="hello",
        args=[5],
        kwargs={},
        expect="hello5",
    ),
    Case(
        description="missing argument",
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
        args=["hi"],
        kwargs={},
        expect="hi",
    ),
    Case(
        description="undefined argument",
        val="hi",
        args=[ENV.undefined("test")],
        kwargs={},
        expect="hi",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_append_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            append(case.val, *case.args, **case.kwargs)
    else:
        assert append(case.val, *case.args, **case.kwargs) == case.expect
