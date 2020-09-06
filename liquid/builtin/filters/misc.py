"""Filter functions that can operate on multiple input data types."""

import datetime

from dateutil import parser

from liquid.filter import Filter
from liquid.filter import (
    no_args,
    one_string_arg_required,
    array_or_string_required,
    one_arg_required,
)
from liquid.exceptions import FilterArgumentError


class Size(Filter):
    """Return the length of an array or string."""

    __slots__ = ()

    name = "size"

    @no_args
    @array_or_string_required
    def __call__(self, val, *args, **kwargs):
        return len(val)


class Default(Filter):
    """Return a default value if the input is nil, false, or empty."""

    __slots__ = ()

    name = "default"

    @one_arg_required
    def __call__(self, val, *args, **kwargs):
        return val or args[0]


class Date(Filter):
    """Converts a timestamp into another date format."""

    __slots__ = ()

    name = "date"

    @one_string_arg_required
    def __call__(self, dt, fmt):
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
