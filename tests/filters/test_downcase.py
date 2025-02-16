import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import downcase
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
        description="make lower case",
        val="HELLO",
        args=[],
        kwargs={},
        expect="hello",
    ),
    Case(
        description="not a string",
        val=5,
        args=[],
        kwargs={},
        expect="5",
    ),
    Case(
        description="unexpected argument",
        val="HELLO",
        args=[5],
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
def test_downcase_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            downcase(case.val, *case.args, **case.kwargs)
    else:
        assert downcase(case.val, *case.args, **case.kwargs) == case.expect
