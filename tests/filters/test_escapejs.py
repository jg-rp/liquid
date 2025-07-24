import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.extra import escapejs
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import LiquidError


@dataclass
class Case:
    description: str
    val: Any
    expect: Any
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


ENV = Environment()

TEST_CASES = [
    Case(
        description="escape <script> tag",
        val="<script>alert('x')</script>",
        args=[],
        kwargs={},
        expect="\\u003Cscript\\u003Ealert(\\u0027x\\u0027)\\u003C/script\\u003E",
    ),
    Case(
        description="escape quotes and backslash",
        val='"foo\\bar"',
        args=[],
        kwargs={},
        expect="\\u0022foo\\u005Cbar\\u0022",
    ),
    Case(
        description="escape control characters",
        val="foo\x00bar\x1fbaz",
        args=[],
        kwargs={},
        expect="foo\\u0000bar\\u001Fbaz",
    ),
    Case(
        description="not a string",
        val=123,
        args=[],
        kwargs={},
        expect="123",
    ),
    Case(
        description="unexpected argument",
        val="test",
        args=[1],
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
def test_escapejs_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            escapejs(case.val, *case.args, **case.kwargs)
    else:
        assert escapejs(case.val, *case.args, **case.kwargs) == case.expect
