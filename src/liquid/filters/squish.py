import re

from .._filter import FilterContext

RE_WHITESPACE = re.compile(r"\s+")


def squish(context: FilterContext, left: object) -> str:
    return RE_WHITESPACE.sub(" ", context.to_str(left, "").strip())
