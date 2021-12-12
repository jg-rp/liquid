"""Test the "drop" API."""
# pylint: disable=missing-class-docstring
import unittest

from typing import Generic
from typing import NamedTuple
from typing import TypeVar

from liquid import Environment


class Case(NamedTuple):
    description: str
    template: str
    context: dict
    expect: str


DropT = TypeVar("DropT")


class Drop(Generic[DropT]):
    """Mock generic drop that wraps a primitive value."""

    def __init__(self, val: DropT):
        self.val = val

    def __liquid__(self) -> DropT:
        return self.val

    def __str__(self) -> str:
        return str(self.val)


class IntDrop:
    """Mock drop that wraps an integer value."""

    def __init__(self, val: int):
        self.val = val

    def __int__(self) -> int:
        return self.val

    def __str__(self) -> str:
        return "one"

    def __liquid__(self) -> int:
        return int(self)


class ConfusedDrop:
    """Mock drop that will evaluate to a boolean when used as an array index or hash
    key, or when used in a conditional expression, but will render as a string."""

    def __init__(self, val: bool):
        self.val = val

    def __liquid__(self) -> bool:
        return self.val

    def __str__(self) -> str:
        return "yay" if self.val else "nay"


class DropAPITestCase(unittest.TestCase):
    """Test the drop API."""

    def test_to_liquid(self):
        """Test that user defined classes can be used as primitives."""
        test_cases = [
            Case(
                description="int drop",
                template=r"{{ drop }}",
                context={"drop": IntDrop(1)},
                expect="one",
            ),
            Case(
                description="int drop as array index",
                template=r"{{ foo[drop] }}",
                context={"foo": ["a", "b", "c"], "drop": IntDrop(1)},
                expect="b",
            ),
            Case(
                description="int drop as hash key",
                template=r"{{ foo[drop] }}",
                context={"foo": {1: "a", 2: "b"}, "drop": IntDrop(1)},
                expect="a",
            ),
            Case(
                description="int drop as filter left value",
                template=r"{{ drop | plus: 1 }}",
                context={"drop": IntDrop(1)},
                expect="1",
            ),
            Case(
                description="int drop in boolean expression",
                template=r"{% if drop == 1 %}one{% endif %}",
                context={"drop": IntDrop(1)},
                expect="one",
            ),
            Case(
                description="int drop is less than int drop",
                template=r"{% if some < other %}hello{% endif %}",
                context={"some": IntDrop(1), "other": IntDrop(2)},
                expect="hello",
            ),
            Case(
                description="int drop in case expression",
                template=r"{% case drop %}{% when 1 %}one{% endcase %}",
                context={"drop": IntDrop(1)},
                expect="one",
            ),
            Case(
                description="boolean drop",
                template=r"{{ drop }}",
                context={"drop": Drop[bool](False)},
                expect="False",
            ),
            Case(
                description="bool drop in boolean expression",
                template=r"{% if drop == true %}one{% endif %}",
                context={"drop": Drop[bool](True)},
                expect="one",
            ),
            Case(
                description="false bool drop in boolean expression",
                template=r"{% if drop == true %}one{% endif %}",
                context={"drop": Drop[bool](False)},
                expect="",
            ),
            Case(
                description="false bool drop is False",
                template=r"{% if drop %}one{% endif %}",
                context={"drop": Drop[bool](False)},
                expect="",
            ),
            Case(
                description="bool drop in unless expression",
                template=r"{% unless drop %}hello{% endunless %}",
                context={"drop": Drop[bool](True)},
                expect="",
            ),
            Case(
                description="confused drop",
                template=r"{{ drop }}",
                context={"drop": ConfusedDrop(False)},
                expect="nay",
            ),
            Case(
                description="filtered confused drop",
                template=r"{{ drop | upcase }}",
                context={"drop": ConfusedDrop(False)},
                expect="NAY",
            ),
            Case(
                description="compare confused drop",
                template=r"{% if drop %}{{ drop | upcase }}{% endif %}",
                context={"drop": ConfusedDrop(False)},
                expect="",
            ),
        ]

        env = Environment()

        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)
                result = template.render(**case.context)
                self.assertEqual(result, case.expect)
