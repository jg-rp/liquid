"""Bad context test cases."""

from unittest import TestCase

from typing import NamedTuple
from typing import Type

from liquid.context import builtin
from liquid.context import get_item
from liquid.context import UNDEFINED
from liquid.context import ReadOnlyChainMap
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


class ReadOnlyChainMapTestCase(TestCase):
    """Read only chain map test case."""

    def test_get(self):
        """Test that we can get items from a chain map."""
        test_cases = [
            {
                "description": "earlier maps take priority",
                "maps": ({"foo": 1}, {"foo": 2}),
                "expect": 1,
            },
            {
                "description": "fall back top later maps",
                "maps": ({"bar": 1}, {"foo": 2}),
                "expect": 2,
            },
            {
                "description": "default to None",
                "maps": ({"bar": 1}, {"bar": 2}),
                "expect": None,
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                chain_map = ReadOnlyChainMap(*case["maps"])
                self.assertEqual(chain_map.get("foo"), case["expect"])

    def test_iter(self):
        """Test that we can iterate a chain map."""
        chain_map = ReadOnlyChainMap({"foo": 1}, {"bar": 2}, {"foo": 3})
        self.assertEqual(list(chain_map), ["foo", "bar", "foo"])


class ChainedItemGetterTestCase(TestCase):
    """Chained item getter test case."""

    def test_get_item(self):
        """Test that we can get nested items."""
        test_cases = [
            {
                "description": "single string key",
                "obj": {"foo": 1},
                "key": ["foo"],
                "expect": 1,
            },
            {
                "description": "chained string key",
                "obj": {"foo": {"bar": 2}},
                "key": ["foo", "bar"],
                "expect": 2,
            },
            {
                "description": "single int key",
                "obj": ["foo", "bar"],
                "key": [0],
                "expect": "foo",
            },
            {
                "description": "chained string and int key",
                "obj": {"foo": [1, 2]},
                "key": ["foo", 1],
                "expect": 2,
            },
            {
                "description": "default to undefined",
                "obj": {"foo": 1},
                "key": ["no", "such", "thing"],
                "expect": UNDEFINED,
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                self.assertEqual(get_item(case["obj"], *case["key"]), case["expect"])


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
