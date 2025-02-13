import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError
from liquid.extra.filters.array import sort_numeric


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
        description="list of string ints",
        val=["10", "3", "2", "1"],
        args=[],
        kwargs={},
        expect=["1", "2", "3", "10"],
    ),
    Case(
        description="list of ints",
        val=[10, 3, 2, 1],
        args=[],
        kwargs={},
        expect=[1, 2, 3, 10],
    ),
    Case(
        description="list of floats",
        val=[10.1, 3.5, 2.3, 1.1, 1.01],
        args=[],
        kwargs={},
        expect=[1.01, 1.1, 2.3, 3.5, 10.1],
    ),
    Case(
        description="negative string ints",
        val=["1", "-1"],
        args=[],
        kwargs={},
        expect=["-1", "1"],
    ),
    Case(
        description="empty list",
        val=[],
        args=[],
        kwargs={},
        expect=[],
    ),
    Case(
        description="string input",
        val="12345",
        args=[],
        kwargs={},
        expect=["12345"],
    ),
    Case(
        description="not a sequence",
        val=None,
        args=[],
        kwargs={},
        expect=[None],
    ),
    Case(
        description="empty list with key argument",
        val=[],
        args=["x"],
        kwargs={},
        expect=[],
    ),
    Case(
        description="tuple of ints",
        val=(10, 3, 2, 1),
        args=[],
        kwargs={},
        expect=[1, 2, 3, 10],
    ),
    Case(
        description="list of dicts without a key argument",
        val=[{"y": "-1", "x": "10"}, {"x": "3"}, {"x": "2"}, {"x": "1"}],
        args=[],
        kwargs={},
        expect=[{"y": "-1", "x": "10"}, {"x": "1"}, {"x": "2"}, {"x": "3"}],
    ),
    Case(
        description="list of dicts with string int values",
        val=[{"y": "-1", "x": "10"}, {"x": "3"}, {"x": "2"}, {"x": "1"}],
        args=["x"],
        kwargs={},
        expect=[{"x": "1"}, {"x": "2"}, {"x": "3"}, {"y": "-1", "x": "10"}],
    ),
    Case(
        description="dotted with leading non-digit characters",
        val=["v1.2", "v1.9", "v10.0", "v1.10", "v1.1.0"],
        args=[],
        kwargs={},
        expect=["v1.1.0", "v1.2", "v1.9", "v1.10", "v10.0"],
    ),
    Case(
        description="leading zeros",
        val=["107", "042", "0001", "02", "17"],
        args=[],
        kwargs={},
        expect=["0001", "02", "17", "042", "107"],
    ),
    Case(
        description="trailing non-digits",
        val=["42 Some Street", "7 Some Street", "101 Some Street"],
        args=[],
        kwargs={},
        expect=["7 Some Street", "42 Some Street", "101 Some Street"],
    ),
    Case(
        description="too many arguments",
        val=["1", "2"],
        args=["x", "y"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="key argument and non-mapping input",
        val=["2", "1"],
        args=["x"],
        kwargs={},
        expect=["2", "1"],
    ),
    Case(
        description="input containing booleans",
        val=["2", True, "1"],
        args=[],
        kwargs={},
        expect=["1", "2", True],
    ),
    Case(
        description="list of dicts with some missing keys",
        val=[{"y": "-1", "x": "10"}, {"x": "3"}, {"x": "2"}, {"y": "1"}],
        args=["x"],
        kwargs={},
        expect=[{"x": "2"}, {"x": "3"}, {"y": "-1", "x": "10"}, {"y": "1"}],
    ),
    Case(
        description="list containing non sequence amongst dicts",
        val=[{"y": "-1", "x": "10"}, {"x": "3"}, {"x": "2"}, None],
        args=["x"],
        kwargs={},
        expect=[{"x": "2"}, {"x": "3"}, {"y": "-1", "x": "10"}, None],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_sort_numeric_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            sort_numeric(case.val, *case.args, **case.kwargs)
    else:
        assert sort_numeric(case.val, *case.args, **case.kwargs) == case.expect
