from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from babel import Locale, UnknownLocaleError, dates, numbers, units
from dateutil import parser

if TYPE_CHECKING:
    from .._filter import FilterContext


def _resolve_locale(
    context: FilterContext,
    locale_var: str,
    default: Locale,
) -> Locale:
    locale_ = context.resolve(locale_var)

    if context.is_nil(locale_):
        locale = default

    elif isinstance(locale_, str):
        try:
            locale = Locale.parse(locale_)
        except UnknownLocaleError:
            locale = default

    else:
        raise context.error(
            f"expected a string argument, found {locale_.__class__.__name__}"
        )

    return locale


class Currency:
    """A Liquid filter for formatting currency values.

    Parameters
    ----------
    currency_code_var
        The name of a render context variable that resolves to the current currency code.
        Defaults to ``"currency_code"``.
    default_currency_code
        A fallback currency code if `currency_code_var` can not be resolved. Defaults to
        ``"USD"``.
    locale_var
        The name of a render context variable that resolves to the current locale.
        Defaults to ``"locale"``.
    default_locale
        A fallback locale to use if `locale_var` can not be resolved. Defaults to
        ``"en_US"``.
    format_var
        The name of a render context variable that resolves to the current currency
        format string. Defaults to ``"currency_format"``.
    default_format
        A fallback currency format that is used if `format_var` can not be resolved.
        Defaults to `None`, which means the standard format for the current locale will
        be used.
    currency_digits
        Indicates if the format should override locale specific trailing digit behavior.
        Defaults to ``False``.
    input_locale_var
        The name of a render context variable that resolves to a locale suitable for
        parsing input strings to decimals. Defaults to ``"input_locale"``.
    default_input_locale
        A fallback locale to use if `input_locale_var` can not be resolved. Defaults to
        ``"en_US"``.
    """

    def __init__(
        self,
        *,
        currency_code_var: str = "currency_code",
        default_currency_code: str = "USD",
        locale_var: str = "locale",
        default_locale: str = "en_US",
        format_var: str = "currency_format",
        default_format: str | None = None,
        currency_digits: bool = True,
        input_locale_var: str = "input_locale",
        default_input_locale: str = "en_US",
    ) -> None:
        self.currency_code_var = currency_code_var
        self.default_currency_code = default_currency_code
        self.locale_var = locale_var
        self.default_locale = Locale.parse(default_locale)
        self.format_var = format_var
        self.default_format = default_format
        self.currency_digits = currency_digits
        self.input_locale_var = input_locale_var
        self.default_input_locale = Locale.parse(default_input_locale)

    def __call__(
        self,
        context: FilterContext,
        left: object,
        *,
        group_separator: bool = True,
    ) -> str:
        """Apply the filter and return the result."""
        locale = _resolve_locale(
            context,
            self.locale_var,
            default=self.default_locale,
        )

        input_locale = _resolve_locale(
            context,
            self.input_locale_var,
            default=self.default_input_locale,
        )

        format_ = context.resolve(self.format_var)
        if context.is_nil(format_):
            format_ = self.default_format

        if format_ is not None and not isinstance(format_, str):
            raise context.error(f"expected a string argument, found {format_}")

        currency_code = context.resolve(self.currency_code_var)
        if context.is_nil(currency_code):
            currency_code = self.default_currency_code

        if not isinstance(currency_code, str):
            raise context.error(f"expected a string argument, found {currency_code}")

        return numbers.format_currency(
            _parse_decimal(context, left, input_locale),
            currency_code,
            format=format_,
            locale=locale,
            group_separator=group_separator,
            currency_digits=self.currency_digits,
        )


def _parse_decimal(
    context: FilterContext, val: object, locale: str | Locale
) -> Decimal:
    if isinstance(val, str):
        try:
            return numbers.parse_decimal(val, locale)
        except numbers.NumberFormatError:
            return Decimal(0)

    if isinstance(val, (Decimal, float, int)):
        return Decimal(val)

    # Give objects that implement __int__ etc. a chance.
    return Decimal(context.to_decimal(val, 0))


class DateTime:
    """A Liquid filter for formatting datetime objects.

    Parameters
    ----------
    timezone_var
        The name of a render context variable that resolves to a timezone. Defaults to
        ``"timezone"``.
    default_timezone
        A fallback timezone to use if `timezone_var` can not be resolved. Defaults to
        ``"UTC"``.
    locale_var
        The name of a render context variable that resolves to the current locale.
        Defaults to ``"locale"``.
    default_locale
        A fallback locale to use if `locale_var` can not be resolved. Defaults to
        ``"en_US"``.
    format_var
        The name of a render context variable that resolves to the current datetime
        format string. Defaults to ``"datetime_format"``.
    default_format
        A fallback datetime format that is used if `format_var` can not be resolved.
        Defaults to ``"medium"``.
    input_timezone_var
        The name of a render context variable that resolves to a timezone for parsing
        datetimes entered as strings. Defaults to ``"input_timezone"``.
    default_input_timezone
        A fallback timezone to use if `input_timezone_var` can not be resolved. Defaults
        to ``"UTC"``.
    """

    formats: ClassVar[dict[str, str]] = {
        "short": "short",
        "medium": "medium",
        "long": "long",
        "full": "full",
    }

    def __init__(
        self,
        *,
        timezone_var: str = "timezone",
        default_timezone: str = "UTC",
        locale_var: str = "locale",
        default_locale: str = "en_US",
        format_var: str = "datetime_format",
        default_format: str = "medium",
        input_timezone_var: str = "input_timezone",
        default_input_timezone: str = "UTC",
    ) -> None:
        self.timezone_var = timezone_var
        self.default_timezone = ZoneInfo(default_timezone)
        self.locale_var = locale_var
        self.default_locale = Locale.parse(default_locale)
        self.format_var = format_var
        self.default_format = self.formats.get(default_format, default_format)
        self.input_timezone_var = input_timezone_var
        self.default_input_timezone = ZoneInfo(default_input_timezone)

    def __call__(
        self,
        context: FilterContext,
        left: object,
        *,
        format: str | None = None,
    ) -> str:
        """Apply the filter and return the result."""
        locale = _resolve_locale(
            context,
            self.locale_var,
            default=self.default_locale,
        )

        if format:
            _format = self.formats.get(format, format)
        else:
            format_string = context.resolve(self.format_var)

            if context.is_nil(format_string):
                _format = self.default_format
            elif not isinstance(format_string, str):
                raise context.error(
                    f"expected a string argument, found {format_string}"
                )
            else:
                _format = self.formats.get(format_string, format_string)

        tzinfo = self._resolve_timezone(
            context,
            self.timezone_var,
            default=self.default_timezone,
        )

        input_tzinfo = self._resolve_timezone(
            context,
            self.input_timezone_var,
            default=self.default_input_timezone,
        )

        return dates.format_datetime(
            _parse_datetime(context, left, input_tzinfo),
            format=_format,
            locale=locale,
            tzinfo=tzinfo,
        )

    def _resolve_timezone(
        self,
        context: FilterContext,
        timezone_var: str,
        default: ZoneInfo,
    ) -> ZoneInfo:
        _tz = context.resolve(timezone_var)

        if context.is_nil(_tz):
            timezone = default
        elif isinstance(_tz, str):
            try:
                timezone = ZoneInfo(_tz)
            except ZoneInfoNotFoundError:
                timezone = default
        else:
            raise context.error(f"expected a string argument, found {_tz}")

        return timezone


def _parse_number(val: str) -> int | float:
    try:
        return int(val)
    except ValueError:
        # Let the ValueError raise
        return float(val)


def _parse_datetime(
    context: FilterContext,
    val: object,
    default_timezone: ZoneInfo,
) -> date | time | datetime | int | float | None:
    if isinstance(val, str):
        # `date.format_datetime` will use the current timestamp if
        # given `None`.
        if val in ("now", "today"):
            return None

        # String representations of ints and floats need to be cast
        # to an int or float, but not passed to the fuzzy parser.
        try:
            return _parse_number(val)
        except ValueError:
            pass

        # Fuzzy parsing using dateutil.
        try:
            _dt = parser.parse(val)
            if _dt.tzinfo is None:
                return _dt.replace(tzinfo=default_timezone)
            return _dt
        except parser.ParserError as err:
            raise context.error(str(err)) from err

    if not isinstance(val, (date, time, datetime, int, float)):
        raise context.error(f"date expected date or time, found {type(val).__name__}")

    return val


class Number:
    """A Liquid filter for formatting decimal values.

    Parameters
    ----------
    decimal_quantization_var
        The name of a render context variable that resolves to the decimal quantization
        to be used. Defaults to ``"decimal_quantization"``.
    default_decimal_quantization:
        A fallback decimal quantization if `decimal_quantization_var` can not be
        resolved. Defaults to ``False``.
    locale_var
        The name of a render context variable that resolves to the current locale.
        Defaults to ``"locale"``.
    default_locale
        A fallback locale to use if `locale_var` can not be resolved. Defaults to
        ``"en_US"``.
    format_var
        The name of a render context variable that resolves to the current decimal format
        string. Defaults to ``"decimal_format"``.
    default_format
        A fallback decimal format that is used if `format_var` can not be resolved.
        Defaults to ``None``, which means the standard format for the current locale will
        be used.
    input_locale_var
        The name of a render context variable that resolves to a locale suitable for
        parsing input strings to decimals. Defaults to ``"input_locale"``.
    default_input_locale
        A fallback locale to use if `input_locale_var` can not be resolved. Defaults to
        ``"en_US"``.
    """

    def __init__(
        self,
        *,
        decimal_quantization_var: str = "decimal_quantization",
        default_decimal_quantization: bool = False,
        locale_var: str = "locale",
        default_locale: str = "en_US",
        format_var: str = "decimal_format",
        default_format: str | None = None,
        input_locale_var: str = "input_locale",
        default_input_locale: str = "en_US",
    ) -> None:
        self.decimal_quantization_var = decimal_quantization_var
        self.default_decimal_quantization = default_decimal_quantization
        self.locale_var = locale_var
        self.default_locale = Locale.parse(default_locale)
        self.format_var = format_var
        self.default_format = default_format
        self.input_locale_var = input_locale_var
        self.default_input_locale = Locale.parse(default_input_locale)

    def __call__(
        self,
        context: FilterContext,
        left: object,
        *,
        group_separator: bool = True,
    ) -> str:
        """Apply the filter and return the result."""
        decimal_quantization = context.resolve(self.decimal_quantization_var)
        if context.is_nil(decimal_quantization):
            decimal_quantization = self.default_decimal_quantization

        if not isinstance(decimal_quantization, bool):
            raise context.error(
                f"expected a Boolean argument, found {decimal_quantization!r}"
            )

        locale = _resolve_locale(
            context,
            self.locale_var,
            default=self.default_locale,
        )

        input_locale = _resolve_locale(
            context,
            self.input_locale_var,
            default=self.default_input_locale,
        )

        format_ = context.resolve(self.format_var)
        if context.is_nil(format_):
            format_ = self.default_format

        if format_ is not None and not isinstance(format_, str):
            raise context.error(f"expected a string argument, found {format_}")

        return numbers.format_decimal(  # type: ignore
            _parse_decimal(context, left, input_locale),
            format=format_,
            locale=locale,
            group_separator=group_separator,
            decimal_quantization=decimal_quantization,
        )


class Unit:
    """A Liquid filter for formatting units of measurement.

    Parameters
    ----------
    locale_var
        The name of a render context variable that resolves to the current locale.
        Defaults to ``"locale"``.
    default_locale
        A fallback locale to use if `locale_var` can not be resolved. Defaults to
        ``"en_US"``.
    length_var
        The name of a render context variable that resolves to a unit format length.
        Should be one of ``"short"``, ``"long"`` or ``"narrow"``. Defaults to ``"long"``.
    default_length
        A fallback format length to use if `length_var` can not be resolved.
    format_var
        The name of a render context variable that resolves to a decimal format string.
        Defaults to ``"unit_format"``.
    default_format
        A fallback decimal format to use if `format_var` can not be resolved. Defaults to
        ``None``, meaning the locale's standard decimal format is used.
    input_locale_var
        The name of a render context variable that resolves to a locale suitable for
        parsing input strings to decimals. Defaults to ``"input_locale"``.
    default_input_locale
        A fallback locale to use if `input_locale_var` can not be resolved. Defaults to
        ``"en_US"``.
    """

    def __init__(
        self,
        *,
        locale_var: str = "locale",
        default_locale: str = "en_US",
        length_var: str = "unit_length",
        default_length: str = "long",
        format_var: str = "unit_format",
        default_format: str | None = None,
        input_locale_var: str = "input_locale",
        default_input_locale: str = "en_US",
    ) -> None:
        self.locale_var = locale_var
        self.default_locale = Locale.parse(default_locale)
        self.length_var = length_var
        self.default_length = default_length
        self.format_var = format_var
        self.default_format = default_format
        self.input_locale_var = input_locale_var
        self.default_input_locale = Locale.parse(default_input_locale)

    def __call__(
        self,
        context: FilterContext,
        left: object,
        measurement_unit: str,
        *,
        denominator: object = None,
        denominator_unit: str | None = None,
        length: str | None = None,
        format: str | None = None,
    ) -> str:
        try:
            return self._inner(
                context,
                left,
                measurement_unit,
                denominator=denominator,
                denominator_unit=denominator_unit,
                length=length,
                format=format,
            )
        except TypeError as err:
            raise context.error(str(err)) from err
        except units.UnknownUnitError as err:
            raise context.error(str(err)) from err

    def _inner(
        self,
        context: FilterContext,
        left: object,
        measurement_unit: str,
        *,
        denominator: object = None,
        denominator_unit: str | None = None,
        length: str | None = None,
        format: str | None = None,
    ) -> str:
        locale = _resolve_locale(
            context,
            self.locale_var,
            default=self.default_locale,
        )

        input_locale = _resolve_locale(
            context,
            self.input_locale_var,
            default=self.default_input_locale,
        )

        length_ = length if length else context.resolve(self.length_var)

        if length_ not in ("short", "long", "narrow"):
            length_ = self.default_length

        assert isinstance(length_, str)

        if format:
            format_: str | None = format
        else:
            format_string = context.resolve(self.format_var)
            if isinstance(format_string, str):
                format_ = format_string
            else:
                format_ = self.default_format

        if denominator is not None or denominator_unit is not None:
            denominator_ = (
                _parse_decimal(context, denominator, input_locale)
                if denominator is not None
                else 1
            )
            return units.format_compound_unit(
                _parse_decimal(context, left, input_locale),
                numerator_unit=measurement_unit,
                denominator_value=denominator_,  # type: ignore
                denominator_unit=denominator_unit,
                length=length_,  # type: ignore
                format=format_,
                locale=locale,
            )

        return units.format_unit(
            _parse_decimal(context, left, input_locale),
            measurement_unit=measurement_unit,
            length=length_,  # type: ignore
            format=format_,
            locale=locale,
        )
