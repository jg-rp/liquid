from collections.abc import Sequence

from .._drop import is_drop
from .._filter import FilterContext
from ..drops import Range, Undefined


def last(context: FilterContext, left: object) -> object:
    if isinstance(left, Range):
        return left.stop

    if is_drop(left):
        left = left.__liquid__("data", context.context)

    if isinstance(left, Sequence):
        return left[-1] if left else None  # type: ignore

    if isinstance(left, Undefined):
        left.poke()

    return None
