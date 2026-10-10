import datetime

import markupsafe
from dateutil import parser

from .._filter import FilterContext


def date(context: FilterContext, obj: object, fmt: str) -> str:
    if context.is_nil(obj):
        return ""

    if context.is_nil(fmt):
        return context.to_str(obj, "")

    if isinstance(obj, str):
        if obj in ("now", "today"):
            date_ = datetime.datetime.now()  # noqa: DTZ005

        elif obj.isdigit():
            # The reference implementation does not support string
            # representations of negative integers either.
            date_ = datetime.datetime.fromtimestamp(int(obj))  # noqa: DTZ006

        else:
            try:
                date_ = parser.parse(obj)
            except parser.ParserError:
                # Input is returned unchanged. This is consistent
                # with the reference implementation.
                return obj

    elif isinstance(obj, int):
        try:
            date_ = datetime.datetime.fromtimestamp(obj)  # noqa: DTZ006
        except (OverflowError, OSError):
            # Testing on Windows shows that it can't handle some
            # negative integers.
            return str(obj)

    else:
        raise context.error(f"expected a data, found {type(obj).__name__!r}")

    try:
        result = date_.strftime(fmt)
    except ValueError as err:
        # This is not uncommon on Windows when a format string contains
        # directives that are not officially supported by Python.

        # Handle "%s" as a special case.
        if fmt == r"%s":
            return str(date_.timestamp()).split(".")[0]

        raise context.error(str(err))

    if context.env.autoescape and isinstance(fmt, markupsafe.Markup):
        return markupsafe.Markup(result)
    return result
