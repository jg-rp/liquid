import decimal
import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.misc import default
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


class MockDrop:  # pragma: no cover
    def __init__(self, val: Any) -> None:
        self.val = val

    def __eq__(self, other: object) -> bool:
        return bool(isinstance(other, MockDrop) and self.val == other.val)

    def __str__(self) -> str:
        return "hello mock drop"

    def __liquid__(self) -> object:
        return self.val


class NoLiquidDrop:  # pragma: no cover
    def __init__(self, val: Any) -> None:
        self.val = val

    def __eq__(self, other: object) -> bool:
        return bool(isinstance(other, NoLiquidDrop) and self.val == other.val)

    def __str__(self) -> str:
        return "hello no liquid drop"


class FalsyDrop:  # pragma: no cover
    def __init__(self, val: Any) -> None:
        self.val = val

    def __eq__(self, other: object) -> bool:
        if isinstance(other, bool) and self.val == other:
            return True
        return bool(isinstance(other, FalsyDrop) and self.val == other.val)

    def __str__(self) -> str:
        return "falsy drop"

    def __bool__(self) -> bool:
        return False


ENV = Environment()

TEST_CASES = [
    Case(
        description="nil",
        val=None,
        args=["foo"],
        kwargs={},
        expect="foo",
    ),
    Case(
        description="false",
        val=False,
        args=["foo"],
        kwargs={},
        expect="foo",
    ),
    Case(
        description="empty string",
        val="",
        args=["foo"],
        kwargs={},
        expect="foo",
    ),
    Case(
        description="empty list",
        val=[],
        args=["foo"],
        kwargs={},
        expect="foo",
    ),
    Case(
        description="empty object",
        val={},
        args=["foo"],
        kwargs={},
        expect="foo",
    ),
    Case(
        description="not empty string",
        val="hello",
        args=["foo"],
        kwargs={},
        expect="hello",
    ),
    Case(
        description="not empty list",
        val=["hello"],
        args=["foo"],
        kwargs={},
        expect=["hello"],
    ),
    Case(
        description="not empty object",
        val={"title": "hello"},
        args=["foo"],
        kwargs={},
        expect={"title": "hello"},
    ),
    Case(
        description="too many arguments",
        val=None,
        args=["foo", "bar"],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="missing argument",
        val=None,
        args=[],
        kwargs={},
        expect="",
    ),
    Case(
        description="false returns default",
        val=False,
        args=["bar"],
        kwargs={},
        expect="bar",
    ),
    Case(
        description="allow false",
        val=False,
        args=["bar"],
        kwargs={"allow_false": True},
        expect=False,
    ),
    Case(
        description="undefined",
        val=ENV.undefined("test"),
        args=["bar"],
        kwargs={},
        expect="bar",
    ),
    Case(
        description="a false drop",
        val=MockDrop(False),
        args=["bar"],
        kwargs={},
        expect="bar",
    ),
    Case(
        description="a true drop",
        val=MockDrop(True),
        args=["bar"],
        kwargs={},
        expect=MockDrop(True),
    ),
    Case(
        description="simple drop is always true",
        val=NoLiquidDrop(False),
        args=["bar"],
        kwargs={},
        expect=NoLiquidDrop(False),
    ),
    Case(
        description="zero is not false",
        val=0,
        args=["bar"],
        kwargs={},
        expect=0,
    ),
    Case(
        description="0.0 is not false",
        val=0.0,
        args=["bar"],
        kwargs={},
        expect=0.0,
    ),
    Case(
        description="Decimal('0') is not false",
        val=decimal.Decimal("0"),
        args=["bar"],
        kwargs={},
        expect=decimal.Decimal("0"),
    ),
    Case(
        description="one is not false or true",
        val=1,
        args=["bar"],
        kwargs={},
        expect=1,
    ),
    Case(
        description="falsy drop",
        val=FalsyDrop(0),
        args=["bar"],
        kwargs={},
        expect="bar",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_default_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            default(case.val, *case.args, **case.kwargs)
    else:
        assert default(case.val, *case.args, **case.kwargs) == case.expect
