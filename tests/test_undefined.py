from unittest import TestCase
from typing import NamedTuple

from liquid import Environment
from liquid import StrictUndefined

from liquid.exceptions import UndefinedError


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
        ]

        env = Environment(undefined=StrictUndefined)

        for case in tests:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template)

                with self.assertRaises(UndefinedError) as raised:
                    template.render()

                self.assertEqual(case.expect, str(raised.exception))
