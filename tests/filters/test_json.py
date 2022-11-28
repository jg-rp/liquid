"""Test cases for the `json` filter function."""
import unittest

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from inspect import isclass

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import NamedTuple

from liquid.environment import Environment
from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError
from liquid.extra.filters._json import JSON


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


@dataclass
class MockData:
    """Mock data class."""

    length: int
    width: int


class JSONFilterTestCase(unittest.TestCase):
    """Test the JSON template filter."""

    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, func, test_cases: Iterable[Case]):
        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(case.expect, Error):
                    with self.assertRaises(case.expect):
                        func(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        func(case.val, *case.args, **case.kwargs), case.expect
                    )

    def test_json_filter(self) -> None:
        """Test `json` filter function."""
        test_cases = [
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

        self._test(JSON(), test_cases)

    def test_json_with_encoder_func(self) -> None:
        """Test `json` filter function with default encoder."""
        test_cases = [
            Case(
                description="serialize a dataclass",
                val={"foo": MockData(3, 4)},
                args=[],
                kwargs={},
                expect=r'{"foo": {"length": 3, "width": 4}}',
            ),
            Case(
                description="serialize an arbitrary object",
                val={"foo": object()},
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        def default(obj: object) -> Dict[str, Any]:
            if is_dataclass(obj):
                return asdict(obj)
            raise TypeError(f"can't serialize object {obj}")

        self._test(JSON(default=default), test_cases)
