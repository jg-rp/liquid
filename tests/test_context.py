"""Bad context test cases."""

from unittest import TestCase
from typing import NamedTuple, Type

from liquid.environment import Environment
from liquid.mode import Mode
from liquid.exceptions import LiquidTypeError, lookup_warning


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
        """Test that we gracefully handle render time errors due to incorrect context."""
        test_cases = [
            Case(
                description="loop expression variable does not exist",
                template="{% for tag in product.tags %}{tag}{% endfor %}",
                expect_exception=LiquidTypeError,
                expect_msg="expected array or hash at 'product.tags', found 'None', on line 1",
            ),
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
