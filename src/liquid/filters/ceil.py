import math
from decimal import Decimal

from .._filter import FilterContext


def ceil(context: FilterContext, left: object) -> int | float | Decimal:
    return math.ceil(context.to_numeric(left, 0))
