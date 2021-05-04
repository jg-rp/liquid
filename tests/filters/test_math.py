"""Test math filter functions."""
import unittest

from functools import partial
from inspect import isclass

from typing import NamedTuple
from typing import Any
from typing import List
from typing import Dict

from liquid.environment import Environment

from liquid.exceptions import FilterArgumentError

from liquid.builtin.filters._math import abs_
from liquid.builtin.filters._math import at_most
from liquid.builtin.filters._math import at_least
from liquid.builtin.filters._math import ceil
from liquid.builtin.filters._math import divided_by
from liquid.builtin.filters._math import floor
from liquid.builtin.filters._math import minus
from liquid.builtin.filters._math import plus
from liquid.builtin.filters._math import round_
from liquid.builtin.filters._math import times
from liquid.builtin.filters._math import modulo

from liquid.builtin.filters.math import Abs
from liquid.builtin.filters.math import AtMost
from liquid.builtin.filters.math import AtLeast
from liquid.builtin.filters.math import Ceil
from liquid.builtin.filters.math import DividedBy
from liquid.builtin.filters.math import Floor
from liquid.builtin.filters.math import Minus
from liquid.builtin.filters.math import Plus
from liquid.builtin.filters.math import Round
from liquid.builtin.filters.math import Times
from liquid.builtin.filters.math import Modulo


class Case(NamedTuple):
    """Table driven test case helper."""

    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class MathFilterTestCase(unittest.TestCase):
    """Test math filter functions."""

    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, filter_cls, test_cases):
        """Helper method for running lists of `Case`s"""
        with self.assertWarns(DeprecationWarning):
            func = filter_cls(self.env)

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

    def _test_newstyle_filter(self, func, test_cases):
        if getattr(func, "with_environment", False):
            func = partial(func, environment=self.env)

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

    def test_abs(self):
        """Test abs filter function."""

        test_cases = [
            Case(
                description="positive integer",
                val=5,
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="negative integer",
                val=-5,
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="positive float",
                val=5.4,
                args=[],
                kwargs={},
                expect=5.4,
            ),
            Case(
                description="negative float",
                val=-5.4,
                args=[],
                kwargs={},
                expect=5.4,
            ),
            Case(
                description="zero",
                val=0,
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="positive string integer",
                val="5",
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="negative string integer",
                val="-5",
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="positive string float",
                val="5.1",
                args=[],
                kwargs={},
                expect=5.1,
            ),
            Case(
                description="negative string float",
                val="-5.1",
                args=[],
                kwargs={},
                expect=5.1,
            ),
            Case(
                description="unexpected argument",
                val=-3,
                args=[1],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="string not a number",
                val="hello",
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="not a string, int or float",
                val=object(),
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=0,
            ),
        ]

        self._test(Abs, test_cases)
        self._test_newstyle_filter(abs_, test_cases)

    def test_at_most(self):
        """Test at_most filter function."""

        test_cases = [
            Case(
                description="positive integer < arg",
                val=5,
                args=[8],
                kwargs={},
                expect=5,
            ),
            Case(
                description="positive integer > arg",
                val=8,
                args=[5],
                kwargs={},
                expect=5,
            ),
            Case(
                description="negative integer < arg",
                val=-8,
                args=[5],
                kwargs={},
                expect=-8,
            ),
            Case(
                description="positive integer == arg",
                val=5,
                args=[5],
                kwargs={},
                expect=5,
            ),
            Case(
                description="positive float < arg",
                val=5.4,
                args=[8.9],
                kwargs={},
                expect=5.4,
            ),
            Case(
                description="positive float > arg",
                val=8.4,
                args=[5.9],
                kwargs={},
                expect=5.9,
            ),
            Case(
                description="positive string > arg",
                val="9",
                args=["8"],
                kwargs={},
                expect=8,
            ),
            Case(
                description="missing arg",
                val=5,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, 2],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[5],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined argument",
                val=5,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=0,
            ),
            Case(
                description="unacceptable left value",
                val="abc",
                args=[-2],
                kwargs={},
                expect=-2,
            ),
        ]

        self._test(AtMost, test_cases)
        self._test_newstyle_filter(at_most, test_cases)

    def test_at_least(self):
        """Test at_least filter function."""

        test_cases = [
            Case(
                description="positive integer < arg",
                val=5,
                args=[8],
                kwargs={},
                expect=8,
            ),
            Case(
                description="positive integer > arg",
                val=8,
                args=[5],
                kwargs={},
                expect=8,
            ),
            Case(
                description="negative integer < arg",
                val=-8,
                args=[5],
                kwargs={},
                expect=5,
            ),
            Case(
                description="positive integer == arg",
                val=5,
                args=[5],
                kwargs={},
                expect=5,
            ),
            Case(
                description="positive float < arg",
                val=5.4,
                args=[8.9],
                kwargs={},
                expect=8.9,
            ),
            Case(
                description="positive float > arg",
                val=8.4,
                args=[5.9],
                kwargs={},
                expect=8.4,
            ),
            Case(
                description="positive string > arg",
                val="9",
                args=["8"],
                kwargs={},
                expect=9,
            ),
            Case(
                description="missing arg",
                val=5,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, 2],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[5],
                kwargs={},
                expect=5,
            ),
            Case(
                description="undefined argument",
                val=5,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=5,
            ),
            Case(
                description="unacceptable left value",
                val="abc",
                args=[2],
                kwargs={},
                expect=2,
            ),
        ]

        self._test(AtLeast, test_cases)
        self._test_newstyle_filter(at_least, test_cases)

    def test_ceil(self):
        """Test ceil filter function."""

        test_cases = [
            Case(
                description="positive integer",
                val=5,
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="negative integer",
                val=-5,
                args=[],
                kwargs={},
                expect=-5,
            ),
            Case(
                description="positive float",
                val=5.4,
                args=[],
                kwargs={},
                expect=6,
            ),
            Case(
                description="negative float",
                val=-5.4,
                args=[],
                kwargs={},
                expect=-5,
            ),
            Case(
                description="zero",
                val=0,
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="positive string float",
                val="5.1",
                args=[],
                kwargs={},
                expect=6,
            ),
            Case(
                description="negative string float",
                val="-5.1",
                args=[],
                kwargs={},
                expect=-5,
            ),
            Case(
                description="unexpected argument",
                val=-3.1,
                args=[1],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="string not a number",
                val="hello",
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="not a string, int or float",
                val=object(),
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=0,
            ),
        ]

        self._test(Ceil, test_cases)
        self._test_newstyle_filter(ceil, test_cases)

    def test_floor(self):
        """Test floor filter function."""

        test_cases = [
            Case(
                description="positive integer",
                val=5,
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="negative integer",
                val=-5,
                args=[],
                kwargs={},
                expect=-5,
            ),
            Case(
                description="positive float",
                val=5.4,
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="negative float",
                val=-5.4,
                args=[],
                kwargs={},
                expect=-6,
            ),
            Case(
                description="zero",
                val=0,
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="positive string float",
                val="5.1",
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="negative string float",
                val="-5.1",
                args=[],
                kwargs={},
                expect=-6,
            ),
            Case(
                description="unexpected argument",
                val=-3.1,
                args=[1],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="string not a number",
                val="hello",
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="not a string, int or float",
                val=object(),
                args=[],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[],
                kwargs={},
                expect=0,
            ),
        ]

        self._test(Floor, test_cases)
        self._test_newstyle_filter(floor, test_cases)

    def test_divided_by(self):
        """Test divided_by filter function."""

        test_cases = [
            Case(
                description="integer value and integer arg",
                val=10,
                args=[2],
                kwargs={},
                expect=5,
            ),
            Case(
                description="integer value and float arg",
                val=10,
                args=[2.0],
                kwargs={},
                expect=5.0,
            ),
            Case(
                description="integer division",
                val=9,
                args=[2],
                kwargs={},
                expect=4,
            ),
            Case(
                description="float division",
                val=20,
                args=[7.0],
                kwargs={},
                expect=2.857142857142857,
            ),
            Case(
                description="string value and argument",
                val="10",
                args=["2.0"],
                kwargs={},
                expect=5.0,
            ),
            Case(
                description="string not a number",
                val="foo",
                args=["2.0"],
                kwargs={},
                expect=0,
            ),
            Case(
                description="arg string not a number",
                val="10",
                args=["foo"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, "5"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not a string, int or float",
                val=object(),
                args=[1],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[2],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined argument",
                val=10,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(DividedBy, test_cases)
        self._test_newstyle_filter(divided_by, test_cases)

    def test_minus(self):
        """Test minus filter function."""

        test_cases = [
            Case(
                description="integer value and integer arg",
                val=10,
                args=[2],
                kwargs={},
                expect=8,
            ),
            Case(
                description="integer value and float arg",
                val=10,
                args=[2.0],
                kwargs={},
                expect=8.0,
            ),
            Case(
                description="float value and float arg",
                val=10.1,
                args=[2.2],
                kwargs={},
                expect=7.9,
            ),
            Case(
                description="string value and string arg",
                val="10.1",
                args=["2.2"],
                kwargs={},
                expect=7.9,
            ),
            Case(
                description="string not a number",
                val="foo",
                args=["2.0"],
                kwargs={},
                expect=-2.0,
            ),
            Case(
                description="arg string not a number",
                val="10",
                args=["foo"],
                kwargs={},
                expect=10,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, "5"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not a string, int or float",
                val=object(),
                args=[1],
                kwargs={},
                expect=-1,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[2],
                kwargs={},
                expect=-2,
            ),
            Case(
                description="undefined argument",
                val=10,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=10,
            ),
        ]

        self._test(Minus, test_cases)
        self._test_newstyle_filter(minus, test_cases)

    def test_plus(self):
        """Test plus filter function."""

        test_cases = [
            Case(
                description="integer value and integer arg",
                val=10,
                args=[2],
                kwargs={},
                expect=12,
            ),
            Case(
                description="integer value and float arg",
                val=10,
                args=[2.0],
                kwargs={},
                expect=12.0,
            ),
            Case(
                description="float value and float arg",
                val=10.1,
                args=[2.2],
                kwargs={},
                expect=12.3,
            ),
            Case(
                description="string value and string arg",
                val="10.1",
                args=["2.2"],
                kwargs={},
                expect=12.3,
            ),
            Case(
                description="string not a number",
                val="foo",
                args=["2.0"],
                kwargs={},
                expect=2.0,
            ),
            Case(
                description="arg string not a number",
                val="10",
                args=["foo"],
                kwargs={},
                expect=10,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, "5"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not a string, int or float",
                val=object(),
                args=[1],
                kwargs={},
                expect=1,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[2],
                kwargs={},
                expect=2,
            ),
            Case(
                description="undefined argument",
                val=10,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=10,
            ),
        ]

        self._test(Plus, test_cases)
        self._test_newstyle_filter(plus, test_cases)

    def test_round(self):
        """Test round filter function."""

        test_cases = [
            Case(
                description="float round down",
                val=5.1,
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="float round up",
                val=5.6,
                args=[],
                kwargs={},
                expect=6,
            ),
            Case(
                description="float as a string",
                val="5.6",
                args=[],
                kwargs={},
                expect=6,
            ),
            Case(
                description="string argument",
                val=5.666,
                args=["1"],
                kwargs={},
                expect=5.7,
            ),
            Case(
                description="decimal places",
                val="5.666666",
                args=[2],
                kwargs={},
                expect=5.67,
            ),
            Case(
                description="integer",
                val=5,
                args=[],
                kwargs={},
                expect=5,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, 2],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[2],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined argument",
                val=5.666,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=6,
            ),
        ]

        self._test(Round, test_cases)
        self._test_newstyle_filter(round_, test_cases)

    def test_times(self):
        """Test times filter function."""

        test_cases = [
            Case(
                description="int times int",
                val=5,
                args=[2],
                kwargs={},
                expect=10,
            ),
            Case(
                description="int times float",
                val=5,
                args=[2.1],
                kwargs={},
                expect=10.5,
            ),
            Case(
                description="int times float",
                val=5,
                args=[2.1],
                kwargs={},
                expect=10.5,
            ),
            Case(
                description="float times float",
                val=5.0,
                args=[2.1],
                kwargs={},
                expect=10.5,
            ),
            Case(
                description="string times string",
                val="5.0",
                args=["2.1"],
                kwargs={},
                expect=10.5,
            ),
            Case(
                description="negative multiplication",
                val=-5,
                args=[2],
                kwargs={},
                expect=-10,
            ),
            Case(
                description="missing arg",
                val=5,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, 2],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[2],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined argument",
                val=5,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=0,
            ),
        ]

        self._test(Times, test_cases)
        self._test_newstyle_filter(times, test_cases)

    def test_modulo(self):
        """Test modulo filter function."""

        test_cases = [
            Case(
                description="integer value and integer arg",
                val=10,
                args=[2],
                kwargs={},
                expect=0,
            ),
            Case(
                description="integer value and float arg",
                val=10,
                args=[2.0],
                kwargs={},
                expect=0.0,
            ),
            Case(
                description="float value and float arg",
                val=10.1,
                args=[7.0],
                kwargs={},
                expect=3.1,
            ),
            Case(
                description="string value and argument",
                val="10",
                args=["2.0"],
                kwargs={},
                expect=0.0,
            ),
            Case(
                description="string not a number",
                val="foo",
                args=["2.0"],
                kwargs={},
                expect=0,
            ),
            Case(
                description="arg string not a number",
                val="10",
                args=["foo"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="too many args",
                val=5,
                args=[1, "5"],
                kwargs={},
                expect=FilterArgumentError,
            ),
            Case(
                description="not a string, int or float",
                val=object(),
                args=[1],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined left value",
                val=self.env.undefined("test"),
                args=[2],
                kwargs={},
                expect=0,
            ),
            Case(
                description="undefined argument",
                val=5,
                args=[self.env.undefined("test")],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self._test(Modulo, test_cases)
        self._test_newstyle_filter(modulo, test_cases)
