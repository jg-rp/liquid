import datetime

import pytest
import pytz
from babel import UnknownLocaleError

from liquid import Environment
from liquid.exceptions import LiquidTypeError
from liquid.exceptions import LiquidValueError
from liquid.extra import DateTime

DT = dt = datetime.datetime(2007, 4, 1, 15, 30)

render = Environment(extra=True).render


def test_default_options() -> None:
    assert (
        render("{{ dt | datetime }}", dt=DT)
        == "Apr 1, 2007, 3:30:00\N{NARROW NO-BREAK SPACE}PM"
    )


def test_short_format() -> None:
    assert (
        render("{{ dt | datetime: format:'short' }}", dt=DT)
        == "4/1/07, 3:30\N{NARROW NO-BREAK SPACE}PM"
    )


def test_medium_format() -> None:
    assert (
        render("{{ dt | datetime: format:'medium' }}", dt=DT)
        == "Apr 1, 2007, 3:30:00\N{NARROW NO-BREAK SPACE}PM"
    )


def test_long_format() -> None:
    assert (
        render("{{ dt | datetime: format:'long' }}", dt=DT)
        == "April 1, 2007, 3:30:00\N{NARROW NO-BREAK SPACE}PM UTC"
    )


def test_full_format() -> None:
    assert (
        render("{{ dt | datetime: format:'full' }}", dt=DT)
        == "Sunday, April 1, 2007, 3:30:00\N{NARROW NO-BREAK SPACE}PM Coordinated Universal Time"  # noqa: E501
    )


def test_custom_format() -> None:
    assert (
        render("{{ dt | datetime: format: 'EEEE, d.M.yyyy' }}", dt=DT)
        == "Sunday, 1.4.2007"
    )


def test_format_from_context() -> None:
    assert (
        render("{{ dt | datetime }}", dt=DT, datetime_format="EEEE, d.M.yyyy")
        == "Sunday, 1.4.2007"
    )


def test_set_default_timezone() -> None:
    env = Environment(extra=True)
    # Choose a static timezone so tests wont fail as we go in and out of daylight
    # saving. Etc/GMT reverses the meaning of '+' and '-' compared to UTC or GMT.
    env.filters["datetime"] = DateTime(default_timezone="Etc/GMT-1")
    assert (
        env.from_string("{{ dt | datetime }}").render(dt=DT)
        == "Apr 1, 2007, 4:30:00\N{NARROW NO-BREAK SPACE}PM"
    )


def test_get_timezone_from_context() -> None:
    assert (
        render("{{ dt | datetime }}", dt=DT, timezone="Etc/GMT-1")
        == "Apr 1, 2007, 4:30:00\N{NARROW NO-BREAK SPACE}PM"
    )


def test_unknown_timezone_falls_back_to_default() -> None:
    assert (
        render("{{ dt | datetime }}", dt=DT, timezone="foo")
        == "Apr 1, 2007, 3:30:00\N{NARROW NO-BREAK SPACE}PM"
    )


def test_unknown_default_timezone() -> None:
    env = Environment(extra=True)
    with pytest.raises(pytz.UnknownTimeZoneError):
        env.filters["datetime"] = DateTime(default_timezone="foo")


def test_set_default_locale() -> None:
    env = Environment(extra=True)
    env.filters["datetime"] = DateTime(default_locale="en_GB")
    assert (
        env.from_string("{{ dt | datetime }}").render(dt=DT) == "1 Apr 2007, 15:30:00"
    )


def test_get_locale_from_context() -> None:
    assert (
        render("{{ dt | datetime }}", dt=DT, locale="en_GB") == "1 Apr 2007, 15:30:00"
    )


def test_unknown_default_locale() -> None:
    env = Environment(extra=True)
    with pytest.raises(UnknownLocaleError):
        env.filters["datetime"] = DateTime(default_locale="nosuchthing")


def test_unknown_locale_falls_back_to_default() -> None:
    assert (
        render("{{ dt | datetime }}", dt=DT, locale="nosuchthing")
        == "Apr 1, 2007, 3:30:00\N{NARROW NO-BREAK SPACE}PM"
    )


def test_parse_a_string() -> None:
    assert (
        render("{{ 'Apr 1, 2007, 3:30:00 PM' | datetime: format: 'short' }}")
        == "4/1/07, 3:30\N{NARROW NO-BREAK SPACE}PM"
    )


def test_parse_a_string_with_tz_info() -> None:
    assert (
        render("{{ 'Apr 1, 2007, 3:30:00 PM GMT-1' | datetime: format: 'short' }}")
        == "4/1/07, 2:30\N{NARROW NO-BREAK SPACE}PM"
    )


def test_set_default_input_timezone() -> None:
    env = Environment(extra=True)
    env.filters["datetime"] = DateTime(default_input_timezone="Etc/GMT-1")
    assert (
        env.from_string(
            "{{ 'Apr 1, 2007, 3:30:00 PM' | datetime: format: 'short' }}"
        ).render()
        == "4/1/07, 2:30\N{NARROW NO-BREAK SPACE}PM"
    )


def test_garbage_string_left_value() -> None:
    with pytest.raises(LiquidValueError):
        render("{{ 'foobar' | datetime: format: 'short' }}")


def test_now() -> None:
    assert render("{{ 'now' | datetime }}", datetime_format="yyyy") == str(
        datetime.datetime.today().year
    )


def test_today() -> None:
    assert render("{{ 'today' | datetime }}", datetime_format="yyyy") == str(
        datetime.datetime.today().year
    )


def test_int_left_value() -> None:
    assert (
        render("{{ 1152098955 | datetime }}")
        == "Jul 5, 2006, 11:29:15\N{NARROW NO-BREAK SPACE}AM"
    )


def test_arbitrary_object_left_value() -> None:
    with pytest.raises(LiquidTypeError):
        render("{{ obj | datetime: format: 'short' }}", obj=object())


def test_filter_args_take_priority_over_render_context() -> None:
    assert (
        render(
            "{{ 'Apr 1, 2007, 3:30:00 PM' | datetime: format:'short' }}",
            datetime_format="full",
        )
        == "4/1/07, 3:30\N{NARROW NO-BREAK SPACE}PM"
    )


def test_timestamp_as_string() -> None:
    assert (
        render("{{ '1152098955' | datetime }}")
        == "Jul 5, 2006, 11:29:15\N{NARROW NO-BREAK SPACE}AM"
    )


def test_timestamp_as_float() -> None:
    assert (
        render("{{ 1152098955.0 | datetime }}")
        == "Jul 5, 2006, 11:29:15\N{NARROW NO-BREAK SPACE}AM"
    )
