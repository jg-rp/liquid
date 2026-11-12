import math
from decimal import Decimal

from .._filter import FilterContext


def floor(context: FilterContext, left: object) -> int | float | Decimal:
    return math.floor(context.to_numeric(left, 0))
