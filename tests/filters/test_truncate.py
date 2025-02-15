import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.string import truncate
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
        description="default end",
        val="Ground control to Major Tom.",
        args=[20],
        kwargs={},
        expect="Ground control to...",
    ),
    Case(
        description="custom end",
        val="Ground control to Major Tom.",
        args=[25, ", and so on"],
        kwargs={},
        expect="Ground control, and so on",
    ),
    Case(
        description="no end",
        val="Ground control to Major Tom.",
        args=[20, ""],
        kwargs={},
        expect="Ground control to Ma",
    ),
    Case(
        description="string is shorter than length",
        val="Ground control",
        args=[20],
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
        description="undefined left value",
        val=ENV.undefined("test"),
        args=[5],
        kwargs={},
        expect="",
    ),
    Case(
        description="undefined first argument",
        val="Ground control to Major Tom.",
        args=[ENV.undefined("test")],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="undefined second argument",
        val="Ground control to Major Tom.",
        args=[20, ENV.undefined("test")],
        kwargs={},
        expect="Ground control to Ma",
    ),
    Case(
        description="default length is 50",
        val="Ground control to Major Tom. Ground control to Major Tom.",
        args=[],
        kwargs={},
        expect="Ground control to Major Tom. Ground control to ...",
    ),
    Case(
        description="big positive argument",
        val="foobar",
        args=[1 << 63],
        kwargs={},
        expect="foobar",
    ),
    Case(
        description="big negative argument",
        val="foobar",
        args=[-(1 << 63)],
        kwargs={},
        expect="...",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_truncate_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            truncate(case.val, *case.args, **case.kwargs)
    else:
        assert truncate(case.val, *case.args, **case.kwargs) == case.expect
