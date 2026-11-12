from collections.abc import Mapping, Sequence
from decimal import Decimal

from .._drop import liquid_iterable
from .._filter import FilterContext
from ..drops import Undefined


def size(context: FilterContext, left: object) -> int:
    if isinstance(left, (float, bool)):
        return 0

    if isinstance(left, (int, Decimal)):
        return 8

    if isinstance(left, Undefined):
        return 0

    if isinstance(left, (Sequence, Mapping)):
        return len(left)  # pyright: ignore[reportUnknownArgumentType]

    if liquid_iterable(left):
        return left.__liquid_iter__(0, None, False).length

    return 0
