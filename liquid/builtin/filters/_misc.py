"""Miscellaneous filters."""
from __future__ import annotations

import datetime
import functools

from typing import Any
from typing import Union
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from liquid import Environment


@liquid_filter
def size(obj: Any) -> int:
    """Return the length of an array or string."""
    return len(obj)


@liquid_filter
def default(obj: Any, default_: object, *, allow_false: bool = False) -> Any:
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
def date(
    dat: Union[datetime.datetime, str], fmt: str, *, environment: Environment
) -> str:
    """Formats a datetime according the the given format string."""
    if is_undefined(dat):
        return ""

    if is_undefined(fmt):
        raise FilterArgumentError(
            f"expected a format string, found {type(fmt).__name__}"
        )

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
