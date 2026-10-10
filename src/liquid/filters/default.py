from decimal import Decimal

from .._drop import is_drop
from .._filter import FilterContext
from ..drops import EMPTY, FalsyStrictUndefined


def default(
    context: FilterContext, left: object, right: object, allow_false: bool = False
) -> object:
    if isinstance(left, FalsyStrictUndefined):
        return right

    if is_drop(left):
        left = left.__liquid__("boolean", context.context)

    if not isinstance(left, bool) and isinstance(left, (int, float, Decimal)):
        return left

    if allow_false and left is False:
        return right

    if not context.truthy(left) or left == EMPTY:
        return right

    return left
