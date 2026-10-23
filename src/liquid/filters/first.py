from collections.abc import Mapping, Sequence
from itertools import islice

from .._drop import liquid_iterable
from .._filter import FilterContext


def first(context: FilterContext, left: object) -> object:
    if liquid_iterable(left):
        it = left.__liquid_iter__(0, None, False)
        return next(iter(it), None)

    if isinstance(left, Sequence):
        return left[0] if left else None  # pyright: ignore[reportUnknownVariableType]

    if isinstance(left, Mapping):
        return next(islice(left.items(), 1), None)  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

    return None
