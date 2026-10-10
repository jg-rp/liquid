from .._drop import is_drop, is_iterable_drop
from .._filter import FilterContext


def last(context: FilterContext, left: object) -> object:
    if is_iterable_drop(left):
        it = left.__liquid_iter__(0, None, False)
        return next(iter(it), None)

    if is_drop(left):
        left = left.__liquid__("data", context.context)

    return None
