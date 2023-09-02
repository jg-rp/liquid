"""Test cases for controlling automatic suppression of empty blocks."""
import unittest

from liquid import Environment


class DefaultWhitespaceSuppressionTestCase(unittest.TestCase):
    """Test cases for controlling automatic suppression of empty blocks."""

    def setUp(self) -> None:
        self.env = Environment()

    def test_suppress_empty_if_block(self) -> None:
        """Test that we suppress empty if blocks by default."""
        template = self.env.from_string("!{% if true %}\n \t\r{% endif %}!")
        self.assertEqual(template.render(), "!!")

    def test_suppress_empty_else_block(self) -> None:
        """Test that we suppress empty else blocks by default."""
        template = self.env.from_string(
            "!{% if false %}foo{% else %}\n \r\t{% endif %}!"
        )
        self.assertEqual(template.render(), "!!")

    def test_suppress_empty_unless_block(self) -> None:
        """Test that we suppress empty unless blocks by default."""
        template = self.env.from_string("!{% unless false %}\n \t\r{% endunless %}!")
        self.assertEqual(template.render(), "!!")

    def test_suppress_empty_case_block(self) -> None:
        """Test that we suppress empty case blocks by default."""
        template = self.env.from_string(
            "!{% assign x = 1 %}{% case x %}{% when 1 %}\n \t\r{% endcase %}!"
        )
        self.assertEqual(template.render(), "!!")

    def test_suppress_empty_for_block(self) -> None:
        """Test that we suppress empty for blocks by default."""
        template = self.env.from_string("!{% for x in (1..3) %}\n \t\r{% endfor %}!")
        self.assertEqual(template.render(), "!!")


class MyEnvironment(Environment):
    render_whitespace_only_blocks = True


class ControlWhitespaceSuppressionTestCase(unittest.TestCase):
    """Test cases for controlling automatic suppression of empty blocks."""

    def setUp(self) -> None:
        self.env = MyEnvironment()

    def test_output_empty_if_block(self) -> None:
        """Test that we can output empty if blocks."""
        template = self.env.from_string("!{% if true %}\n \t\r{% endif %}!")
        self.assertEqual(template.render(), "!\n \t\r!")

    def test_output_empty_else_block(self) -> None:
        """Test that we can output empty else blocks."""
        template = self.env.from_string(
            "!{% if false %}foo{% else %}\n \r\t{% endif %}!"
        )
        self.assertEqual(template.render(), "!\n \r\t!")

    def test_output_empty_unless_block(self) -> None:
        """Test that we can output empty unless blocks."""
        template = self.env.from_string("!{% unless false %}\n \t\r{% endunless %}!")
        self.assertEqual(template.render(), "!\n \t\r!")

    def test_output_empty_case_block(self) -> None:
        """Test that we can output empty case blocks."""
        template = self.env.from_string(
            "!{% assign x = 1 %}{% case x %}{% when 1 %}\n \t\r{% endcase %}!"
        )
        self.assertEqual(template.render(), "!\n \t\r!")

    def test_output_empty_for_block(self) -> None:
        """Test that we can output empty for blocks."""
        template = self.env.from_string("!{% for x in (1..3) %}\n{% endfor %}!")
        self.assertEqual(template.render(), "!\n\n\n!")
