"""Test built-in "undefined" types."""
import asyncio

from dataclasses import dataclass
from dataclasses import field

from unittest import TestCase
from typing import Dict

from liquid import Environment
from liquid import Undefined
from liquid import DebugUndefined
from liquid import StrictUndefined
from liquid import StrictDefaultUndefined

from liquid.template import BoundTemplate

from liquid.exceptions import UndefinedError
from liquid.exceptions import NoSuchFilterFunc


@dataclass
class Case:
    """Table driven test case helper."""

    description: str
    template: str
    expect: str
    context: Dict[str, object] = field(default_factory=dict)


class TestUndefined(TestCase):
    """Undefined test case."""

    def test_default_undefined(self):
        """Test that the default undefined type is quiet and forgiving."""
        tests = [
            Case(
                description="undefined in output statement",
                template=r"{{ nosuchthing }}",
                expect="",
            ),
            Case(
                description="undefined in loop expression",
                template=r"{% for tag in nosuchthing %}{tag}{% endfor %}",
                expect="",
            ),
            Case(
                description="index undefined",
                template=r"{{ nosuchthing[0] }}",
                expect="",
            ),
            Case(
                description="test undefined for truthy-ness",
                template=r"{% if nosuchthing %}hello{% endif %}",
                expect="",
            ),
            Case(
                description="compare undefined",
                template=r"{% if nosuchthing == 'hello' %}hello{% endif %}",
                expect="",
            ),
            Case(
                description="undefined equals undefined",
                template=r"{% if nosuchthing == noway %}hello{% endif %}",
                expect="hello",
            ),
            Case(
                description="undefined contains string",
                template=r"{% if nosuchthing contains 'hello' %}hello{% endif %}",
                expect="",
            ),
            Case(
                description="access `last` from undefined",
                template=r"{{ nosuchthing.last }}",
                expect="",
            ),
            Case(
                description="access `size` from undefined",
                template=r"{{ nosuchthing.size }}",
                expect="",
            ),
            Case(
                description="filtered undefined",
                template=r"hello {{ nosuchthing | last }} there",
                expect="hello  there",
            ),
            Case(
                description="math filter undefined",
                template=r"hello {{ nosuchthing | abs }} there",
                expect="hello 0 there",
            ),
            Case(
                description="undefined filter argument",
                template=r"hello {{ '1,2,3' | split: nosuchthing }} there",
                expect="hello 1,2,3 there",
            ),
            Case(
                description="filter undefined through date",
                template=r"hello {{ nosuchthing | date: '%b %d, %y' }} there",
                expect="hello  there",
            ),
            Case(
                description="array index out or range",
                template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[100] }}",
                expect="",
            ),
            Case(
                description="negative array index out or range",
                template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[-100] }}",
                expect="",
            ),
        ]

        env = Environment()

        for case in tests:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)
                result = template.render()
                self.assertEqual(case.expect, result)

    def test_strict_undefined(self):
        """Test that the strict undefined type raises an exception for everything."""
        tests = [
            Case(
                description="undefined in output statement",
                template=r"{{ nosuchthing }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined in loop expression",
                template=r"{% for tag in nosuchthing %}{tag}{% endfor %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="index undefined",
                template=r"{{ nosuchthing[0] }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="test undefined for truthy-ness",
                template=r"{% if nosuchthing %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="compare undefined",
                template=r"{% if nosuchthing == 'hello' %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined equals undefined",
                template=r"{% if nosuchthing == noway %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined contains string",
                template=r"{% if nosuchthing contains 'hello' %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="access `last` from undefined",
                template=r"{{ nosuchthing.last }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="access `size` from undefined",
                template=r"{{ nosuchthing.size }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="filtered undefined",
                template=r"hello {{ nosuchthing | last }} there",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined filter argument",
                template=r"hello {{ '1,2,3' | split: nosuchthing }} there",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="math filter undefined",
                template=r"hello {{ nosuchthing | abs }} there",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="array index out of range",
                template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[100] }}",
                expect="list index out of range: a[100], on line 1",
            ),
            Case(
                description="negative array index out of range",
                template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[-100] }}",
                expect="list index out of range: a[-100], on line 1",
            ),
            Case(
                description="key error",
                template=r"{{ obj['bar'] }}",
                expect="key error: 'bar', obj[bar], on line 1",
                context={"obj": {"foo": 1}},
            ),
            Case(
                description="default filter undefined",
                template=r"hello {{ nosuchthing | default: 'foo' }} there",
                expect="'nosuchthing' is undefined, on line 1",
            ),
        ]

        env = Environment(undefined=StrictUndefined)

        for case in tests:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)

                with self.assertRaises(UndefinedError) as raised:
                    template.render(**case.context)

                self.assertEqual(case.expect, str(raised.exception))

    def test_debug_undefined(self):
        """Test that the debugging undefined type prints debugging information."""
        env = Environment(undefined=DebugUndefined)
        template = env.from_string(r"{{ nosuchthing }}")
        result = template.render()
        self.assertEqual(result, "'nosuchthing' is undefined")

    def test_debug_undefined_hint(self):
        """Test that the debugging undefined type prints debugging hints."""
        env = Environment(undefined=DebugUndefined)
        undef = DebugUndefined(name="nosuchthing", hint="can't resolve identifier")
        template = env.from_string(r"{{ undef }}")
        result = template.render(undef=undef)
        self.assertEqual(result, "undefined: can't resolve identifier")

    def test_debug_undefined_object(self):
        """Test that the debugging undefined type prints related object information."""
        env = Environment(undefined=DebugUndefined)
        undef = DebugUndefined(name="nosuchthing", obj="foo")
        template = env.from_string(r"{{ nosuchthing }}")
        result = template.render(nosuchthing=undef)
        self.assertEqual(result, "str has no attribute 'nosuchthing'")

    def test_strict_default_undefined_with_default_filter(self):
        """Test that we can use an undefined type with the default filter."""
        env = Environment(undefined=StrictDefaultUndefined)
        template = env.from_string(r"{{ nosuchthing | default: 'hello' }}")
        result = template.render()
        self.assertEqual(result, "hello")

        template = env.from_string(r"{{ thing | default: 'hello' }}")
        result = template.render(thing="foo")
        self.assertEqual(result, "foo")

        template = env.from_string(r"{{ nosuchthing }}")
        with self.assertRaises(UndefinedError) as raised:
            template.render()

        self.assertEqual(str(raised.exception), "'nosuchthing' is undefined, on line 1")

    def test_filter_strict_default_undefined(self):
        """Test that the default undefined type raises an exception when used as a
        filter left value."""
        env = Environment(undefined=StrictDefaultUndefined)
        template = env.from_string(r"{{ nosuchthing | floor }}")
        with self.assertRaises(UndefinedError) as raised:
            template.render()

        self.assertEqual(str(raised.exception), "'nosuchthing' is undefined, on line 1")

    def test_isinstance_strict_default_filter(self):
        """Test that the default undefined type raises an exception when accessing
        __class__."""
        undef = StrictDefaultUndefined("nosuchthing")
        with self.assertRaises(UndefinedError):
            undef.__class__  # pylint: disable=pointless-statement

    def test_strict_default_undefined(self):
        """Test that the strict default undefined type raises an exception for
        everything other than the default filter."""
        tests = [
            Case(
                description="undefined in output statement",
                template=r"{{ nosuchthing }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined in loop expression",
                template=r"{% for tag in nosuchthing %}{tag}{% endfor %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="index undefined",
                template=r"{{ nosuchthing[0] }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="test undefined for truthy-ness",
                template=r"{% if nosuchthing %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="compare undefined",
                template=r"{% if nosuchthing == 'hello' %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined equals undefined",
                template=r"{% if nosuchthing == noway %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined contains string",
                template=r"{% if nosuchthing contains 'hello' %}hello{% endif %}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="access `last` from undefined",
                template=r"{{ nosuchthing.last }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="access `size` from undefined",
                template=r"{{ nosuchthing.size }}",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="filtered undefined",
                template=r"hello {{ nosuchthing | last }} there",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="undefined filter argument",
                template=r"hello {{ '1,2,3' | split: nosuchthing }} there",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="math filter undefined",
                template=r"hello {{ nosuchthing | abs }} there",
                expect="'nosuchthing' is undefined, on line 1",
            ),
            Case(
                description="array index out of range",
                template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[100] }}",
                expect="list index out of range: a[100], on line 1",
            ),
            Case(
                description="negative array index out of range",
                template=r"{% assign a = '1,2,3,4,5' | split: ',' %}{{ a[-100] }}",
                expect="list index out of range: a[-100], on line 1",
            ),
            Case(
                description="key error",
                template=r"{{ obj['bar'] }}",
                expect="key error: 'bar', obj[bar], on line 1",
                context={"obj": {"foo": 1}},
            ),
        ]

        env = Environment(undefined=StrictDefaultUndefined)

        for case in tests:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)

                with self.assertRaises(UndefinedError) as raised:
                    template.render(**case.context)

                self.assertEqual(case.expect, str(raised.exception))

    def test_lax_filter(self):
        """Test that undefined filters can be silently ignored."""
        tests = [
            Case(
                description="undefined filter",
                template=r"{{ 'hello' | nosuchthing }}",
                expect="hello",
            ),
            Case(
                description="undefined filter with argument",
                template=r"{{ 'hello' | nosuchthing: 'foo' }}",
                expect="hello",
            ),
            Case(
                description="undefined filter with more filters",
                template=r"{{ 'hello' | nosuchthing | upcase }}",
                expect="HELLO",
            ),
        ]

        env = Environment(strict_filters=False)

        for case in tests:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)
                result = template.render()
                self.assertEqual(case.expect, result)

    def test_strict_filters(self):
        """Test that undefined filters raise an exception in strict mode."""
        tests = [
            Case(
                description="undefined filter",
                template=r"{{ 'hello' | nosuchthing }}",
                expect="unknown filter 'nosuchthing', on line 1",
            ),
            Case(
                description="undefined filter with argument",
                template=r"{{ 'hello' | nosuchthing: 'foo' }}",
                expect="unknown filter 'nosuchthing', on line 1",
            ),
            Case(
                description="undefined filter with more filters",
                template=r"{{ 'hello' | nosuchthing | upcase }}",
                expect="unknown filter 'nosuchthing', on line 1",
            ),
        ]

        env = Environment(strict_filters=True)

        for case in tests:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)

                with self.assertRaises(NoSuchFilterFunc) as raised:
                    template.render()

                self.assertEqual(case.expect, str(raised.exception))

                # And render async
                async def coro(template: BoundTemplate):
                    return await template.render_async()

                with self.assertRaises(NoSuchFilterFunc) as raised:
                    asyncio.run(coro(template))

    def test_default_undefined_magic(self):
        """Test the default undefined type magic methods."""
        undefined = Undefined("test")
        self.assertFalse("foo" in undefined)
        self.assertTrue(int(undefined) == 0)

    def test_strict_undefined_magic(self):
        """Test the strict undefined type magic methods."""
        undefined = StrictUndefined("test")

        with self.assertRaises(UndefinedError):
            self.assertFalse("foo" in undefined)

        with self.assertRaises(UndefinedError):
            int(undefined)  # type: ignore

        with self.assertRaises(UndefinedError):
            list(undefined)

        with self.assertRaises(UndefinedError):
            len(undefined)  # type: ignore

        with self.assertRaises(UndefinedError):
            str(undefined)

        self.assertEqual(repr(undefined), "StrictUndefined(test)")

        with self.assertRaises(UndefinedError):
            bool(undefined)

        with self.assertRaises(UndefinedError):
            hash(undefined)

        with self.assertRaises(UndefinedError):
            reversed(undefined)  # type: ignore
