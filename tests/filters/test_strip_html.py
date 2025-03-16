import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.string import strip_html
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
        description="some HTML markup",
        val="Have <em>you</em> read <strong>Ulysses</strong> &amp; &#20;?",
        args=[],
        kwargs={},
        expect="Have you read Ulysses &amp; &#20;?",
    ),
    Case(
        description="some HTML markup with HTML comment",
        val="<!-- Have --><em>you</em> read <strong>Ulysses</strong> &amp; &#20;?",
        args=[],
        kwargs={},
        expect="you read Ulysses &amp; &#20;?",
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
def test_strip_html_filter(case: Case) -> None:
    strip_html_ = partial(strip_html, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, LiquidError):
        with pytest.raises(case.expect):
            strip_html_(case.val, *case.args, **case.kwargs)
    else:
        assert strip_html_(case.val, *case.args, **case.kwargs) == case.expect
