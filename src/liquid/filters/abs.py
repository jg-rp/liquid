from decimal import Decimal

from .._filter import FilterContext


def abs_(context: FilterContext, left: object) -> int | float | Decimal:
    return abs(context.to_numeric(left, 0))
