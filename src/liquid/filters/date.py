import markupsafe

from .._filter import FilterContext
from .._strftime import ruby_strftime


def date(context: FilterContext, obj: object, fmt: str) -> object:
    if context.is_nil(obj):
        return ""

    if context.is_nil(fmt) or fmt == "":
        return context.to_str(obj, "")

    date_ = context.to_date(obj)

    if date_ is None:
        return obj

    try:
        result = ruby_strftime(date_, fmt)
    except (ValueError, TypeError) as err:
        raise context.error(str(err))

    if context.env.autoescape and isinstance(fmt, markupsafe.Markup):
        return markupsafe.Markup(result)

    return result
