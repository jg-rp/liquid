import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.string import remove
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError


@dataclass
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)


ENV = Environment()

TEST_CASES = [
    Case(
        description="remove substrings",
        val="I strained to see the train through the rain",
        args=["rain"],
        kwargs={},
        expect="I sted to see the t through the ",
    ),
    Case(
        description="not a string",
        val=5,
        args=["there"],
        kwargs={},
        expect="5",
    ),
    Case(
        description="argument not a string",
        val="hello",
        args=[5],
        kwargs={},
        expect="hello",
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
        args=["rain"],
        kwargs={},
        expect="",
    ),
    Case(
        description="undefined argument",
        val="I strained to see the train through the rain",
        args=[ENV.undefined("test")],
        kwargs={},
        expect="I strained to see the train through the rain",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_remove_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            remove(case.val, *case.args, **case.kwargs)
    else:
        assert remove(case.val, *case.args, **case.kwargs) == case.expect
