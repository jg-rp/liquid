import urllib.parse

import markupsafe

from .._filter import FilterContext


def url_encode(context: FilterContext, left: object) -> str:
    left_ = context.to_str(left, "")

    if context.env.autoescape:
        return markupsafe.Markup(urllib.parse.quote_plus(left_))

    return urllib.parse.quote_plus(left_)


def url_decode(context: FilterContext, left: object) -> str:
    return urllib.parse.unquote_plus(context.to_str(left, ""), errors="strict")
