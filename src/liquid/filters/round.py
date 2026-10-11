import math
from decimal import Decimal

from .._filter import FilterContext


def round_(
    context: FilterContext, left: object, decimal_places: object = None
) -> int | float | Decimal:
    if context.is_nil(decimal_places):
        return round(context.to_numeric(left, 0))

    to = context.to_numeric(decimal_places, 0)

    if to == 0:
        return round(context.to_numeric(left, 0))

    if to < 0:
        return 0

    return round(context.to_numeric(left, 0), math.floor(to))
