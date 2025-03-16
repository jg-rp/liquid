import pytest
from babel import UnknownLocaleError

from liquid import Environment
from liquid.extra import Currency

render = Environment(extra=True).render


def test_default_currency_code_and_locale() -> None:
    assert render("{{ 1.99 | currency }}") == "$1.99"


def test_set_default_currency_code() -> None:
    env = Environment(extra=True)
    env.filters["currency"] = Currency(default_currency_code="GBP")
    assert env.from_string("{{ 1.99 | currency }}").render() == "£1.99"


def test_currency_code_from_context() -> None:
    assert render("{{ 1.99 | currency }}", currency_code="GBP") == "£1.99"


def test_prefix_unknown_currency_code() -> None:
    assert (
        render("{{ 1.99 | currency }}", currency_code="nosuchthing")
        == "nosuchthing1.99"
    )


def test_set_default_locale() -> None:
    env = Environment(extra=True)
    env.filters["currency"] = Currency(default_locale="de")
    assert env.from_string("{{ 1.99 | currency }}").render() == "1,99\xa0$"


def test_locale_from_context() -> None:
    assert render("{{ 1.99 | currency }}", locale="de") == "1,99\xa0$"


def test_unknown_default_locale() -> None:
    env = Environment(extra=True)
    with pytest.raises(UnknownLocaleError):
        env.filters["currency"] = Currency(default_locale="nosuchthing")


def test_unknown_locale_from_context() -> None:
    # Falls back to default
    assert render("{{ 1.99 | currency }}", locale="nosuchthing") == "$1.99"


def test_set_default_format() -> None:
    env = Environment(extra=True)
    env.filters["currency"] = Currency(default_format="¤¤ #,##0.00")
    assert env.from_string("{{ 1.99 | currency }}").render() == "USD 1.99"


def test_format_from_context() -> None:
    assert render("{{ 1.99 | currency }}", currency_format="¤¤ #,##0.00") == "USD 1.99"


def test_garbage_format() -> None:
    assert render("{{ 1.99 | currency }}", currency_format="bad format") == "bad format"


def test_string_left_value() -> None:
    assert render("{{ '1.99' | currency }}") == "$1.99"


def test_invalid_string_left_value() -> None:
    assert render("{{ 'not a number' | currency }}") == "$0.00"


def test_arbitrary_object_left_value() -> None:
    assert render("{{ obj | currency }}", obj=object()) == "$0.00"


def test_separate_groups_by_default() -> None:
    assert render("{{ 811375 | currency }}") == "$811,375.00"


def test_group_separator_argument() -> None:
    assert render("{{ 811375 | currency: group_separator: false }}") == "$811375.00"


def test_money_format() -> None:
    assert render("{{ 10 | money }}") == "$10.00"


def test_money_with_currency() -> None:
    assert (
        render("{{ 10 | money_with_currency }}", currency_code="CAD", locale="en_CA")
        == "$10.00 CAD"
    )


def test_money_without_currency() -> None:
    assert render("{{ 10 | money_without_currency }}") == "10.00"


def test_money_without_trailing_zeros() -> None:
    assert render("{{ 10 | money_without_trailing_zeros }}") == "$10"


def test_parse_string_with_default_input_locale() -> None:
    assert render("{{ '10,000.00' | currency }}", locale="de") == "10.000,00\xa0$"


def test_parse_string_with_input_locale_from_context() -> None:
    assert (
        render("{{ '10.000,00' | currency }}", locale="en_US", input_locale="de")
        == "$10,000.00"
    )


def test_set_default_input_locale() -> None:
    env = Environment(extra=True)
    env.filters["currency"] = Currency(default_input_locale="de")
    assert (
        env.from_string("{{ '10.000,00' | currency }}").render(locale="en_US")
        == "$10,000.00"
    )
