import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.array import where
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
        description="lists of object",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
        args=["title"],
        kwargs={},
        expect=[{"title": "foo"}, {"title": "bar"}],
    ),
    Case(
        description="lists of object with equality test",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
        args=["title", "bar"],
        kwargs={},
        expect=[{"title": "bar"}],
    ),
    Case(
        description="value not an array",
        val=1234,
        args=["title"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="missing argument",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
        args=[],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="too many arguments",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
        args=["title", "bar", "foo"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=["title", "bar"],
        kwargs={},
        expect=[],
    ),
    Case(
        description="undefined first argument",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
        args=[ENV.undefined("test"), "bar"],
        kwargs={},
        expect=[],
    ),
    Case(
        description="undefined second argument",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
        args=["title", ENV.undefined("test")],
        kwargs={},
        expect=[{"title": "foo"}, {"title": "bar"}],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_where_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            where(case.val, *case.args, **case.kwargs)
    else:
        assert where(case.val, *case.args, **case.kwargs) == case.expect
