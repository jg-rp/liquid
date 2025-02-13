import operator
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from inspect import isclass
from typing import Any
from typing import Dict
from typing import List

import pytest

from liquid import Environment
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError
from liquid.extra.filters._json import JSON


@dataclass
class Case:
    """Test helper class."""

    description: str
    val: Any
    expect: Any
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockData:
    """Mock data class."""

    length: int
    width: int


ENV = Environment()

TEST_CASES = [
    Case(
        description="serialize a string",
        val="hello",
        args=[],
        kwargs={},
        expect='"hello"',
    ),
    Case(
        description="serialize an int",
        val=42,
        args=[],
        kwargs={},
        expect="42",
    ),
    Case(
        description="serialize a dict with list",
        val={"foo": [1, 2, 3]},
        args=[],
        kwargs={},
        expect='{"foo": [1, 2, 3]}',
    ),
    Case(
        description="serialize an arbitrary object",
        val={"foo": MockData(3, 4)},
        args=[],
        kwargs={},
        expect=FilterArgumentError,
    ),
    Case(
        description="with indent",
        val={"foo": [1, 2, 3]},
        args=[4],
        kwargs={},
        expect='{\n    "foo": [\n        1,\n        2,\n        3\n    ]\n}',
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_json_filter(case: Case) -> None:
    json_ = JSON()
    if isclass(case.expect) and issubclass(case.expect, Error):
        with pytest.raises(case.expect):
            json_(case.val, *case.args, **case.kwargs)
    else:
        assert json_(case.val, *case.args, **case.kwargs) == case.expect


def test_json_encoder_func() -> None:
    def default(obj: object) -> Any:
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        raise TypeError(f"can't serialize object {obj}")

    json_ = JSON(default=default)
    assert json_({"foo": MockData(3, 4)}) == r'{"foo": {"length": 3, "width": 4}}'
