from decimal import Decimal

from .._filter import FilterContext


def at_most(
    context: FilterContext, left: object, right: object
) -> int | float | Decimal:
    return min(context.to_numeric(left, 0), context.to_numeric(right, 0))
