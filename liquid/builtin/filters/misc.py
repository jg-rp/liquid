"""Miscellaneous filter functions."""

from __future__ import annotations

import datetime as dt
import decimal
import functools
from typing import TYPE_CHECKING
from typing import Any
from typing import Union

from dateutil import parser

from liquid import Markup
from liquid.builtin.expressions import is_empty
from liquid.exceptions import FilterArgumentError
from liquid.filter import liquid_filter
from liquid.filter import with_environment
from liquid.undefined import is_undefined

if TYPE_CHECKING:
    from liquid import Environment


@liquid_filter
def size(obj: Any) -> int:
    """Return the length of _obj_.

    _obj_ could be a dict, list, string or any class implementing _len_.
    """
    try:
        return len(obj)
    except TypeError:
        return 0


@liquid_filter
def default(obj: Any, default_: object = "", *, allow_false: bool = False) -> Any:
    """Return _obj_, or _default_ if _obj_ is nil, false, or empty."""
    _obj = obj

    # Return the default value immediately if the object defines a
    # `force_liquid_default` property.
    if hasattr(obj, "force_liquid_default") and obj.force_liquid_default:
        return default_

    if hasattr(obj, "__liquid__"):
        _obj = obj.__liquid__()

    # Liquid 0, 0.0, 0b0, 0X0, 0o0 and Decimal("0") are not falsy.
    if not isinstance(obj, bool) and isinstance(obj, (int, float, decimal.Decimal)):
        return obj

    if allow_false is True and _obj is False:
        return obj

    if _obj in (None, False) or is_empty(_obj):
        return default_

    return obj


@with_environment
@liquid_filter
def date(
    dat: Union[dt.datetime, str, int],
    fmt: str,
    *,
    environment: Environment,
) -> str:
    """Return a string representation of _dat_ using format string _fmt_."""
    if is_undefined(dat):
        return ""

    if is_undefined(fmt):
        return str(dat)

    date_ = dt.datetime.now() if dat in ("now", "today") else _to_date(dat)

    if date_ is None:
        if isinstance(dat, (str, int)):
            # Input is returned unchanged. This is consistent
            # with the reference implementation.
            return str(dat)
        raise FilterArgumentError(
            f"date expected datetime.datetime, found {type(dat).__name__}",
            token=None,
        )

    try:
        rv = date_.strftime(fmt)
    except ValueError as err:
        # This is not uncommon on Windows when a format string contains
        # directives that are not officially supported by Python.

        # Handle "%s" as a special case.
        if fmt == r"%s":
            return str(date_.timestamp()).split(".")[0]
        raise FilterArgumentError(str(err), token=None) from err

    if environment.autoescape and isinstance(fmt, Markup):
        return Markup(rv)
    return rv


@functools.lru_cache(maxsize=10)
def _to_date(  # noqa: PLR0911
    d: object,
) -> Union[dt.datetime, None]:
    if isinstance(d, dt.datetime):
        return d

    if isinstance(d, dt.date):
        return dt.datetime.combine(d, dt.time.min)

    if isinstance(d, str):
        if d.isdigit():
            # The reference implementation does not support string
            # representations of negative integers either.
            return dt.datetime.fromtimestamp(int(d))

        try:
            return parser.parse(d)
        except parser.ParserError:
            # Input is returned unchanged. This is consistent
            # with the reference implementation.
            return None

    if isinstance(d, int):
        try:
            return dt.datetime.fromtimestamp(d)
        except (OverflowError, OSError):
            # Testing on Windows shows that it can't handle some
            # negative integers.
            return None

    return None
