"""Test math filter functions."""
import unittest
from inspect import isclass
from typing import NamedTuple, Any, List, Dict

from liquid.environment import Environment
from liquid.exceptions import FilterArgumentError

from liquid.builtin.filters.array import (
    Join,
    First,
    Last,
    Concat,
    Map,
    Reverse,
    Sort,
    SortNatural,
    Where,
    Uniq,
    Compact,
)


class Case(NamedTuple):
    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class ArrayFilterTestCase(unittest.TestCase):
    """Test array filter functions."""

    def _test(self, filter_cls, test_cases):
        """Helper method for running lists of `Case`s"""
        env = Environment()
        func = filter_cls(env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(
                    case.expect, FilterArgumentError
                ):
                    with self.assertRaises(case.expect):
                        func(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        func(case.val, *case.args, **case.kwargs), case.expect
                    )

    def test_join(self):
        """Test `join` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["a", "b"],
                args=[
                    ", ",
                ],
                kwargs={},
                expect="a, b",
            ),
            Case(
                description="missing argument",
                val=["a", "b"],
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val=["a", "b"],
                args=[", ", ""],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="arguments not a string",
                val=["a", "b"],
                args=[5],
                kwargs={},
                expect="a5b",
            ),
            Case(
                description="value not an array",
                val=12,
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value array contains non string",
                val=["a", "b", 5],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Join, test_cases)

    def test_first(self):
        """Test `first` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["a", "b"],
                args=[],
                kwargs={},
                expect="a",
            ),
            Case(
                description="lists of things",
                val=["a", "b", 1, [], {}],
                args=[],
                kwargs={},
                expect="a",
            ),
            Case(
                description="empty list",
                val=[],
                args=[],
                kwargs={},
                expect=None,
            ),
            Case(
                description="unexpected argument",
                val=["a", "b"],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value not an array",
                val=1,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(First, test_cases)

    def test_last(self):
        """Test `last` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["a", "b"],
                args=[],
                kwargs={},
                expect="b",
            ),
            Case(
                description="lists of things",
                val=["a", "b", 1, [], {}],
                args=[],
                kwargs={},
                expect={},
            ),
            Case(
                description="empty list",
                val=[],
                args=[],
                kwargs={},
                expect=None,
            ),
            Case(
                description="unexpected argument",
                val=["a", "b"],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value not an array",
                val=1,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Last, test_cases)

    def test_concat(self):
        """Test `concat` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["a", "b"],
                args=[["c", "d"]],
                kwargs={},
                expect=["a", "b", "c", "d"],
            ),
            Case(
                description="missing argument",
                val=["a", "b"],
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val=["a", "b"],
                args=[["c", "d"], ""],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="arguments not a list",
                val=["a", "b"],
                args=[5],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not an array",
                val="a, b",
                args=[["c", "d"]],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="array contains non string",
                val=["a", "b", 5],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Concat, test_cases)

    def test_map(self):
        """Test `map` filter function."""

        test_cases = [
            Case(
                description="lists of objects",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
                args=["title"],
                kwargs={},
                expect=["foo", "bar", "baz"],
            ),
            Case(
                description="missing argument",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
                args=["title", ""],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="missing property",
                val=[{"title": "foo"}, {"title": "bar"}, {"heading": "baz"}],
                args=["title"],
                kwargs={},
                expect=["foo", "bar", None],
            ),
            Case(
                description="value not an array",
                val=123,
                args=["title"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="array contains non object",
                val=[{"title": "foo"}, {"title": "bar"}, 5, []],
                args=["title"],
                kwargs={},
                expect=["foo", "bar", None, None],
            ),
        ]

        self._test(Map, test_cases)

    def test_reverse(self):
        """Test `reverse` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["b", "a", "B", "A"],
                args=[],
                kwargs={},
                expect=["A", "B", "a", "b"],
            ),
            Case(
                description="lists of things",
                val=["a", "b", 1, [], {}],
                args=[],
                kwargs={},
                expect=[{}, [], 1, "b", "a"],
            ),
            Case(
                description="empty list",
                val=[],
                args=[],
                kwargs={},
                expect=[],
            ),
            Case(
                description="unexpected argument",
                val=["a", "b"],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value not an array",
                val=123,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Reverse, test_cases)

    def test_sort(self):
        """Test `sort` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["b", "a", "C", "B", "A"],
                args=[],
                kwargs={},
                expect=["A", "B", "C", "a", "b"],
            ),
            Case(
                description="lists of objects with key",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
                args=["title"],
                kwargs={},
                expect=[{"title": "Baz"}, {"title": "bar"}, {"title": "foo"}],
            ),
            Case(
                description="lists of objects with missing key",
                val=[{"title": "foo"}, {"title": "bar"}, {"heading": "Baz"}],
                args=["title"],
                kwargs={},
                expect=[{"title": "bar"}, {"title": "foo"}, {"heading": "Baz"}],
            ),
            Case(
                description="empty list",
                val=[],
                args=[],
                kwargs={},
                expect=[],
            ),
            Case(
                description="too many arguments",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
                args=["title", "heading"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value not an array",
                val=123,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Sort, test_cases)

    def test_sort_natural(self):
        """Test `sort_natural` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["b", "a", "C", "B", "A"],
                args=[],
                kwargs={},
                expect=["a", "A", "b", "B", "C"],
            ),
            Case(
                description="lists of strings with a None",
                val=["b", "a", None, "C", "B", "A"],
                args=[],
                kwargs={},
                expect=[None, "a", "A", "b", "B", "C"],
            ),
            Case(
                description="lists of objects with key",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
                args=["title"],
                kwargs={},
                expect=[{"title": "bar"}, {"title": "Baz"}, {"title": "foo"}],
            ),
            Case(
                description="lists of objects with missing key",
                val=[{"title": "foo"}, {"title": "bar"}, {"heading": "Baz"}],
                args=["title"],
                kwargs={},
                expect=[{"title": "bar"}, {"title": "foo"}, {"heading": "Baz"}],
            ),
            Case(
                description="empty list",
                val=[],
                args=[],
                kwargs={},
                expect=[],
            ),
            Case(
                description="too many arguments",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
                args=["title", "heading"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value not an array",
                val=1234,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(SortNatural, test_cases)

    def test_where(self):
        """Test `where` filter function."""

        test_cases = [
            Case(
                description="lists of object",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
                args=["title"],
                kwargs={},
                expect=[{"title": "foo"}, {"title": "bar"}],
            ),
            Case(
                description="lists of object with equality test",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
                args=["title", "bar"],
                kwargs={},
                expect=[{"title": "bar"}],
            ),
            Case(
                description="value not an array",
                val=1234,
                args=["title"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="missing argument",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many arguments",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
                args=["title", "bar", "foo"],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Where, test_cases)

    def test_uniq(self):
        """Test `uniq` filter function."""

        test_cases = [
            Case(
                description="lists of strings",
                val=["a", "b", "b", "a"],
                args=[],
                kwargs={},
                expect=["a", "b"],
            ),
            Case(
                description="lists of things",
                val=["a", "b", 1, 1],
                args=[],
                kwargs={},
                expect=["a", "b", 1],
            ),
            Case(
                description="empty list",
                val=[],
                args=[],
                kwargs={},
                expect=[],
            ),
            Case(
                description="unhashable items",
                val=["a", "b", [], {}],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="unexpected argument",
                val=["a", "b"],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value not an array",
                val="a, b",
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Uniq, test_cases)

    def test_compact(self):
        """Test `compact` filter function."""

        test_cases = [
            Case(
                description="lists with nil",
                val=["b", "a", None, "A"],
                args=[],
                kwargs={},
                expect=["b", "a", "A"],
            ),
            Case(
                description="empty list",
                val=[],
                args=[],
                kwargs={},
                expect=[],
            ),
            Case(
                description="unexpected argument",
                val=["a", "b"],
                args=[", "],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="value not an array",
                val=1,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Compact, test_cases)
