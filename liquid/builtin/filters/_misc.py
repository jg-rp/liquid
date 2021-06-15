"""Miscellaneous filters."""

import datetime
import functools

from dateutil import parser

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from liquid import is_undefined

from liquid.filter import liquid_filter
from liquid.filter import with_environment

from liquid.exceptions import FilterArgumentError
from liquid.expression import EMPTY


@liquid_filter
def size(obj):
    """Return the length of an array or string."""
    return len(obj)


@liquid_filter
def default(obj, default_, *, allow_false=None):
    """Return a default value if the input is nil, false, or empty."""
    _obj = obj
    if hasattr(obj, "__liquid__"):
        _obj = obj.__liquid__()

    if allow_false is True and _obj is False:
        return obj

    if _obj in (None, False, EMPTY) or is_undefined(_obj):
        return default_

    return obj


@with_environment
@liquid_filter
@functools.lru_cache(maxsize=10)
def date(dat, fmt, *, environment):
    """Formats a datetime according the the given format string."""
    if is_undefined(dat):
        return ""

    if isinstance(dat, str):
        if dat == "now":
            dat = datetime.datetime.now()
        else:
            dat = parser.parse(dat)

    if not isinstance(dat, (datetime.datetime, datetime.date)):
        raise FilterArgumentError(
            f"date expected datetime.datetime, found {type(dat).__name__}"
        )

    rv = dat.strftime(fmt)

    if environment.autoescape and isinstance(fmt, Markup):
        return Markup(rv)
    return rv
