import datetime

import dateutil
import markupsafe

from .._filter import FilterContext
from .._strftime import ruby_strftime


def date(context: FilterContext, obj: object, fmt: str) -> str:
    if context.is_nil(obj):
        return ""

    if context.is_nil(fmt) or fmt == "":
        return context.to_str(obj, "")

    # TODO: env.to_date

    if isinstance(obj, str):
        if obj in ("now", "today", "Today"):
            date_ = datetime.datetime.now()

        elif obj.isdigit():
            # The reference implementation does not support string
            # representations of negative integers either.
            date_ = datetime.datetime.fromtimestamp(int(obj))

        else:
            try:
                # TODO: Cache this?
                date_ = dateutil.parser.parse(obj)
            except dateutil.parser.ParserError:
                # Input is returned unchanged. This is consistent
                # with the reference implementation.
                return obj

    elif isinstance(obj, int):
        try:
            date_ = datetime.datetime.fromtimestamp(obj)
        except (OverflowError, OSError):
            # Testing on Windows shows that it can't handle some
            # negative integers.
            return str(obj)

    else:
        raise context.error(f"expected a data, found {type(obj).__name__!r}")

    try:
        result = ruby_strftime(date_, fmt)
    except (ValueError, TypeError) as err:
        raise context.error(str(err))

    if context.env.autoescape and isinstance(fmt, markupsafe.Markup):
        return markupsafe.Markup(result)
    return result
