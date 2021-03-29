"""Bad context test cases."""

from unittest import TestCase

from typing import NamedTuple
from typing import Type

from liquid.context import builtin
from liquid.environment import Environment

from liquid.exceptions import LiquidTypeError
from liquid.exceptions import lookup_warning

from liquid.mode import Mode


class Case(NamedTuple):
    """Table driven test case helper."""

    description: str
    template: str
    expect_exception: Type[Exception]
    expect_msg: str
    expect_render: str = ""


class BadContextTemplateTestCase(TestCase):
    """Bad context test case."""

    def _test(self, test_cases, mode=Mode.STRICT):
        """Helper method for running lists of `Case`s"""
        env = Environment()
        env.mode = mode

        global_context = {"arr": [], "hash": {}}

        for case in test_cases:
            with self.subTest(msg=case.description):
                if mode == Mode.STRICT:
                    with self.assertRaises(case.expect_exception) as raised:
                        template = env.from_string(
                            case.template, globals=global_context
                        )
                        result = template.render()

                    self.assertEqual(str(raised.exception), case.expect_msg)

                elif mode == Mode.WARN:
                    with self.assertWarns(lookup_warning(case.expect_exception)):
                        template = env.from_string(
                            case.template, globals=global_context
                        )
                        result = template.render()

                elif mode == Mode.LAX:
                    template = env.from_string(case.template, globals=global_context)
                    result = template.render()
                    self.assertEqual(result, case.expect_render)

    def test_bad_context(self):
        """Test that we handle render time errors due to incorrect context."""
        test_cases = [
            Case(
                description="array less than hash",
                template="{% if arr < hash %}foo{% endif %}",
                expect_exception=LiquidTypeError,
                expect_msg=r"invalid operator for types '[] < {}', on line 1",
            ),
        ]

        self._test(test_cases, mode=Mode.STRICT)
        self._test(test_cases, mode=Mode.WARN)
        self._test(test_cases, mode=Mode.LAX)


class BuiltinDynamicScopeTestCase(TestCase):
    """Built-in dynamic scope test case."""

    def test_builtin_contains_now(self):
        """Test that `now` is in the builtin scope."""
        self.assertTrue("now" in builtin)

    def test_builtin_contains_today(self):
        """Test that `today` is in the builtin scope."""
        self.assertTrue("today" in builtin)

    def test_builtin_not_contains(self):
        """Test that garbage is not in the builtin scope."""
        self.assertFalse("foo" in builtin)

    def test_builtin_length(self):
        """Test that builtin has a length."""
        self.assertEqual(len(builtin), 2)

    def test_builtin_iter(self):
        """Test that builtin has a length."""
        self.assertEqual(list(builtin), ["now", "today"])
