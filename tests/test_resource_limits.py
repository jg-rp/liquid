"""Resource limit test cases."""
# pylint: disable=missing-class-docstring
import platform
import unittest

from liquid import DictLoader
from liquid import Environment

from liquid.exceptions import ContextDepthError
from liquid.exceptions import LoopIterationLimitError
from liquid.exceptions import LocalNamespaceLimitError
from liquid.exceptions import OutputStreamLimitError


class ContextDepthLimitTestCase(unittest.TestCase):
    """Render context depth limit test cases."""

    def test_recursive_render(self):
        """Test that we get an exception when rendering recursively."""
        env = Environment(
            loader=DictLoader(
                {
                    "foo": "{% render 'bar' %}",
                    "bar": "{% render 'foo' %}",
                }
            )
        )
        template = env.from_string("{% render 'foo' %}")
        with self.assertRaises(ContextDepthError):
            template.render()

    def test_recursive_include(self):
        """Test that we get an exception when including recursively."""
        env = Environment(
            loader=DictLoader(
                {
                    "foo": "{% include 'bar' %}",
                    "bar": "{% include 'foo' %}",
                }
            )
        )
        template = env.from_string("{% include 'foo' %}")
        with self.assertRaises(ContextDepthError):
            template.render()

    def test_set_context_depth_limit_render(self):
        """Test that we can set the context depth limit."""
        env = Environment(
            loader=DictLoader(
                {
                    "foo": "{% render 'bar' %}",
                    "bar": "{% render 'baz' %}",
                    "baz": "Hello",
                }
            )
        )
        template = env.from_string("{% render 'foo' %}")
        result = template.render()
        self.assertEqual(result, "Hello")

        env.context_depth_limit = 3
        template = env.from_string("{% render 'foo' %}")
        with self.assertRaises(ContextDepthError):
            template.render()

    def test_set_context_depth_limit_include(self):
        """Test that we can set the context depth limit."""
        env = Environment(
            loader=DictLoader(
                {
                    "foo": "{% include 'bar' %}",
                    "bar": "{% include 'baz' %}",
                    "baz": "Hello",
                }
            )
        )
        template = env.from_string("{% include 'foo' %}")
        result = template.render()
        self.assertEqual(result, "Hello")

        env.context_depth_limit = 3
        template = env.from_string("{% include 'foo' %}")
        with self.assertRaises(ContextDepthError):
            template.render()


class LoopIterationLimitTestCase(unittest.TestCase):
    """Loop iteration limit test cases."""

    def test_default_loop_iteration_limit(self):
        """Test (effectively) that the default loop limit is None."""
        env = Environment()
        template = env.from_string(
            "{% for i in (1..100) %}"
            "{% for j in (1..100) %}"
            "x"
            "{% endfor %}"
            "{% endfor %}"
        )

        template.render()

    def test_set_loop_iteration_limit(self):
        """Test that we can set the loop iteration limit."""

        class MockEnv(Environment):
            loop_iteration_limit = 10000

        env = MockEnv()
        env.from_string(
            "{% for i in (1..100) %}"
            "{% for j in (1..100) %}"
            "{{ i }},{{ j }}"
            "{% endfor %}"
            "{% endfor %}"
        ).render()

        template = env.from_string(
            "{% for i in (1..101) %}"
            "{% for j in (1..100) %}"
            "{{ i }},{{ j }}"
            "{% endfor %}"
            "{% endfor %}"
        )

        with self.assertRaises(LoopIterationLimitError):
            template.render()

    def test_render_carries_loop_count(self):
        """Test that a `render`ed template carries the loop count from its parent."""

        class MockEnv(Environment):
            loop_iteration_limit = 3000

        env = MockEnv(
            loader=DictLoader(
                {
                    "foo": (
                        "{% for i in (1..50) %}"
                        "{% for j in (1..50) %}"
                        "{{ i }},{{ j }}"
                        "{% endfor %}"
                        "{% endfor %}"
                    ),
                }
            )
        )
        template = env.from_string(
            "{% for i in (1..10) %}{% render 'foo' %}{% endfor %}"
        )

        with self.assertRaises(LoopIterationLimitError):
            template.render()

    def test_nested_renders_carry_loop_count(self):
        """Test that multiple, nested renders carry the loop count."""

        class MockEnv(Environment):
            loop_iteration_limit = 3000

        env = MockEnv(
            loader=DictLoader(
                {
                    "foo": (
                        "{% for i in (1..50) %}" "{% render 'bar' %}" "{% endfor %}"
                    ),
                    "bar": ("{% for j in (1..50) %}" "{{ j }}" "{% endfor %}"),
                }
            )
        )
        template = env.from_string(
            "{% for i in (1..10) %}{% render 'foo' %}{% endfor %}"
        )

        with self.assertRaises(LoopIterationLimitError):
            template.render()

    def test_include_contributes_to_count(self):
        """Test that `included`ed templates contribute to the loop count."""

        class MockEnv(Environment):
            loop_iteration_limit = 3000

        env = MockEnv(
            loader=DictLoader(
                {
                    "foo": (
                        "{% for i in (1..50) %}"
                        "{% for j in (1..50) %}"
                        "{{ i }},{{ j }}"
                        "{% endfor %}"
                        "{% endfor %}"
                    ),
                }
            )
        )
        template = env.from_string(
            "{% for i in (1..10) %}{% include 'foo' %}{% endfor %}"
        )

        with self.assertRaises(LoopIterationLimitError):
            template.render()

    def test_tablerow_contributes_to_count(self):
        """Test that the tablerow tag contributes to the loop count."""

        class MockEnv(Environment):
            loop_iteration_limit = 99

        env = MockEnv()
        template = env.from_string(
            "{% for i in (1..10) %}"
            "{% tablerow i in (1..10) cols:2 %}"
            "{{ i }}"
            "{% endtablerow %}"
            "{% endfor %}"
        )

        with self.assertRaises(LoopIterationLimitError):
            template.render()


class LocalNamespaceLimitTestCase(unittest.TestCase):
    """Render context local namespace length limit test cases."""

    @unittest.skipIf(platform.python_implementation() == "PyPy", "no sys.getsizeof")
    def test_set_local_namespace_limit(self):
        """Test that we can set the local namespace limit."""

        class MockEnv(Environment):
            local_namespace_limit = 140

        env = MockEnv()
        env.from_string(
            "{% assign a = 1 %}"
            "{% assign b = 2 %}"
            "{% assign c = 3 %}"
            "{% assign d = 4 %}"
            "{% assign e = 5 %}"
        ).render()

        template = env.from_string(
            "{% assign a = 1 %}"
            "{% assign b = 2 %}"
            "{% assign c = 3 %}"
            "{% assign d = 4 %}"
            "{% assign e = 5 %}"
            "{% assign f = 6 %}"
        )

        with self.assertRaises(LocalNamespaceLimitError):
            template.render()

    def test_copied_context_carries_parent_length(self):
        """Test that copied render context object cary the length of their parent
        context's local namespace."""

        class MockEnv(Environment):
            local_namespace_limit = 5

        env = MockEnv(
            loader=DictLoader(
                {
                    "foo": (
                        "{% assign a = 1 %}"
                        "{% assign b = 2 %}"
                        "{% assign c = 3 %}"
                        "{% assign d = 4 %}"
                        "{% assign e = 5 %}"
                        "{% assign e = 'five' %}"
                    )
                }
            )
        )

        template = env.from_string("{% assign f = 6 %}{% render 'foo' %}")

        with self.assertRaises(LocalNamespaceLimitError):
            template.render()

    def test_sizeof_local_namespace_with_unhashable_values(self):
        """Test that we can calculate the size of a local namespace when it contains
        unhashable objects."""

        class MockEnv(Environment):
            local_namespace_limit = 200

        env = MockEnv()
        env.from_string("{% assign foo = bar %}").render(bar=[1, 2, 3, 4])

        env.from_string(
            '{% assign beatles = "John, Paul, George, Ringo" | split: ", " %}'
        ).render()


class OutputStreamLimitTestCase(unittest.TestCase):
    """Template output stream limit test cases."""

    def test_set_output_stream_limit(self):
        """Test that we can set an output stream limit."""

        class MockEnv(Environment):
            output_stream_limit = 5

        env = MockEnv()
        env.from_string(
            "{% if false %}some literal that is longer then the limit{% endif %}"
            "hello"
        ).render()

        template = env.from_string(
            "{% if true %}some literal that is longer then the limit{% endif %}hello"
        )

        with self.assertRaises(OutputStreamLimitError):
            template.render()
