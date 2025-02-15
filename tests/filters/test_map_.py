import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.array import map_
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterError
from liquid.expression import NIL


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
        description="lists of objects",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
        args=["title"],
        kwargs={},
        expect=["foo", "bar", "baz"],
    ),
    Case(
        description="missing argument",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
        args=[],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="too many arguments",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
        args=["title", ""],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="missing property",
        val=[{"title": "foo"}, {"title": "bar"}, {"heading": "baz"}],
        args=["title"],
        kwargs={},
        expect=["foo", "bar", NIL],
    ),
    Case(
        description="value not an array",
        val=123,
        args=["title"],
        kwargs={},
        expect=FilterError,
    ),
    Case(
        description="array contains non object",
        val=[{"title": "foo"}, {"title": "bar"}, 5, []],
        args=["title"],
        kwargs={},
        expect=FilterError,
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=["title"],
        kwargs={},
        expect=[],
    ),
    Case(
        description="undefined argument",
        val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
        args=[ENV.undefined("test")],
        kwargs={},
        expect=[NIL, NIL, NIL],
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_map_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            map_(case.val, *case.args, **case.kwargs)
    else:
        assert map_(case.val, *case.args, **case.kwargs) == case.expect
