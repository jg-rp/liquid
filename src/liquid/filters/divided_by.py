from decimal import Decimal

from .._filter import FilterContext


def divided_by(
    context: FilterContext, left: object, right: object
) -> int | float | Decimal:
    left = context.to_numeric(left, 0)
    right = context.to_numeric(right, 0)

    if right == 0:
        raise context.error("divide by zero")

    if isinstance(left, int) and isinstance(right, int):
        return left // right

    if isinstance(left, Decimal) or isinstance(right, Decimal):
        return Decimal(left) / Decimal(right)

    return left / right
