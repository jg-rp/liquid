"""Test that the "compatible" render context is more compatible with Ruby Liquid
than the default render context."""
import asyncio
from unittest import TestCase

from liquid import Environment
from liquid import FutureContext
from liquid import is_undefined

from liquid.future import Environment as RubyEnvironment


class CompatContextTestCase(TestCase):
    """Test cases for the "compatible" render context."""

    def test_string_indices(self) -> None:
        """Test that we can not access characters in a string by index."""
        env = Environment()
        context = FutureContext(env, globals={"some": "thing"})
        self.assertTrue(is_undefined(context.get(["some", 1])))

        with self.subTest(msg="async"):
            self.assertTrue(is_undefined(asyncio.run(context.get_async(["some", 1]))))

    def test_special_properties(self) -> None:
        """Test special `size`, `first` and last properties."""
        env = Environment()
        context = FutureContext(env, globals={"some": "thing"})
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

    def test_cycle_without_name(self) -> None:
        """Test unnamed cycles."""
        env = Environment()
        context = FutureContext(env)
        self.assertEqual(context.cycle("", [1, 2, 3]), 1)
        self.assertEqual(context.cycle("", ["x", "y", "z"]), "x")
        self.assertEqual(context.cycle("", [1, 2, 3]), 2)

    def test_cycle_wraps(self) -> None:
        """Test that we wrap around."""
        env = Environment()
        context = FutureContext(env)
        self.assertEqual(context.cycle("", ["some", "other"]), "some")
        self.assertEqual(context.cycle("", ["some", "other"]), "other")
        self.assertEqual(context.cycle("", ["some", "other"]), "some")

    def test_named_cycle_groups(self) -> None:
        """Test that named cycles ignore arguments."""
        env = Environment()
        context = FutureContext(env)
        self.assertEqual(context.cycle("a", [1, 2, 3]), 1)
        self.assertEqual(context.cycle("a", ["x", "y", "z"]), "y")
        self.assertEqual(context.cycle("a", [1, 2, 3]), 3)

    def test_named_cycles_with_shrinking_lengths(self) -> None:
        """Test that we handle cycles with a shrinking number of arguments."""
        env = Environment()
        context = FutureContext(env)
        self.assertEqual(context.cycle("a", [1, 2, 3]), 1)
        self.assertEqual(context.cycle("a", ["x", "y"]), "y")
        self.assertEqual(context.cycle("a", ["x", "y"]), "x")

    def test_named_cycles_with_growing_lengths(self) -> None:
        """Test that we handle cycles with a growing number of arguments."""
        env = Environment()
        context = FutureContext(env)
        self.assertEqual(context.cycle("a", [1, 2]), 1)
        self.assertEqual(context.cycle("a", ["x", "y", "z"]), "y")
        self.assertEqual(context.cycle("a", ["x", "y", "z"]), "z")


class CompatTemplateTestCase(TestCase):
    """Test cases for the "compatible" versions of BoundTemplate and Environment."""

    def test_compat_capture_context(self) -> None:
        """Test that the "capture" version of the compatible context does indeed
        capture variables."""
        env = RubyEnvironment()
        template = env.from_string("{% assign x = 'hello' %}{{ x[1] }}")
        self.assertEqual(template.render(), "")

        template = env.from_string("{% assign x = 'hello' %}{{ x }}")
        self.assertEqual(template.render(), "hello")
        analysis = template.analyze_with_context()

        self.assertEqual(analysis.all_variables, {"x": 1})
        self.assertEqual(analysis.local_variables, {"x": 1})
