import operator
from dataclasses import dataclass

import pytest

from liquid import Environment


@dataclass
class Case:
    description: str
    source: str
    data: dict[str, object]
    expect: str


ENV = Environment(extra=True)

TEST_CASES = [
    Case(
        description="array of strings",
        source="{{ a | index: 'b' }}",
        data={"a": ["a", "b", "c"]},
        expect="1",
    ),
    Case(
        description="item does not exist",
        source="{{ a | index: 'z' }}",
        data={"a": ["a", "b", "c"]},
        expect="",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_index_filter(case: Case) -> None:
    assert ENV.render(case.source, case.data) == case.expect
