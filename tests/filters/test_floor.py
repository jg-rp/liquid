import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.math import floor
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
        description="positive integer",
        val=5,
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="negative integer",
        val=-5,
        args=[],
        kwargs={},
        expect=-5,
    ),
    Case(
        description="positive float",
        val=5.4,
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="negative float",
        val=-5.4,
        args=[],
        kwargs={},
        expect=-6,
    ),
    Case(
        description="zero",
        val=0,
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="positive string float",
        val="5.1",
        args=[],
        kwargs={},
        expect=5,
    ),
    Case(
        description="negative string float",
        val="-5.1",
        args=[],
        kwargs={},
        expect=-6,
    ),
    Case(
        description="unexpected argument",
        val=-3.1,
        args=[1],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="string not a number",
        val="hello",
        args=[],
        kwargs={},
        expect=0,
    ),
    Case(
        description="not a string, int or float",
        val=object(),
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
def test_floor_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            floor(case.val, *case.args, **case.kwargs)
    else:
        assert floor(case.val, *case.args, **case.kwargs) == case.expect
