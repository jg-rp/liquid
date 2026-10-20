import html
import re

import markupsafe

from .._filter import FilterContext


def escape(context: FilterContext, left: object) -> str:
    left_ = context.to_str(left, "")
    return (
        markupsafe.escape(str(left_))
        if context.env.autoescape
        else html.escape(left_).replace("&#x27;", "&#39;")
    )


def escape_once(context: FilterContext, left: object) -> str:
    left_ = context.to_str(left, "")
    return (
        markupsafe.Markup(left_).unescape()
        if context.env.autoescape
        else html.escape(html.unescape(left_)).replace("&#x27;", "&#39;")
    )


_ESCAPE_MAP = {
    "\\": "\\u005C",
    "'": "\\u0027",
    '"': "\\u0022",
    ">": "\\u003E",
    "<": "\\u003C",
    "&": "\\u0026",
    "=": "\\u003D",
    "-": "\\u002D",
    ";": "\\u003B",
    "`": "\\u0060",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}

_ESCAPE_MAP.update({chr(c): f"\\u{c:04X}" for c in range(32)})
_ESCAPE_RE = re.compile("[" + re.escape("".join(_ESCAPE_MAP.keys())) + "]")


def escapejs(context: FilterContext, left: object) -> str:
    escaped = _ESCAPE_RE.sub(lambda m: _ESCAPE_MAP[m.group()], context.to_str(left, ""))
    if context.env.autoescape:
        return markupsafe.Markup(escaped)
    return escaped


def safe(context: FilterContext, left: object) -> str:
    return (
        markupsafe.Markup(left) if context.env.autoescape else context.to_str(left, "")
    )
