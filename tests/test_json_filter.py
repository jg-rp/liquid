import operator
from dataclasses import asdict, dataclass, is_dataclass

import pytest

from liquid import Environment
from liquid.filters import JSON


@dataclass
class Case:
    description: str
    source: str
    data: dict[str, object]
    expect: str


@dataclass
class MockData:
    length: int
    width: int


ENV = Environment()

TEST_CASES = [
    Case(
        description="serialize a string",
        source="{{ 'hello' | json }}",
        data={},
        expect='"hello"',
    ),
    Case(
        description="serialize an int",
        source="{{ 42 | json }}",
        data={},
        expect="42",
    ),
    Case(
        description="serialize a dict with list",
        source="{{ d | json }}",
        data={"d": {"foo": [1, 2, 3]}},
        expect='{"foo": [1, 2, 3]}',
    ),
    Case(
        description="with indent",
        source="{{ d | json: 4 }}",
        data={"d": {"foo": [1, 2, 3]}},
        expect='{\n    "foo": [\n        1,\n        2,\n        3\n    ]\n}',
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_json_filter(case: Case) -> None:
    env = Environment(extra=True)
    assert env.render(case.source, case.data) == case.expect


def test_json_encoder_func() -> None:
    def default(obj: object) -> object:
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        raise TypeError(f"can't serialize object {obj}")

    env = Environment(extra=True)
    env.filters["json"] = JSON(default=default)

    assert (
        env.render("{{ d | json }}", {"d": {"foo": MockData(3, 4)}})
        == r'{"foo": {"length": 3, "width": 4}}'
    )
