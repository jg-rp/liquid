import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import truncatewords
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
        description="default end",
        val="Ground control to Major Tom.",
        args=[3],
        kwargs={},
        expect="Ground control to...",
    ),
    Case(
        description="custom end",
        val="Ground control to Major Tom.",
        args=[3, "--"],
        kwargs={},
        expect="Ground control to--",
    ),
    Case(
        description="no end",
        val="Ground control to Major Tom.",
        args=[3, ""],
        kwargs={},
        expect="Ground control to",
    ),
    Case(
        description="fewer words than word count",
        val="Ground control",
        args=[3],
        kwargs={},
        expect="Ground control",
    ),
    Case(
        description="not a string",
        val=5,
        args=[10],
        kwargs={},
        expect="5",
    ),
    Case(
        description="too many arguments",
        val="hello",
        args=[5, "foo", "bar"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="reference implementation test 1",
        val="测试测试测试测试",
        args=[5],
        kwargs={},
        expect="测试测试测试测试",
    ),
    Case(
        description="reference implementation test 2",
        val="one two three",
        args=[2, 1],
        kwargs={},
        expect="one two1",
    ),
    Case(
        description="reference implementation test 3",
        val="one  two\tthree\nfour",
        args=[3],
        kwargs={},
        expect="one two three...",
    ),
    Case(
        description="reference implementation test 4",
        val="one two three four",
        args=[2],
        kwargs={},
        expect="one two...",
    ),
    Case(
        description="reference implementation test 5",
        val="one two three four",
        args=[0],
        kwargs={},
        expect="one...",
    ),
    Case(
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[5],
        kwargs={},
        expect="",
    ),
    Case(
        description="undefined first argument",
        val="one two three four",
        args=[ENV.undefined("test")],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined second argument",
        val="one two three four",
        args=[2, ENV.undefined("test")],
        kwargs={},
        expect="one two",
    ),
    Case(
        description="very long argument",
        val="",
        args=[100000000000000],
        kwargs={},
        expect="",
    ),
    Case(
        description="default number of words is 15",
        val="a b c d e f g h i j k l m n o p q",
        args=[],
        kwargs={},
        expect="a b c d e f g h i j k l m n o...",
    ),
    Case(
        description="big positive argument",
        val="one two three four",
        args=[1 << 31],
        kwargs={},
        expect="one two three four",
    ),
    Case(
        description="big negative argument",
        val="one two three four",
        args=[-(1 << 31)],
        kwargs={},
        expect="one...",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_truncatewords_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            truncatewords(case.val, *case.args, **case.kwargs)
    else:
        assert truncatewords(case.val, *case.args, **case.kwargs) == case.expect
