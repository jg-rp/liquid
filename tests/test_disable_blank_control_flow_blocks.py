"""Test cases for controlling automatic suppression of empty blocks."""

from liquid import Environment


class MyEnvironment(Environment):
    suppress_blank_control_flow_blocks = False


ENV = MyEnvironment()


def test_output_empty_if_block() -> None:
    """Test that we can output empty if blocks."""
    template = ENV.from_string("!{% if true %}\n \t\r{% endif %}!")
    assert template.render() == "!\n \t\r!"


def test_output_empty_else_block() -> None:
    """Test that we can output empty else blocks."""
    template = ENV.from_string("!{% if false %}foo{% else %}\n \r\t{% endif %}!")
    assert template.render() == "!\n \r\t!"


def test_output_empty_unless_block() -> None:
    """Test that we can output empty unless blocks."""
    template = ENV.from_string("!{% unless false %}\n \t\r{% endunless %}!")
    assert template.render() == "!\n \t\r!"


def test_output_empty_case_block() -> None:
    """Test that we can output empty case blocks."""
    template = ENV.from_string(
        "!{% assign x = 1 %}{% case x %}{% when 1 %}\n \t\r{% endcase %}!"
    )
    assert template.render() == "!\n \t\r!"


def test_output_empty_for_block() -> None:
    """Test that we can output empty for blocks."""
    template = ENV.from_string("!{% for x in (1..3) %}\n{% endfor %}!")
    assert template.render() == "!\n\n\n!"


def test_issue127_example() -> None:
    """Test example from issue #127."""
    template = ENV.from_string(
        "{% for x in (1..3) %}{{ x }}"
        "{% unless forloop.last %}\n{% endunless %}{% endfor %}"
    )
    assert template.render() == "1\n2\n3"
