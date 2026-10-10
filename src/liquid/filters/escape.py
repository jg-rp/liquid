import html

import markupsafe

from .._filter import FilterContext


def escape(context: FilterContext, left: object) -> str:
    left = context.to_str(left, "")
    return markupsafe.escape(left) if context.env.autoescape else html.escape(left)


def escape_once(context: FilterContext, left: object) -> str:
    left = context.to_str(left, "")
    return (
        markupsafe.escape(left).unescape()
        if context.env.autoescape
        else html.escape(html.unescape(left))
    )


# TODO: escape_js
