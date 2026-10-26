import pytest

from liquid import Environment, LaxExtendedParser, LaxLegacyParser, Parser


@pytest.mark.parametrize(
    "parser",
    [
        LaxLegacyParser,
        LaxExtendedParser,
    ],
)
def test_unknown_operator(parser: type[Parser]) -> None:
    env = Environment(parser=parser)
    template = env.parse("{% if a =! b %}TRUE{% else %}FALSE{% endif %}")
    errors = template.errors()

    assert len(errors) == 1
    assert "unknown or missing operator" in str(errors[0])
    assert template.render() == "FALSE"


@pytest.mark.parametrize(
    "parser",
    [
        LaxLegacyParser,
        LaxExtendedParser,
    ],
)
def test_missing_operator(parser: type[Parser]) -> None:
    env = Environment(parser=parser)
    template = env.parse("{% if a b %}TRUE{% else %}FALSE{% endif %}")
    errors = template.errors()

    assert len(errors) == 1
    assert "unknown or missing operator" in str(errors[0])
    assert template.render() == "FALSE"


@pytest.mark.parametrize(
    "parser",
    [
        LaxLegacyParser,
        LaxExtendedParser,
    ],
)
def test_wrong_end_tag(parser: type[Parser]) -> None:
    env = Environment(parser=parser)
    template = env.parse("{% if 1 > 2 %}TRUE{% else %}FALSE{% endfor %}")
    errors = template.errors()

    assert len(errors) == 1
    assert "expected tag 'endif'" in str(errors[0])
    assert template.render() == ""
