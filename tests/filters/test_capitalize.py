import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import capitalize
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
        description="lower case string",
        val="hello",
        args=[],
        kwargs={},
        expect="Hello",
    ),
    Case(
        description="already capitalized string",
        val="Hello",
        args=[],
        kwargs={},
        expect="Hello",
    ),
    Case(
        description="unexpected argument",
        val="hello",
        args=[2],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect="",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_capitalize_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            capitalize(case.val, *case.args, **case.kwargs)
    else:
        assert capitalize(case.val, *case.args, **case.kwargs) == case.expect
