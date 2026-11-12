from collections.abc import Sequence

from .._filter import FilterContext
from ..drops import Range, Undefined


def last(context: FilterContext, left: object) -> object:
    if isinstance(left, Range):
        return left.stop

    if isinstance(left, Sequence):
        return left[-1] if left else None  # pyright: ignore[reportUnknownVariableType]

    if isinstance(left, Undefined):
        left.poke()

    return None
