"""Maths related filter definitions."""

import math
import decimal

from typing import Optional
from typing import Union

from liquid.exceptions import FilterArgumentError

from liquid.filter import math_filter
from liquid.filter import num_arg
from liquid.filter import int_arg

D = decimal.Decimal
N = Union[float, int]


@math_filter
def abs_(num: N) -> N:
    """Return that absolute value of a number.

    Accepts an int, float or a string representations of an int or float.
    """
    return abs(num)


@math_filter
def at_most(num: N, other: N) -> N:
    """Return `val` or `args[0]`, whichever is smaller.

    Accepts an int, float or a string representations of an int or float.
    """
    other = num_arg(other, default=0)
    return min(num, other)


@math_filter
def at_least(num: N, other: N) -> N:
    """Return `val` or `args[0]`, whichever is greater.

    Accepts an int, float or a string representations of an int or float.
    """
    other = num_arg(other, default=0)
    return max(num, other)


@math_filter
def ceil(num: N) -> N:
    """Return the ceiling of x as an Integral.

    Accepts an int, float or a string representations of an int or float.
    """
    return math.ceil(num)


@math_filter
def divided_by(num: N, other: object) -> N:
    """Divide `num` by `other`."""
    other = num_arg(other, default=0)

    try:
        if isinstance(other, int):
            return num // other
        return num / other
    except ZeroDivisionError as err:
        raise FilterArgumentError(f"divided_by: can't divide by {other}") from err


@math_filter
def floor(num: N) -> N:
    """Return the floor of x as an Integral.

    Accepts an int, float or a string representations of an int or float.
    """
    return math.floor(num)


@math_filter
def minus(num: N, other: N) -> N:
    """Subtract one number from another."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num - other
    return float(D(str(num)) - D(str(other)))


@math_filter
def plus(num: N, other: N) -> N:
    """Add one number to another."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num + other
    return float(D(str(num)) + D(str(other)))


@math_filter
def round_(num: N, ndigits: Optional[int] = None) -> N:
    """Round a number to a given precision in decimal digits."""
    if ndigits:
        ndigits = int_arg(ndigits, default=0)
        return round(num, ndigits)
    return round(num)


@math_filter
def times(num: N, other: N) -> N:
    """Multiply a value by an integer or float."""
    other = num_arg(other, default=0)

    if isinstance(num, int) and isinstance(other, int):
        return num * other
    return float(D(str(num)) * D(str(other)))


@math_filter
def modulo(num: N, other: N) -> N:
    """Divide a value by a number and returns the remainder."""
    other = num_arg(other, default=0)

    try:
        if isinstance(num, int) and isinstance(other, int):
            return num % other
        return float(D(str(num)) % D(str(other)))

    except ZeroDivisionError as err:
        raise FilterArgumentError(f"modulo: can't divide by {other}") from err
