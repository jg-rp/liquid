# type: ignore
"""Legacy, class-based implementations of miscellaneous filters."""

import datetime
import functools

from dateutil import parser

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup

from liquid import is_undefined
from liquid.filter import Filter
from liquid.exceptions import FilterArgumentError
from liquid.expression import EMPTY


# pylint: disable=arguments-differ  too-few-public-methods


class AbstractFilter(Filter):

    name = "AbstractStringFilter"
    num_args = 0
    msg = "{}: unexpected argument type {}"

    def __call__(self, val, *args, **kwargs):
        if len(args) != self.num_args:
            raise FilterArgumentError(
                f"{self.name}: expected {self.num_args} arguments, found {len(args)}"
            )

        try:
            return self.filter(val, *args, **kwargs)
        except (AttributeError, TypeError) as err:
            raise FilterArgumentError(
                self.msg.format(self.name, type(val).__name__)
            ) from err

    def filter(self, val, *args, **kwargs):
        raise NotImplementedError(":(")


class Size(AbstractFilter):
    """Return the length of an array or string."""

    __slots__ = ()

    name = "size"
    msg = "{}: expected an array or string, found {}"

    def filter(self, obj):
        return len(obj)


class Default(AbstractFilter):
    """Return a default value if the input is nil, false, or empty."""

    __slots__ = ()

    name = "default"
    num_args = 1

    def filter(self, obj, _default, allow_false=None):
        _obj = obj
        if hasattr(obj, "__liquid__"):
            _obj = obj.__liquid__()

        if allow_false is True and _obj is False:
            return obj

        if _obj in (None, False, EMPTY) or is_undefined(_obj):
            return _default

        return obj


class Date(AbstractFilter):
    """Converts a timestamp into another date format."""

    __slots__ = ()

    name = "date"
    num_args = 1

    @functools.lru_cache(maxsize=10)
    def filter(self, dt, fmt):
        if is_undefined(dt):
            return ""

        if is_undefined(fmt):
            raise FilterArgumentError(
                f"expected a format string, found {type(fmt).__name__}"
            )

        if isinstance(dt, str):
            if dt == "now":
                dt = datetime.datetime.now()
            else:
                dt = parser.parse(dt)

        if not isinstance(dt, (datetime.datetime, datetime.date)):
            raise FilterArgumentError(
                f"{self.name}: expected datetime.datetime, found {type(dt)} "
            )

        rv = dt.strftime(fmt)

        if self.env.autoescape and isinstance(fmt, Markup):
            return Markup(rv)
        return rv
