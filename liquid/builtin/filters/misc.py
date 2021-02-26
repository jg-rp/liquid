"""Filter functions that can operate on multiple input data types."""

import datetime
import functools

from dateutil import parser

from liquid.filter import Filter
from liquid.exceptions import FilterArgumentError
from liquid.expression import EMPTY


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
            raise FilterArgumentError(self.msg.format(self.name, type(val))) from err

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

    def filter(self, obj, default, allow_false=None):
        if allow_false is True and obj is False:
            return obj

        if obj in (None, False, EMPTY):
            return default

        return obj


class Date(AbstractFilter):
    """Converts a timestamp into another date format."""

    __slots__ = ()

    name = "date"
    num_args = 1

    @functools.lru_cache(maxsize=10)
    def filter(self, dt, fmt):
        if isinstance(dt, str):
            if dt == "now":
                dt = datetime.datetime.now()
            else:
                dt = parser.parse(dt)

        if not isinstance(dt, (datetime.datetime, datetime.date)):
            raise FilterArgumentError(
                f"{self.name}: expected datetime.datetime, found {type(dt)} "
            )

        # TODO: Compare Ruby and Python strftime format codes.
        return dt.strftime(fmt)
