import operator
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pytest

from liquid import Environment
from liquid.builtin.filters.array import reject


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
        description="concat",
        val=["x", "y", "cat", None],
        args=["c"],
        kwargs={},
        expect=None,
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_reject_filter(case: Case) -> None:
    assert reject(case.val, *case.args, **case.kwargs) == case.expect
