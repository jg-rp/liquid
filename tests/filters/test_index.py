import operator
from dataclasses import dataclass
from dataclasses import field
from inspect import isclass
from typing import Any
from typing import List

import pytest

from liquid import Environment
from liquid.exceptions import Error
from liquid.extra.filters.array import index


@dataclass
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: List[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


ENV = Environment()

TEST_CASES = [
    Case(
        description="array of strings",
        val=["a", "b", "c"],
        args=["b"],
        kwargs={},
        expect=1,
    ),
    Case(
        description="item does not exist",
        val=["a", "b", "c"],
        args=["z"],
        kwargs={},
        expect=None,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_index_filter(case: Case) -> None:
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            index(case.val, *case.args, **case.kwargs)
    else:
        assert index(case.val, *case.args, **case.kwargs) == case.expect
