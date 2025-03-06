import pytest

from liquid import Environment
from liquid.exceptions import LiquidSyntaxError


def test_shorthand_indexes_with_default_environment() -> None:
    env = Environment()
    with pytest.raises(LiquidSyntaxError):
        env.from_string("{{ foo.0.bar }}")


class MockEnv(Environment):
    shorthand_indexes = True
    ternary_expressions = True
    logical_not_operator = True


ENV = MockEnv()


def test_shorthand_index() -> None:
    data = {"foo": ["World", "Liquid"]}
    template = ENV.from_string("Hello, {{ foo.0 }}!")
    assert template.render(**data) == "Hello, World!"
    template = ENV.from_string("Hello, {{ foo.1 }}!")
    assert template.render(**data) == "Hello, Liquid!"


def test_consecutive_shorthand_indexes() -> None:
    data = {"foo": [["World", "Liquid"]]}
    template = ENV.from_string("Hello, {{ foo.0.0 }}!")
    assert template.render(**data) == "Hello, World!"
    template = ENV.from_string("Hello, {{ foo.0.1 }}!")
    assert template.render(**data) == "Hello, Liquid!"


def test_shorthand_index_dot_property() -> None:
    data = {"foo": [{"bar": "World"}, {"bar": "Liquid"}]}
    template = ENV.from_string("Hello, {{ foo.0.bar }}!")
    assert template.render(**data) == "Hello, World!"
    template = ENV.from_string("Hello, {{ foo.1.bar }}!")
    assert template.render(**data) == "Hello, Liquid!"


def test_shorthand_index_in_loop_expression() -> None:
    data = {"foo": [["World", "Liquid"]]}
    template = ENV.from_string("{% for x in foo.0 %}Hello, {{ x }}! {% endfor %}")
    assert template.render(**data) == "Hello, World! Hello, Liquid! "


def test_shorthand_index_in_conditional_expression() -> None:
    data = {"foo": ["World", "Liquid"]}
    template = ENV.from_string("{% if foo.0 %}Hello, {{ foo.0 }}!{% endif %}")
    assert template.render(**data) == "Hello, World!"
    template = ENV.from_string("{% if foo.2 %}Hello, {{ foo.2 }}!{% endif %}")
    assert template.render(**data) == ""


def test_shorthand_indexes_in_case_tag() -> None:
    data = {"foo": ["World", "Liquid"]}
    template = ENV.from_string(
        "{% case foo.0 %}{% when 'World' %}Hello, World!{% endcase %}"
    )
    assert template.render(**data) == "Hello, World!"


def test_shorthand_indexes_in_ternary_expressions() -> None:
    env = MockEnv()
    data = {"foo": ["World", "Liquid"]}
    template = env.from_string("Hello, {{ foo.0 }}!")
    assert template.render(**data) == "Hello, World!"
    template = env.from_string("Hello, {{ 'you' if foo.1 }}!")
    assert template.render(**data) == "Hello, you!"
    template = env.from_string("Hello, {{ 'you' if foo.99 else foo.1 }}!")
    assert template.render(**data) == "Hello, Liquid!"


def test_shorthand_indexes_in_logical_not_expressions() -> None:
    env = MockEnv()
    data = {"foo": ["World", "Liquid"]}
    template = env.from_string("{% if not foo.0 %}Hello, {{ foo.0 }}!{% endif %}")
    assert template.render(**data) == ""
    template = env.from_string("{% if not foo.2 %}Hello, {{ foo.0 }}!{% endif %}")
    assert template.render(**data) == "Hello, World!"
