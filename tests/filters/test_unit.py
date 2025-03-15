import pytest
from babel import UnknownLocaleError

from liquid import Environment
from liquid.exceptions import LiquidValueError
from liquid.extra import Unit

render = Environment(extra=True).render


def test_defaults() -> None:
    assert render("{{ 12 | unit: 'length-meter' }}") == "12 meters"


def test_set_default_locale() -> None:
    env = Environment(extra=True)
    env.filters["unit"] = Unit(default_locale="de")
    assert env.from_string("{{ 12 | unit: 'length-meter' }}").render() == "12 Meter"


def test_get_locale_from_context() -> None:
    assert render("{{ 12 | unit: 'length-meter' }}", locale="de") == "12 Meter"


def test_set_default_length() -> None:
    env = Environment(extra=True)
    env.filters["unit"] = Unit(default_length="short")
    assert env.from_string("{{ 12 | unit: 'length-meter' }}").render() == "12 m"


def test_length_argument_takes_priority_over_default_length() -> None:
    env = Environment(extra=True)
    env.filters["unit"] = Unit(default_length="short")
    assert (
        env.from_string("{{ 12 | unit: 'length-meter', length:'narrow' }}").render()
        == "12m"
    )


def test_get_unit_length_from_context() -> None:
    assert render("{{ 12 | unit: 'length-meter' }}", unit_length="narrow") == "12m"


def test_parse_string_left_value() -> None:
    assert (
        render("{{ '1.200' | unit: 'length-meter' }}", input_locale="de")
        == "1,200 meters"
    )


def test_set_default_format() -> None:
    env = Environment(extra=True)
    env.filters["unit"] = Unit(default_format="#,##0.00")
    assert (
        env.from_string("{{ 1200 | unit: 'length-meter' }}").render()
        == "1,200.00 meters"
    )


def test_format_argument_takes_priority_over_default() -> None:
    assert (
        render("{{ 1200 | unit: 'length-meter', format:'#,##0.00' }}")
        == "1,200.00 meters"
    )


def test_get_format_from_context() -> None:
    assert (
        render("{{ 1200 | unit: 'length-meter' }}", unit_format="#,##0.00")
        == "1,200.00 meters"
    )


def test_set_unknown_default_locale() -> None:
    env = Environment(extra=True)
    with pytest.raises(UnknownLocaleError):
        env.filters["unit"] = Unit(default_locale="nosuchthing")


def test_unknown_locale_from_context() -> None:
    # Fall back to default
    assert (
        render("{{ 12 | unit: 'length-meter' }}", locale="nosuchthing") == "12 meters"
    )


def test_invalid_string_left_value() -> None:
    assert render("{{ 'not a number' | unit: 'length-meter' }}") == "0 meters"


def test_compound_units() -> None:
    assert (
        render("{{ 150 | unit: 'kilowatt', denominator_unit: 'year'  }}", locale="fi")
        == "150 kilowattia / vuosi"
    )


def test_compound_units_with_denominator() -> None:
    assert (
        render(
            "{{ 32.5 | unit: 'ton', denominator: 15, denominator_unit: 'hour' }}",
            locale="en",
        )
        == "32.5 tons per 15 hours"
    )


def test_unknown_unit_argument() -> None:
    with pytest.raises(LiquidValueError):
        render("{{ 5 | unit: 'apples' }}")
