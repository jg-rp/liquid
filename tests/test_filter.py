"""Test filter decorators and helpers."""
# pylint: disable=missing-class-docstring
from unittest import TestCase

from liquid import Environment
from liquid import Context

from liquid.filter import liquid_filter
from liquid.filter import with_context
from liquid.filter import num_arg
from liquid.filter import int_arg

from liquid.exceptions import FilterArgumentError


@liquid_filter
@with_context
def some_filter(val, arg, *, context: Context) -> str:
    """Contrived filter function making use of `with_context`."""
    return val + context.resolve(arg)


class WithContextTestCase(TestCase):
    def test_filter_with_context(self):
        """Test that we can pass the active context to a filter function."""
        env = Environment(strict_filters=True)
        env.add_filter("some", some_filter)

        template = env.from_string(r"{{ 'Hello, ' | some: 'you' }}")
        result = template.render(you="World")

        self.assertEqual(result, "Hello, World")


class IntArgTestCase(TestCase):
    def test_int_arg_fail(self):
        """Test that a suitable exception is raised if we can't cast to an int."""
        with self.assertRaises(FilterArgumentError):
            int_arg("foo")

    def test_int_arg_with_default(self):
        """Test that a default is returned if we can't cast to an int."""
        self.assertEqual(int_arg("foo", 99), 99)


class NumArgTestCase(TestCase):
    def test_num_arg_fail_string(self):
        """Test that a suitable exception is raised if we can't cast to a number."""
        with self.assertRaises(FilterArgumentError):
            num_arg("foo")

    def test_num_arg_with_default(self):
        """Test that a default is returned if we can't cast to a number."""
        self.assertEqual(num_arg("foo", 99.8), 99.8)

    def test_num_arg_no_default(self):
        """Test that an exception is raised if a default is not given."""
        with self.assertRaises(FilterArgumentError):
            num_arg(object())
