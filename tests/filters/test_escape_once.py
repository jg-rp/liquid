import operator
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.builtin.filters.string import escape_once
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
        description="make HTML-safe",
        val="&lt;p&gt;test&lt;/p&gt;",
        args=[],
        kwargs={},
        expect="&lt;p&gt;test&lt;/p&gt;",
    ),
    Case(
        description="make HTML-safe from mixed safe and markup.",
        val="&lt;p&gt;test&lt;/p&gt;<p>test</p>",
        args=[],
        kwargs={},
        expect="&lt;p&gt;test&lt;/p&gt;&lt;p&gt;test&lt;/p&gt;",
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
        val="HELLO",
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
def test_escape_once_filter(case: Case) -> None:
    escape_once_ = partial(escape_once, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            escape_once_(case.val, *case.args, **case.kwargs)
    else:
        assert escape_once_(case.val, *case.args, **case.kwargs) == case.expect
