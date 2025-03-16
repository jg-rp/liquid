import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.misc import size
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
        description="array",
        val=["a", "b", "c"],
        args=[],
        kwargs={},
        expect=3,
    ),
    Case(
        description="string",
        val="abc",
        args=[],
        kwargs={},
        expect=3,
    ),
    Case(
        description="empty array",
        val=[],
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="unexpected argument",
        val=[1, 2, 3],
        args=["foo"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="not an array or string",
        val=1,
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[],
        kwargs={},
        expect=0,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_size_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            size(case.val, *case.args, **case.kwargs)
    else:
        assert size(case.val, *case.args, **case.kwargs) == case.expect
