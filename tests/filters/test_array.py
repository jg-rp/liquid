"""Test math filter functions."""
import unittest

from functools import partial
from inspect import isclass

from typing import NamedTuple
from typing import Any
from typing import List
from typing import Dict

from liquid.environment import Environment

from liquid.exceptions import Error
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError

from liquid.builtin.filters._array import join
from liquid.builtin.filters._array import first
from liquid.builtin.filters._array import last
from liquid.builtin.filters._array import concat
from liquid.builtin.filters._array import map_
from liquid.builtin.filters._array import reverse
from liquid.builtin.filters._array import sort
from liquid.builtin.filters._array import sort_natural
from liquid.builtin.filters._array import where
from liquid.builtin.filters._array import uniq
from liquid.builtin.filters._array import compact

from liquid.builtin.filters.array import Join
from liquid.builtin.filters.array import First
from liquid.builtin.filters.array import Last
from liquid.builtin.filters.array import Concat
from liquid.builtin.filters.array import Map
from liquid.builtin.filters.array import Reverse
from liquid.builtin.filters.array import Sort
from liquid.builtin.filters.array import SortNatural
from liquid.builtin.filters.array import Where
from liquid.builtin.filters.array import Uniq
from liquid.builtin.filters.array import Compact


class Case(NamedTuple):
    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class ArrayFilterTestCase(unittest.TestCase):
    """Test array filter functions."""

    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, filter_cls, test_cases):
        """Helper method for running lists of `Case`s"""
        with self.assertWarns(DeprecationWarning):
            func = filter_cls(self.env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(case.expect, Error):
                    with self.assertRaises(case.expect):
                        func(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        func(case.val, *case.args, **case.kwargs), case.expect
                    )

    def _test_newstyle_filter(self, func, test_cases):
        if getattr(func, "with_environment", False):
            func = partial(func, environment=self.env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(case.expect, Error):
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
                    "#",
                ],
                kwargs={},
                expect="a#b",
            ),
            Case(
                description="join a string",
                val="a, b",
                args=[
                    "#",
                ],
                kwargs={},
                expect=FilterValueError,
            ),
            Case(
                description="lists of integers",
                val=[1, 2],
                args=[
                    "#",
                ],
                kwargs={},
                expect="1#2",
            ),
            Case(
                description="missing argument defaults to space",
                val=["a", "b"],
                args=[],
                kwargs={},
                expect="a b",
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
                expect=FilterValueError,
            ),
            Case(
                description="value array contains non string",
                val=["a", "b", 5],
                args=["#"],
                kwargs={},
                expect="a#b#5",
            ),
            Case(
                description="join an undefined variable with a string",
                val=self.env.undefined("test"),
                args=[", "],
                kwargs={},
                expect="",
            ),
            Case(
                description="join an array variable with undefined",
                val=["a", "b"],
                args=[self.env.undefined("test")],
                kwargs={},
                expect="ab",
            ),
        ]

        self._test(Join, test_cases)
        self._test_newstyle_filter(join, test_cases)

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
                val=12,
                args=[],
                kwargs={},
                expect=FilterValueError,
            ),
            Case(
                description="first of undefined",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=None,
            ),
        ]

        self._test(First, test_cases)
        self._test_newstyle_filter(first, test_cases)

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
                val=12,
                args=[],
                kwargs={},
                expect=FilterValueError,
            ),
            Case(
                description="last of undefined",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=None,
            ),
        ]

        self._test(Last, test_cases)
        self._test_newstyle_filter(last, test_cases)

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
                expect=FilterValueError,
            ),
            Case(
                description="array contains non string",
                val=["a", "b", 5],
                args=[["c", "d"]],
                kwargs={},
                expect=["a", "b", 5, "c", "d"],
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[["c", "d"]],
                kwargs={},
                expect=["c", "d"],
            ),
            Case(
                description="undefined argument",
                val=["a", "b"],
                args=[self.env.undefined("test")],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Concat, test_cases)
        self._test_newstyle_filter(concat, test_cases)

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
                expect=FilterValueError,
            ),
            Case(
                description="array contains non object",
                val=[{"title": "foo"}, {"title": "bar"}, 5, []],
                args=["title"],
                kwargs={},
                expect=FilterValueError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["title"],
                kwargs={},
                expect=[],
            ),
            Case(
                description="undefined argument",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "baz"}],
                args=[self.env.undefined("test")],
                kwargs={},
                expect=[None, None, None],
            ),
        ]

        self._test(Map, test_cases)
        self._test_newstyle_filter(map_, test_cases)

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
                expect=FilterValueError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=[],
            ),
        ]

        self._test(Reverse, test_cases)
        self._test_newstyle_filter(reverse, test_cases)

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
                expect=FilterValueError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=[],
            ),
            Case(
                description="undefined argument",
                val=[{"z": "z", "title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
                args=[self.env.undefined("test")],
                kwargs={},
                expect=FilterValueError,
            ),
            Case(
                description="sort by key targeting an array of strings",
                val=["Z", "b", "a", "C", "B", "A"],
                args=["title"],
                kwargs={},
                expect=["Z", "b", "a", "C", "B", "A"],
            ),
        ]

        self._test(Sort, test_cases)
        self._test_newstyle_filter(sort, test_cases)

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
                expect=FilterValueError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=[],
            ),
            Case(
                description="undefined argument",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
                args=[self.env.undefined("test")],
                kwargs={},
                expect=[{"title": "foo"}, {"title": "bar"}, {"title": "Baz"}],
            ),
        ]

        self._test(SortNatural, test_cases)
        self._test_newstyle_filter(sort_natural, test_cases)

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
                expect=FilterValueError,
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
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=["title", "bar"],
                kwargs={},
                expect=[],
            ),
            Case(
                description="undefined first argument",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
                args=[self.env.undefined("test"), "bar"],
                kwargs={},
                expect=[],
            ),
            Case(
                description="undefined second argument",
                val=[{"title": "foo"}, {"title": "bar"}, {"title": None}],
                args=["title", self.env.undefined("test")],
                kwargs={},
                expect=[{"title": "foo"}, {"title": "bar"}],
            ),
        ]

        self._test(Where, test_cases)
        self._test_newstyle_filter(where, test_cases)

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
                expect=FilterValueError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=[],
            ),
        ]

        self._test(Uniq, test_cases)
        self._test_newstyle_filter(uniq, test_cases)

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
                expect=FilterValueError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=[],
            ),
        ]

        self._test(Compact, test_cases)
        self._test_newstyle_filter(compact, test_cases)
