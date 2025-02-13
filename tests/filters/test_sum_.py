import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import sum_
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
        description="empty sequence",
        val=[],
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="only zeros",
        val=[0, 0, 0],
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="ints",
        val=[1, 2, 3],
        args=[],
        kwargs={},
        expect=6,
    ),
    Case(
        description="nested ints",
        val=[1, [2, [3]]],
        args=[],
        kwargs={},
        expect=6,
    ),
    Case(
        description="negative ints",
        val=[-1, -2, -3],
        args=[],
        kwargs={},
        expect=-6,
    ),
    Case(
        description="floats",
        val=[0.1, 0.2, 0.3],
        args=[],
        kwargs={},
        expect=0.6,
    ),
    Case(
        description="floats and ints",
        val=[0.1, 0.2, 0.3, 1, 2, 3],
        args=[],
        kwargs={},
        expect=6.6,
    ),
    Case(
        description="with key argument",
        val=[{"k": 1}, {"k": 2}, {"k": 3}],
        args=["k"],
        kwargs={},
        expect=6,
    ),
    Case(
        description="with key argument and numeric strings",
        val=[{"k": "1"}, {"k": "2"}, {"k": "3"}],
        args=["k"],
        kwargs={},
        expect=6,
    ),
    Case(
        description="list of dicts and no key",
        val=[{"k": 1}, {"k": 2}, {"k": 3}],
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="some missing keys",
        val=[{"k": 1}, {"k": 2}, {"x": 3}],
        args=["k"],
        kwargs={},
        expect=3,
    ),
    Case(
        description="key argument and non-mapping items",
        val=[1, 2, 3],
        args=["k"],
        kwargs={},
        expect=FilterArgumentError,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_sum_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            sum_(case.val, *case.args, **case.kwargs)
    else:
        assert sum_(case.val, *case.args, **case.kwargs) == case.expect
