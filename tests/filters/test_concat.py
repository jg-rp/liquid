import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.array import concat
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
        description="lists of strings",
        val=["a", "b"],
        args=[["c", "d"]],
        kwargs={},
        expect=["a", "b", "c", "d"],
    ),
    Case(
        description="missing argument",
        val=["a", "b"],
        args=[],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="too many arguments",
        val=["a", "b"],
        args=[["c", "d"], ""],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="arguments not a list",
        val=["a", "b"],
        args=[5],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="not an array",
        val="a, b",
        args=[["c", "d"]],
        kwargs={},
        expect=["a, b", "c", "d"],
    ),
    Case(
        description="array contains non string",
        val=["a", "b", 5],
        args=[["c", "d"]],
        kwargs={},
        expect=["a", "b", 5, "c", "d"],
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[["c", "d"]],
        kwargs={},
        expect=["c", "d"],
    ),
    Case(
        description="undefined argument",
        val=["a", "b"],
        args=[ENV.undefined("test")],
        kwargs={},
        expect=FilterArgumentError,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_concat_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            concat(case.val, *case.args, **case.kwargs)
    else:
        assert concat(case.val, *case.args, **case.kwargs) == case.expect
