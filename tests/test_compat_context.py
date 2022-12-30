"""Test that the "compatible" render context is more compatible with Ruby Liquid
than the default render context."""
import asyncio
from unittest import TestCase

from liquid import Environment
from liquid import CompatContext
from liquid import is_undefined


class CompatContextTestCase(TestCase):
    """Test cases for the "compatible" render context."""

    def test_string_indices(self) -> None:
        """Test that we can not access characters in a string by index."""
        env = Environment()
        context = CompatContext(env, globals={"some": "thing"})
        self.assertTrue(is_undefined(context.get(["some", 1])))

        with self.subTest(msg="async"):
            self.assertTrue(is_undefined(asyncio.run(context.get_async(["some", 1]))))

    def test_special_properties(self) -> None:
        """Test special `size`, `first` and last properties."""
        env = Environment()
        context = CompatContext(env, globals={"some": "thing"})
        self.assertEqual(context.get(["some", "size"]), 5)
        self.assertTrue(is_undefined(context.get(["some", "first"])))
        self.assertTrue(is_undefined(context.get(["some", "last"])))

        with self.subTest(msg="async"):
            self.assertEqual(asyncio.run(context.get_async(["some", "size"])), 5)
            self.assertTrue(
                is_undefined(asyncio.run(context.get_async(["some", "first"])))
            )
            self.assertTrue(
                is_undefined(asyncio.run(context.get_async(["some", "last"])))
            )

    # def test_named_cycle_groups(self) -> None:
    #     """Test that named cycles ignore arguments."""
    #     source = (
    #         "{% cycle a: 1, 2, 3 %}\n"
    #         '{% cycle a: "x", "y", "z" %}\n'
    #         "{% cycle a: 1, 2, 3 %}"
    #     )

    #     env = Environment()
    #     context = CompatContext(env)

    #     self.assertEqual(context.cycle("a", [1, 2, 3]), 1)
    #     self.assertEqual(context.cycle("a", ["x", "y", "z"]), "y")
    #     self.assertEqual(context.cycle("a", [1, 2, 3]), 3)
