from liquid import Environment, LaxLegacyParser, StrictUndefined


def test_render_with_errors() -> None:
    env = Environment(undefined=StrictUndefined)
    source = "Hello\n{{ nosuchthing }}\nGoodbye"
    template = env.parse(source)

    result, errors = template.render_with_errors()
    assert len(errors) == 1
    assert "nosuchthing is undefined" in result


def test_render_syntax_errors_with_a_lax_parser() -> None:
    env = Environment(parser=LaxLegacyParser)
    source = "{% if 1 =! 2 %}ok{% endif %}"
    template = env.parse(source)

    result, errors = template.render_with_errors()
    assert len(errors) == 1
    assert "unknown or missing operator" in result


def test_render_unknown_tag() -> None:
    env = Environment(parser=LaxLegacyParser)
    source = """\
      foobar

      {% if 1 != 2 %}
        {% foo %}
      {% endif %}

      bla"""

    template = env.parse(source)

    result, errors = template.render_with_errors()
    assert len(errors) == 1
    assert "unexpected tag 'foo'" in result
