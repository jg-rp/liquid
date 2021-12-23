"""Expression caching test cases."""
# pylint: disable=missing-class-docstring

from unittest import TestCase

from liquid import Environment
from liquid import Template

from liquid.builtin.tags.if_tag import IfNode


class ExpressionCacheTestCase(TestCase):
    def test_env_with_no_expression_caching(self):
        """Test that there is no expression caching by default."""
        env = Environment(expression_cache_size=0)
        template = env.from_string(
            "{% if x == 1 %}{% endif %}{% if x == 1 %}{% endif %}"
        )
        nodes = template.tree.statements
        self.assertEqual(len(nodes), 2)

        node1, node2 = nodes
        assert isinstance(node1, IfNode)
        assert isinstance(node2, IfNode)

        self.assertNotEqual(id(node1.condition), id(node2.condition))

    def test_env_with_expression_caching(self):
        """Test that there is no expression caching by default."""
        env = Environment(expression_cache_size=1)
        template = env.from_string(
            "{% if x == 1 %}{% endif %}{% if x == 1 %}{% endif %}"
        )
        nodes = template.tree.statements
        self.assertEqual(len(nodes), 2)

        node1, node2 = nodes
        assert isinstance(node1, IfNode)
        assert isinstance(node2, IfNode)

        self.assertEqual(id(node1.condition), id(node2.condition))

    def test_template_with_no_expression_caching(self):
        """Test that there is no expression caching by default."""
        template = Template(
            "{% if x == 1 %}{% endif %}{% if x == 1 %}{% endif %}",
            expression_cache_size=0,
        )

        nodes = template.tree.statements
        self.assertEqual(len(nodes), 2)

        node1, node2 = nodes
        assert isinstance(node1, IfNode)
        assert isinstance(node2, IfNode)

        self.assertNotEqual(id(node1.condition), id(node2.condition))

    def test_template_with_expression_caching(self):
        """Test that there is no expression caching by default."""
        template = Template(
            "{% if x == 1 %}{% endif %}{% if x == 1 %}{% endif %}",
            expression_cache_size=1,
        )

        nodes = template.tree.statements
        self.assertEqual(len(nodes), 2)

        node1, node2 = nodes
        assert isinstance(node1, IfNode)
        assert isinstance(node2, IfNode)

        self.assertEqual(id(node1.condition), id(node2.condition))
