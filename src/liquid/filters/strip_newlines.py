import re

import markupsafe

from .._filter import FilterContext

RE_NEWLINES = re.compile(r"\r?\n")


def strip_newlines(context: FilterContext, left: object) -> str:
    left = context.to_str(left, "")
    stripped = RE_NEWLINES.sub("", left)
    return (
        markupsafe.Markup(stripped) if isinstance(left, markupsafe.Markup) else stripped
    )
