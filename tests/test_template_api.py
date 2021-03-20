"""Test case for the `Template` API."""

import unittest

from liquid import Template
from liquid import Environment
from liquid import Mode


class TemplateAPITestCase(unittest.TestCase):
    """Test case for the `Template` API."""

    def test_implicit_environment(self):
        """Test that an Environment is created automatically."""
        template = Template(r"Hello, {{ you }}")
        self.assertIsNotNone(template.env)

    def test_environment_cache(self):
        """Test that we reuse Environments."""
        template = Template(r"Hello, {{ you }}!")
        another = Template(r"Goodbye, {{ you }}.")

        self.assertEqual(template.env, another.env)

        lax = Template("something", tolerance=Mode.LAX)
        self.assertNotEqual(lax.env, template.env)

    def test_implicit_explicit(self):
        """Test that an implicit environment renders the same as an explicit one."""
        env = Environment()

        source = r"Hello, {{ you }}"
        context = {"you": "there"}

        some = env.from_string(source)
        other = Template(source)

        self.assertEqual(some.render(**context), other.render(**context))
