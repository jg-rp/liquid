from collections.abc import Mapping, Sequence
from itertools import islice

from .._drop import is_drop, is_iterable_drop
from .._filter import FilterContext


def first(context: FilterContext, left: object) -> object:
    if is_iterable_drop(left):
        it = left.__liquid_iter__(0, None, False)
        return next(iter(it), None)

    if is_drop(left):
        left = left.__liquid__("data", context.context)

    if isinstance(left, Sequence):
        return left[0] if left else None  # type: ignore

    if isinstance(left, Mapping):
        return next(islice(left.items(), 1), None)  # type: ignore

    return None
