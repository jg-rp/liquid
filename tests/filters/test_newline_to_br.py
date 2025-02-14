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
from liquid.builtin.filters.string import newline_to_br
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
        description="string with newlines",
        val="- apples\n- oranges\n",
        args=[],
        kwargs={},
        expect="- apples<br />\n- oranges<br />\n",
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
        description="reference implementation test 1",
        val="a\nb\nc",
        args=[],
        kwargs={},
        expect="a<br />\nb<br />\nc",
    ),
    Case(
        description="reference implementation test 2",
        val="a\r\nb\nc",
        args=[],
        kwargs={},
        expect="a<br />\nb<br />\nc",
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
def test_newline_to_br_filter(case: Case) -> None:
    newline_to_br_ = partial(newline_to_br, environment=ENV)
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            newline_to_br_(case.val, *case.args, **case.kwargs)
    else:
        assert newline_to_br_(case.val, *case.args, **case.kwargs) == case.expect
