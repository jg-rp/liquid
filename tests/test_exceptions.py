"""Liquid exception test cases."""
# pylint: disable=missing-class-docstring

from pathlib import Path
from unittest import TestCase

from liquid import Environment
from liquid import Mode

from liquid.exceptions import Error
from liquid.exceptions import LiquidSyntaxError


class EnvironmentErrorTestCase(TestCase):
    def test_exception_class_is_raised(self):
        """Test env.error handles exception classes."""
        env = Environment(tolerance=Mode.STRICT, strict_filters=True)

        with self.assertRaises(Error):
            env.error(LiquidSyntaxError, msg=":(")


class LiquidErrorTestCase(TestCase):
    def test_base_error_message(self):
        """Test that the base error can include a message."""
        try:
            raise Error("Oh no!", "extra info")
        except Error as err:
            self.assertEqual(err.message, "Oh no!")

    def test_base_error_no_message(self):
        """Test that the base error can not include a message."""
        try:
            raise Error()
        except Error as err:
            self.assertEqual(err.message, None)

    def test_base_error_include_filename(self):
        """Test that the base error can include a filename."""
        try:
            raise Error("Oh no!", linenum=1, filename="foo.liquid")
        except Error as err:
            self.assertEqual(str(err), "Oh no!, on line 1 of foo.liquid")


class LiquidSyntaxErrorTestCase(TestCase):
    def test_template_name_from_string(self):
        """Test that a syntax error can include a template name as a string."""
        try:
            raise LiquidSyntaxError("Oh no!", filename="foo.liquid")
        except LiquidSyntaxError as err:
            self.assertEqual(err.name, "foo.liquid")

    def test_template_name_from_path(self):
        """Test that a syntax error can include a template name as a path."""
        try:
            raise LiquidSyntaxError("Oh no!", filename=Path("/templates/foo.liquid"))
        except LiquidSyntaxError as err:
            self.assertEqual(err.name, "/templates/foo.liquid")

    def test_no_template_name(self):
        """Test that a syntax error can not include template name."""
        try:
            raise LiquidSyntaxError("Oh no!")
        except LiquidSyntaxError as err:
            self.assertEqual(err.name, "")
