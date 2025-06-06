import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import url_encode
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
        description="some special URL characters",
        val="email address is bob@example.com!",
        args=[],
        kwargs={},
        expect="email+address+is+bob%40example.com%21",
    ),
    Case(
        description="not a string",
        val=5,
        args=[],
        kwargs={},
        expect="5",
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
def test_url_encode_filter(case: Case) -> None:
    url_encode_ = partial(url_encode, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            url_encode_(case.val, *case.args, **case.kwargs)
    else:
        assert url_encode_(case.val, *case.args, **case.kwargs) == case.expect
