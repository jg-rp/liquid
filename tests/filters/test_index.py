import operator
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pytest

from liquid import Environment
from liquid.extra.filters.array import index


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
    assert index(case.val, *case.args, **case.kwargs) == case.expect
