# pylint: disable=missing-class-docstring missing-module-docstring
import unittest

from liquid import Template
from liquid import Mode

from liquid.exceptions import LiquidValueError
from liquid.limits import MAX_STR_INT


class StrToIntTestCase(unittest.TestCase):
    def test_parse_long_integer_literal(self):
        """Test that we honour the maximum str to int length on integer literals."""
        Template("".join(["{{", "1" * MAX_STR_INT, " }}"]))

        with self.assertRaises(LiquidValueError):
            Template("".join(["{{", "1" * (MAX_STR_INT + 1), " }}"]))

    def test_math_filter_long_string_literal(self):
        """Test that we honour the maximum str to int length on string literals."""
        template = Template("".join(["{{ '", "1" * MAX_STR_INT, "' | abs }}"]))
        self.assertEqual(template.render(), "1" * MAX_STR_INT)

        template = Template(
            "".join(["{{ '", "1" * (MAX_STR_INT + 1), "' | abs }}"]),
            tolerance=Mode.STRICT,
        )

        with self.assertRaises(LiquidValueError):
            self.assertEqual(template.render(), "1" * (MAX_STR_INT + 1))
