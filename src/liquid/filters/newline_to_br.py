import re

import markupsafe

from .._filter import FilterContext

RE_LINETERM = re.compile(r"\r?\n")


def newline_to_br(context: FilterContext, left: object) -> str:
    if context.env.autoescape:
        return markupsafe.Markup(
            RE_LINETERM.sub("<br />\n", markupsafe.escape(context.to_str(left, "")))
        )

    return RE_LINETERM.sub("<br />\n", context.to_str(left, ""))
