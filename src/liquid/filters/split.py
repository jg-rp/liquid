import re

import markupsafe

from .._filter import FilterContext

RE_S = re.compile(r"\s")


def split(context: FilterContext, left: object, sep: object) -> list[str]:
    left_ = context.to_str(left, "")

    if not left_:
        return []

    sep_ = context.to_str(sep, "")

    if not sep_:
        return list(left_)

    if left_ == sep_:
        return []

    result: list[str]

    if sep_ == " ":
        result = [markupsafe.Markup(s) for s in RE_S.split(left_)]
    else:
        result = left_.split(sep_)

    if result[-1] == "":
        result.pop()

    return result
