import math
from decimal import ROUND_HALF_UP, Decimal

from .._filter import FilterContext


def round_(
    context: FilterContext, left: object, decimal_places: object = None
) -> int | float | Decimal:
    left = context.to_numeric(left, 0)

    if context.is_nil(decimal_places):
        return _round_up(left)

    to = context.to_numeric(decimal_places, 0)

    if to == 0:
        return _round_up(left)

    if to < 0:
        return 0

    if left == 0:
        return 0

    return _round_up(left, math.floor(to))


def _round_up(x: float | Decimal, digits: int = 0) -> int | float:
    if isinstance(x, int):
        return x

    quantum = Decimal(1).scaleb(-digits)
    result = Decimal(str(x)).quantize(quantum, rounding=ROUND_HALF_UP)
    return int(result) if digits == 0 else float(result)
