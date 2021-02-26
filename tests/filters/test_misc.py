"""Test miscellaneous filter functions."""
import datetime
import unittest
from inspect import isclass
from typing import NamedTuple, Any, List, Dict

from liquid.environment import Environment
from liquid.exceptions import FilterArgumentError
from liquid.expression import EMPTY

from liquid.builtin.filters.misc import Size, Default, Date


class Case(NamedTuple):
    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class MiscFilterTestCase(unittest.TestCase):
    """Test miscellaneous filter functions."""

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

    def test_size(self):
        """Test `size` filter function."""
        test_cases = [
            Case(
                description="array", val=["a", "b", "c"], args=[], kwargs={}, expect=3
            ),
            Case(description="string", val="abc", args=[], kwargs={}, expect=3),
            Case(description="empty array", val=[], args=[], kwargs={}, expect=0),
            Case(
                description="unexpected argument",
                val=[1, 2, 3],
                args=["foo"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not an array or string",
                val=1,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Size, test_cases)

    def test_default(self):
        """Test `default` filter function."""
        test_cases = [
            Case(description="nil", val=None, args=["foo"], kwargs={}, expect="foo"),
            Case(description="false", val=False, args=["foo"], kwargs={}, expect="foo"),
            Case(
                description="empty string",
                val="",
                args=["foo"],
                kwargs={},
                expect="foo",
            ),
            Case(
                description="empty list",
                val=[],
                args=["foo"],
                kwargs={},
                expect="foo",
            ),
            Case(
                description="empty object",
                val={},
                args=["foo"],
                kwargs={},
                expect="foo",
            ),
            Case(
                description="not empty string",
                val="hello",
                args=["foo"],
                kwargs={},
                expect="hello",
            ),
            Case(
                description="not empty list",
                val=["hello"],
                args=["foo"],
                kwargs={},
                expect=["hello"],
            ),
            Case(
                description="not empty object",
                val={"title": "hello"},
                args=["foo"],
                kwargs={},
                expect={"title": "hello"},
            ),
            Case(
                description="too many arguments",
                val=None,
                args=["foo", "bar"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="missing argument",
                val=None,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not an array or string",
                val={},
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="false returns default",
                val=False,
                args=["bar"],
                kwargs={},
                expect="bar",
            ),
            Case(
                description="empty returns default",
                val=EMPTY,
                args=["bar"],
                kwargs={},
                expect="bar",
            ),
            Case(
                description="allow false",
                val=False,
                args=["bar"],
                kwargs={"allow_false": True},
                expect=False,
            ),
        ]

        self._test(Default, test_cases)

    def test_date(self):
        """Test `date` filter function."""
        test_cases = [
            Case(
                description="datetime object",
                val=datetime.datetime(2002, 1, 1, 11, 45, 13),
                args=[r"%a, %b %d, %y"],
                kwargs={},
                expect="Tue, Jan 01, 02",
            ),
            Case(
                description="well formed string",
                val="March 14, 2016",
                args=[r"%b %d, %y"],
                kwargs={},
                expect="Mar 14, 16",
            ),
            Case(
                description="too many arguments",
                val=datetime.datetime(2001, 2, 1, 11, 45, 13),
                args=[r"%a, %b %d, %y", "foo"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not a date or time",
                val=[],
                args=[r"%a, %b %d, %y"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="missing argument",
                val=None,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Date, test_cases)
