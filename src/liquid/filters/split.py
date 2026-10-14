import re

import markupsafe

from .._filter import FilterContext

RE_S = re.compile(r"\s")


def split(context: FilterContext, left: object, sep: object) -> list[str]:
    left = context.to_str(left, "")

    if not left:
        return []

    sep = context.to_str(sep, "")

    if not sep:
        return list(left)

    if left == sep:
        return []

    result: list[str]

    if sep == " ":
        result = [markupsafe.Markup(s) for s in RE_S.split(left)]
    else:
        result = left.split(sep)

    if result[-1] == "":
        result.pop()

    return result
