import pytest

from liquid import Environment
from liquid.exceptions import LiquidSyntaxError


def test_default_string_sequences() -> None:
    """Test that strings are not sequences by default."""
    env = Environment()
    template = env.parse("{% for x in y %}{{ x }},{% endfor %}{{ y[0] }}")
    assert template.render({"y": "hello"}) == "hello,"


def test_enable_string_sequences() -> None:
    env = Environment(iterable_strings=True)
    template = env.parse("{% for x in y %}{{ x }},{% endfor %}{{ y[0] }}")
    assert template.render({"y": "hello"}) == "h,e,l,l,o,h"


def test_string_first_and_last() -> None:
    """Test that strings respond to first and last by default."""
    env = Environment()
    template = env.parse("{{ y.first }}{{ y.last }}")
    assert template.render({"y": "hello"}) == "ho"
    template = env.parse("{{ y |first }}{{ y | last }}")
    assert template.render({"y": "hello"}) == "ho"


@pytest.mark.parametrize("obj", ["hello", "", ["a", "b"], [], 5])
def test_first_last_filter_property_parity(obj: object) -> None:
    env = Environment(globals={"x": obj})

    def render(source: str) -> str:
        return env.parse(source).render()

    env.iterable_strings = False
    assert render("{{ x.first }}") == render("{{ x | first }}")
    assert render("{{ x.last }}") == render("{{ x | last }}")

    env.iterable_strings = True
    assert render("{{ x.first }}") == render("{{ x | first }}")
    assert render("{{ x.last }}") == render("{{ x | last }}")


def test_iterable_strings_filter_empty_string() -> None:
    """An empty string yields nothing, matching the property path."""
    env = Environment(iterable_strings=True)
    template = env.parse("{{ y | first }}{{ y | last }}")
    assert template.render({"y": ""}) == ""


def test_default_logical_not_operator() -> None:
    """Test that logical _not_ is not allowed by default."""
    env = Environment()

    with pytest.raises(LiquidSyntaxError):
        env.parse("{% if not false %}TRUE{% else %}FALSE{% endif %}")


def test_enable_logical_not_operator() -> None:
    env = Environment(extended_expressions=True)
    assert env.render("{% if not false %}TRUE{% else %}FALSE{% endif %}", {}) == "TRUE"


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
        env.parse("{% if (false and true) or true %}TRUE{% else %}FALSE{% endif %}")


def test_enable_logical_parentheses() -> None:
    env = Environment(extended_expressions=True)

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
    env = Environment(extended_expressions=True)
    assert env.parse("{{ 'TRUE' if true else 'FALSE' }}").render() == "TRUE"


def test_default_shorthand_indexes() -> None:
    env = Environment()

    with pytest.raises(LiquidSyntaxError):
        env.parse("{{ a.1 }}")


def test_default_argument_separator() -> None:
    env = Environment()

    # With a colon
    assert (
        env.parse("{% for x in y limit:2 %}{{ x }}{% endfor %}").render(
            {"y": [1, 2, 3, 4, 5]}
        )
        == "12"
    )

    # With a `=`
    with pytest.raises(LiquidSyntaxError):
        env.parse("{% for x in y limit=2 %}{% endfor %}")


def test_enable_assign_argument_separator() -> None:
    env = Environment(extended_expressions=True)

    # With a colon
    assert (
        env.parse("{% for x in y limit:2 %}{{ x }}{% endfor %}").render(
            {"y": [1, 2, 3, 4, 5]}
        )
        == "12"
    )

    # With a `=`
    assert (
        env.parse("{% for x in y limit=2 %}{{x}}{% endfor %}").render(
            {"y": [1, 2, 3, 4, 5]}
        )
        == "12"
    )
