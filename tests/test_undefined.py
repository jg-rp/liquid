from unittest import TestCase
from typing import NamedTuple

from liquid import Environment
from liquid import Undefined
from liquid import DebugUndefined
from liquid import StrictUndefined

from liquid.exceptions import UndefinedError
from liquid.exceptions import NoSuchFilterFunc


class Case(NamedTuple):
    """Table driven test case helper."""

    description: str
    template: str
    expect: str


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
                expect="0",
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
        ]

        env = Environment(undefined=StrictUndefined)

        for case in tests:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)

                with self.assertRaises(UndefinedError) as raised:
                    template.render()

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
