"""Test liquid environment options."""

import pytest

from liquid import Environment
from liquid.exceptions import LiquidSyntaxError


def test_default_string_sequences() -> None:
    """Test that strings are not sequences by default."""
    env = Environment()
    template = env.from_string("{% for x in y %}{{ x }},{% endfor %}{{ y[0] }}")
    assert template.render(y="hello") == "hello,"


def test_enable_string_sequences() -> None:
    class MockEnv(Environment):
        string_sequences = True

    env = MockEnv()
    template = env.from_string("{% for x in y %}{{ x }},{% endfor %}{{ y[0] }}")
    assert template.render(y="hello") == "h,e,l,l,o,h"


def test_default_string_first_and_last() -> None:
    """Test that strings do not respond to first and last by default."""
    env = Environment()
    template = env.from_string("{{ y.first }}{{ y.last }}")
    assert template.render(y="hello") == ""


def test_enable_string_first_and_last() -> None:
    class MockEnv(Environment):
        string_first_and_last = True

    env = MockEnv()
    template = env.from_string("{{ y.first }}{{ y.last }}")
    assert template.render(y="hello") == "ho"


def test_default_logical_parentheses() -> None:
    """Test that parentheses are not allowed in logical expressions by default."""
    env = Environment()

    # Without parens
    assert (
        env.parse(
            "{% if false and true or true %}TRUE{% else %}FALSE{% endif %}"
        ).render()
        == "FALSE"
    )

    with pytest.raises(LiquidSyntaxError):
        # With parens
        env.parse(
            "{% if (false and true) or true %}TRUE{% else %}FALSE{% endif %}"
        ).render()


def test_enable_logical_parentheses() -> None:
    class MockEnv(Environment):
        logical_parentheses = True

    env = MockEnv()

    # Without parens
    assert (
        env.parse(
            "{% if false and true or true %}TRUE{% else %}FALSE{% endif %}"
        ).render()
        == "FALSE"
    )

    # With parens
    assert (
        env.parse(
            "{% if (false and true) or true %}TRUE{% else %}FALSE{% endif %}"
        ).render()
        == "TRUE"
    )


def test_default_ternary_expressions() -> None:
    """Test that ternary expressions are disabled by default."""
    env = Environment()

    with pytest.raises(LiquidSyntaxError):
        env.parse("{{ TRUE if true else FALSE }}")


def test_enable_ternary_expressions() -> None:
    class MockEnv(Environment):
        ternary_expressions = True

    env = MockEnv()
    assert env.parse("{{ 'TRUE' if true else 'FALSE' }}").render() == "TRUE"


def test_default_shorthand_indexes() -> None:
    env = Environment()

    with pytest.raises(LiquidSyntaxError):
        env.parse("{{ a.1 }}")


def test_enable_shorthand_indexes() -> None:
    class MockEnv(Environment):
        shorthand_indexes = True

    env = MockEnv()
    assert env.parse("{{ a.1 }}").render(a=["foo", "bar"]) == "bar"


def test_default_argument_separator() -> None:
    env = Environment()

    # With a colon
    assert (
        env.parse("{% for x in y limit:2 %}{{ x }}{% endfor %}").render(
            y=[1, 2, 3, 4, 5]
        )
        == "12"
    )

    # With a `=`
    with pytest.raises(LiquidSyntaxError):
        env.parse("{% for x in y limit=2 %}{% endfor %}")


def test_enable_assign_argument_separator() -> None:
    class MockEnv(Environment):
        keyword_assignment = True

    env = MockEnv()

    # With a colon
    assert (
        env.parse("{% for x in y limit:2 %}{{ x }}{% endfor %}").render(
            y=[1, 2, 3, 4, 5]
        )
        == "12"
    )

    # With a `=`
    assert (
        env.parse("{% for x in y limit=2 %}{{x}}{% endfor %}").render(y=[1, 2, 3, 4, 5])
        == "12"
    )


# TODO: test `with` is disabled by default
# TODO: test template inheritance is disabled by default
# TODO: test macros are disabled by default
