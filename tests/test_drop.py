import operator
from dataclasses import dataclass

import pytest

from liquid import AbstractDrop, ContextHint, Environment, RenderContext

# TODO: test drop contains
# TODO: test drop callable and awaitable


@dataclass
class Case:
    description: str
    template: str
    data: dict[str, object]
    expect: str


class GenericDrop[T](AbstractDrop):
    """Mock generic drop that wraps a primitive value."""

    def __init__(self, val: T):
        self.val = val

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        return self.val

    def __str__(self) -> str:
        return str(self.val)

    def __eq__(self, other: object) -> bool:
        return other == self.val

    def __bool__(self) -> bool:
        return bool(self.val)


class IntDrop(GenericDrop[int]):
    """Mock drop that wraps an integer value."""

    def __init__(self, val: int):
        self.val = val

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string":
                return str(self.val)
            case "data":
                return self.val
            case "numeric":
                return self.val
            case "boolean":
                return bool(self.val)

    def __int__(self) -> int:
        return self.val

    def __str__(self) -> str:
        return "one"

    def __eq__(self, other: object) -> bool:
        return other == self.val

    def __lt__(self, other: object) -> bool:
        if isinstance(other, IntDrop):
            other = other.val
        return self.val < other if isinstance(other, (float, int)) else False

    def __gt__(self, other: object) -> bool:
        return self.val > other if isinstance(other, (float, int)) else False


class ConfusedDrop(GenericDrop[bool]):
    """Mock drop that will evaluate to a boolean when used as an array index or hash
    key, or when used in a conditional expression, but will render as a string."""

    def __init__(self, val: bool):
        self.val = val

    def __str__(self) -> str:
        return "yay" if self.val else "nay"


TEST_CASES = [
    Case(
        description="int drop",
        template=r"{{ drop }}",
        data={"drop": IntDrop(1)},
        expect="one",
    ),
    Case(
        description="int drop as array index",
        template=r"{{ foo[drop] }}",
        data={"foo": ["a", "b", "c"], "drop": IntDrop(1)},
        expect="b",
    ),
    Case(
        description="int drop as hash key",
        template=r"{{ foo[drop] }}",
        data={"foo": {1: "a", 2: "b"}, "drop": IntDrop(1)},
        expect="a",
    ),
    Case(
        description="int drop as filter left value",
        template=r"{{ drop | plus: 1 }}",
        data={"drop": IntDrop(1)},
        expect="2",
    ),
    Case(
        description="int drop in boolean expression",
        template=r"{% if drop == 1 %}one{% endif %}",
        data={"drop": IntDrop(1)},
        expect="one",
    ),
    Case(
        description="int drop is less than int drop",
        template=r"{% if some < other %}hello{% endif %}",
        data={"some": IntDrop(1), "other": IntDrop(2)},
        expect="hello",
    ),
    Case(
        description="int drop in case expression",
        template=r"{% case drop %}{% when 1 %}one{% endcase %}",
        data={"drop": IntDrop(1)},
        expect="one",
    ),
    Case(
        description="boolean drop",
        template=r"{{ drop }}",
        data={"drop": GenericDrop[bool](False)},
        expect="False",
    ),
    Case(
        description="bool drop in boolean expression",
        template=r"{% if drop == true %}one{% endif %}",
        data={"drop": GenericDrop[bool](True)},
        expect="one",
    ),
    Case(
        description="false bool drop in boolean expression",
        template=r"{% if drop == true %}one{% endif %}",
        data={"drop": GenericDrop[bool](False)},
        expect="",
    ),
    Case(
        description="false bool drop is False",
        template=r"{% if drop %}one{% endif %}",
        data={"drop": GenericDrop[bool](False)},
        expect="",
    ),
    Case(
        description="bool drop in unless expression",
        template=r"{% unless drop %}hello{% endunless %}",
        data={"drop": GenericDrop[bool](True)},
        expect="",
    ),
    Case(
        description="confused drop",
        template=r"{{ drop }}",
        data={"drop": ConfusedDrop(False)},
        expect="nay",
    ),
    Case(
        description="filtered confused drop",
        template=r"{{ drop | upcase }}",
        data={"drop": ConfusedDrop(False)},
        expect="NAY",
    ),
    Case(
        description="compare confused drop",
        template=r"{% if drop %}{{ drop | upcase }}{% endif %}",
        data={"drop": ConfusedDrop(False)},
        expect="",
    ),
]


@pytest.mark.parametrize("case", TEST_CASES, ids=operator.attrgetter("description"))
def test_to_liquid(case: Case) -> None:
    env = Environment()
    template = env.parse(case.template)
    result = template.render(case.data)
    assert result == case.expect
