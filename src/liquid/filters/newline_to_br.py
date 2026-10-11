import re

import markupsafe

from .._filter import FilterContext

RE_LINETERM = re.compile(r"\r?\n")


def newline_to_br(context: FilterContext, left: object) -> str:
    left = context.to_str(left, "")

    if context.env.autoescape:
        return markupsafe.Markup(RE_LINETERM.sub("<br />\n", markupsafe.escape(left)))

    return RE_LINETERM.sub("<br />\n", left)
