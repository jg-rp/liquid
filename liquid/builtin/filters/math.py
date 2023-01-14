"""Maths related filter definitions."""

import math
import decimal

from typing import Optional
from typing import Union

from liquid.context import is_undefined
from liquid.exceptions import FilterArgumentError

from liquid.filter import math_filter
from liquid.filter import num_arg

DecimalT = decimal.Decimal
NumberT = Union[float, int]


@math_filter
def abs_(num: NumberT) -> NumberT:
    """Return the absolute value of a number.

    Accepts an int, float or a string representations of an int or float.
    """
    return abs(num)


@math_filter
def at_most(num: NumberT, other: NumberT) -> NumberT:
    """Return `val` or `args[0]`, whichever is smaller.

    Accepts an int, float or a string representations of an int or float.
    """
    other = num_arg(other, default=0)
    return min(num, other)


@math_filter
def at_least(num: NumberT, other: NumberT) -> NumberT:
    """Return `val` or `args[0]`, whichever is greater.

    Accepts an int, float or a string representations of an int or float.
    """
    other = num_arg(other, default=0)
    return max(num, other)


@math_filter
def ceil(num: NumberT) -> NumberT:
    """Return the ceiling of x as an Integral.

    Accepts an int, float or a string representations of an int or float.
    """
    return math.ceil(num)


@math_filter
def divided_by(num: NumberT, other: object) -> NumberT:
    """Divide `num` by `other`."""
    other = num_arg(other, default=0)

    try:
        if isinstance(other, int) and isinstance(num, int):
            return num // other
        return num / other
    except ZeroDivisionError as err:
        raise FilterArgumentError(f"divided_by: can't divide by {other}") from err


@math_filter
def floor(num: NumberT) -> NumberT:
    """Return the floor of x as an Integral.

    Accepts an int, float or a string representations of an int or float.
    """
    return math.floor(num)


@math_filter
def minus(num: NumberT, other: NumberT) -> NumberT:
    """Subtract one number from another."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num - other
    return float(DecimalT(str(num)) - DecimalT(str(other)))


@math_filter
def plus(num: NumberT, other: NumberT) -> NumberT:
    """Add one number to another."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num + other
    return float(DecimalT(str(num)) + DecimalT(str(other)))


@math_filter
def round_(num: NumberT, ndigits: Optional[int] = None) -> NumberT:
    """Round a number to a given precision in decimal digits."""
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
def times(num: NumberT, other: NumberT) -> NumberT:
    """Multiply a value by an integer or float."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num * other
    return float(DecimalT(str(num)) * DecimalT(str(other)))


@math_filter
def modulo(num: NumberT, other: NumberT) -> NumberT:
    """Divide a value by a number and returns the remainder."""
    other = num_arg(other, default=0)

    try:
        if isinstance(num, int) and isinstance(other, int):
            return num % other
        return float(DecimalT(str(num)) % DecimalT(str(other)))

    except ZeroDivisionError as err:
        raise FilterArgumentError(f"modulo: can't divide by {other}") from err
