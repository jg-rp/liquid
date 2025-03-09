"""Maths related filter functions."""

import decimal
import math
from typing import Optional
from typing import Union

from liquid.exceptions import FilterArgumentError
from liquid.filter import math_filter
from liquid.filter import num_arg
from liquid.undefined import is_undefined


@math_filter
def abs_(num: Union[float, int]) -> Union[float, int]:
    """Return the absolute value of number _num_."""
    return abs(num)


@math_filter
def at_most(num: Union[float, int], other: Union[float, int]) -> Union[float, int]:
    """Return _val_ or _other_, whichever is smaller."""
    other = num_arg(other, default=0)
    return min(num, other)


@math_filter
def at_least(num: Union[float, int], other: Union[float, int]) -> Union[float, int]:
    """Return _val_ or _other_, whichever is greater."""
    other = num_arg(other, default=0)
    return max(num, other)


@math_filter
def ceil(num: Union[float, int]) -> Union[float, int]:
    """Return _num_ rounded up to the next integer."""
    return math.ceil(num)


@math_filter
def divided_by(num: Union[float, int], other: object) -> Union[float, int]:
    """Return the result of dividing _num_ by _other_.

    If both _num_ and _other_ are integers, integer division is performed.
    """
    other = num_arg(other, default=0)

    try:
        if isinstance(other, int) and isinstance(num, int):
            return num // other
        return num / other
    except ZeroDivisionError as err:
        raise FilterArgumentError(
            f"divided_by: can't divide by {other}", token=None
        ) from err


@math_filter
def floor(num: Union[float, int]) -> Union[float, int]:
    """Return _num_ rounded down to the next integer."""
    return math.floor(num)


@math_filter
def minus(num: Union[float, int], other: Union[float, int]) -> Union[float, int]:
    """Return the result of subtracting _other_ from _num_."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num - other
    return float(decimal.Decimal(str(num)) - decimal.Decimal(str(other)))


@math_filter
def plus(num: Union[float, int], other: Union[float, int]) -> Union[float, int]:
    """Return the result of adding _other_ to _num_."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num + other
    return float(decimal.Decimal(str(num)) + decimal.Decimal(str(other)))


@math_filter
def round_(num: Union[float, int], ndigits: Optional[int] = None) -> Union[float, int]:
    """Returns the result of rounding _num_ to _ndigits_ decimal digits."""
    if ndigits is None or is_undefined(ndigits):
        return round(num)

    try:
        _ndigits = num_arg(ndigits)
    except FilterArgumentError:
        # Probably a string that can't be case to an int or float
        return round(num)

    if isinstance(_ndigits, float):
        _ndigits = int(_ndigits)

    if _ndigits < 0:
        return 0
    if _ndigits == 0:
        return round(num)

    return round(num, _ndigits)


@math_filter
def times(num: Union[float, int], other: Union[float, int]) -> Union[float, int]:
    """Return the result of multiplying _num_ by _other_."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num * other
    return float(decimal.Decimal(str(num)) * decimal.Decimal(str(other)))


@math_filter
def modulo(num: Union[float, int], other: Union[float, int]) -> Union[float, int]:
    """Return the remainder of dividing _num_ by _other_."""
    other = num_arg(other, default=0)

    try:
        if isinstance(num, int) and isinstance(other, int):
            return num % other
        return float(decimal.Decimal(str(num)) % decimal.Decimal(str(other)))
    except ZeroDivisionError as err:
        raise FilterArgumentError(
            f"modulo: can't divide by {other}", token=None
        ) from err
