"""Miscellaneous filters."""
from __future__ import annotations

import datetime
import decimal
import functools

from typing import Any
from typing import Union
from typing import TYPE_CHECKING

from dateutil import parser

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from liquid.filter import liquid_filter
from liquid.filter import with_environment

from liquid.exceptions import FilterArgumentError
from liquid.expression import EMPTY

from liquid.undefined import is_undefined

if TYPE_CHECKING:
    from liquid import Environment


@liquid_filter
def size(obj: Any) -> int:
    """Return the length of an array or string."""
    try:
        return len(obj)
    except TypeError:
        return 0


@liquid_filter
def default(obj: Any, default_: object = "", *, allow_false: bool = False) -> Any:
    """Return a default value if the input is nil, false, or empty."""
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

    if _obj in (None, False, EMPTY):
        return default_

    return obj


@with_environment
@liquid_filter
@functools.lru_cache(maxsize=10)
def date(
    dat: Union[datetime.datetime, str, int],
    fmt: str,
    *,
    environment: Environment,
) -> str:
    """Formats a datetime according the the given format string."""
    if is_undefined(dat):
        return ""

    if is_undefined(fmt):
        return str(dat)

    if isinstance(dat, str):
        if dat in ("now", "today"):
            dat = datetime.datetime.now()
        elif dat.isdigit():
            # The reference implementation does not support string
            # representations of negative integers either.
            dat = datetime.datetime.fromtimestamp(int(dat))
        else:
            try:
                dat = parser.parse(dat)
            except parser.ParserError:
                # Input is returned unchanged. This is consistent
                # with the reference implementation.
                return str(dat)
    elif isinstance(dat, int):
        try:
            dat = datetime.datetime.fromtimestamp(dat)
        except (OverflowError, OSError):
            # Testing on Windows shows that it can't handle some
            # negative integers.
            return str(dat)

    if not isinstance(dat, (datetime.datetime, datetime.date)):
        raise FilterArgumentError(
            f"date expected datetime.datetime, found {type(dat).__name__}"
        )

    rv = dat.strftime(fmt)

    if environment.autoescape and isinstance(fmt, Markup):
        return Markup(rv)
    return rv
