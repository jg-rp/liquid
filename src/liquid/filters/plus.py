from decimal import Decimal

from .._filter import FilterContext


def plus(context: FilterContext, left: object, right: object) -> int | float:
    left = context.to_numeric(left, 0)
    right = context.to_numeric(right, 0)

    if isinstance(left, int) and isinstance(right, int):
        return left + right

    return float(Decimal(str(left)) + Decimal(str(right)))
