import datetime
import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.misc import date
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
        description="datetime object",
        val=datetime.datetime(2002, 1, 1, 11, 45, 13),
        args=[r"%a, %b %d, %y"],
        kwargs={},
        expect="Tue, Jan 01, 02",
    ),
    Case(
        description="well formed string",
        val="March 14, 2016",
        args=[r"%b %d, %y"],
        kwargs={},
        expect="Mar 14, 16",
    ),
    Case(
        description="too many arguments",
        val=datetime.datetime(2001, 2, 1, 11, 45, 13),
        args=[r"%a, %b %d, %y", "foo"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="not a date or time",
        val=[],
        args=[r"%a, %b %d, %y"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="missing argument",
        val=None,
        args=[],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[r"%b %d, %y"],
        kwargs={},
        expect="",
    ),
    Case(
        description="undefined argument",
        val="March 14, 2016",
        args=[ENV.undefined("test")],
        kwargs={},
        expect="March 14, 2016",
    ),
    Case(
        description="special 'now' value",
        val="now",
        args=["%Y"],
        kwargs={},
        expect=datetime.datetime.now().strftime("%Y"),
    ),
    Case(
        description="special 'today' value",
        val="today",
        args=["%Y"],
        kwargs={},
        expect=datetime.datetime.now().strftime("%Y"),
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_date_filter(case: Case) -> None:
    date_ = partial(date, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            date_(case.val, *case.args, **case.kwargs)
    else:
        assert date_(case.val, *case.args, **case.kwargs) == case.expect
