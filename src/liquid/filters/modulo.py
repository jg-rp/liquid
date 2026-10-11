from decimal import Decimal

from .._filter import FilterContext


def modulo(
    context: FilterContext, left: object, right: object
) -> int | float | Decimal:
    left = context.to_numeric(left, 0)
    right = context.to_numeric(right, 0)

    if right == 0:
        raise context.error("divide by zero")

    if isinstance(left, int) and isinstance(right, int):
        return left % right

    return float(Decimal(left) / Decimal(right))
