import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import base64_decode
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterError
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
        description="from string",
        val="XyMvLg==",
        args=[],
        kwargs={},
        expect="_#/.",
    ),
    Case(
        description="from string with URL unsafe",
        val=(
            "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXogQUJDREVGR0hJSktMTU5PUFFSU1RVV"
            "ldYWVogMTIzNDU2Nzg5MCAhQCMkJV4mKigpLT1fKy8/Ljo7W117fVx8"
        ),
        args=[],
        kwargs={},
        expect=(
            r"abcdefghijklmnopqrstuvwxyz "
            r"ABCDEFGHIJKLMNOPQRSTUVWXYZ "
            r"1234567890 !@#$%^&*()-=_+/?.:;[]{}\|"
        ),
    ),
    Case(
        description="not a string",
        val=5,
        args=[],
        kwargs={},
        expect=FilterError,
    ),
    Case(
        description="unexpected argument",
        val="hello",
        args=[5],
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
def test_base64_decode_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            base64_decode(case.val, *case.args, **case.kwargs)
    else:
        assert base64_decode(case.val, *case.args, **case.kwargs) == case.expect
