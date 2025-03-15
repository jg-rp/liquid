import pytest
from babel import UnknownLocaleError

from liquid import Environment
from liquid.extra import Number

render = Environment(extra=True).render


def test_defaults() -> None:
    assert render("{{ '374881.01' | decimal }}") == "374,881.01"


def test_set_default_locale() -> None:
    env = Environment(extra=True)
    env.filters["decimal"] = Number(default_locale="de")
    assert env.from_string("{{ '374881.01' | decimal }}").render() == "374.881,01"


def test_default_locale_from_context() -> None:
    assert render("{{ '374881.01' | decimal }}", locale="de") == "374.881,01"


def test_default_decimal_quantization_is_false() -> None:
    assert render("{{ '2.2346' | decimal }}") == "2.2346"


def test_set_default_decimal_quantization() -> None:
    env = Environment(extra=True)
    env.filters["decimal"] = Number(default_decimal_quantization=True)
    assert env.from_string("{{ '2.2346' | decimal }}").render() == "2.235"


def test_default_decimal_quantization_from_context() -> None:
    assert render("{{ '2.2346' | decimal }}", decimal_quantization=True) == "2.235"


def test_input_locale_from_context() -> None:
    assert (
        render("{{ '10.000,00' | decimal }}", locale="en_US", input_locale="de")
        == "10,000"
    )


def test_set_default_input_locale() -> None:
    env = Environment(extra=True)
    env.filters["decimal"] = Number(default_input_locale="de")
    assert env.from_string("{{ '10.000,00' | decimal }}").render() == "10,000"


def test_set_unknown_default_locale() -> None:
    env = Environment(extra=True)
    with pytest.raises(UnknownLocaleError):
        env.filters["decimal"] = Number(default_locale="nosuchthing")


def test_unknown_locale_from_context_falls_back_to_default() -> None:
    assert render("{{ '1.99' | decimal }}", locale="nosuchthing") == "1.99"


def test_invalid_string_left_value() -> None:
    assert render("{{ 'not a number' | decimal }}") == "0"


def test_arbitrary_object_left_value() -> None:
    assert render("{{ obj | decimal }}", obj=object()) == "0"


def test_float_left_value() -> None:
    assert render("{{ 1.5 | decimal }}") == "1.5"
