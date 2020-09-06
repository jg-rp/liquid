"""Maths related filter function definitions"""
import math
import decimal

from liquid.filter import Filter
from liquid.filter import (
    maybe_one_arg,
    expect_integer,
    no_args,
    number_required,
    one_number_arg_required,
)

D = decimal.Decimal


class Abs(Filter):
    """Return that absolute value of a number.

    Accepts an int, float or a string representations of an int or float.
    """

    __slots__ = ()

    name = "abs"

    @no_args
    @number_required
    def __call__(self, val, *args, **kwargs):
        return abs(val)


class AtMost(Filter):
    """Return `val` or `args[0]`, whichever is smaller.

    Accepts an int, float or a string representations of an int or float.
    """

    __slots__ = ()

    name = "at_most"

    @number_required
    @one_number_arg_required
    def __call__(self, val, *args, **kwargs):
        return min(val, args[0])


class AtLeast(Filter):
    """Return `val` or `args[0]`, whichever is greater.

    Accepts an int, float or a string representations of an int or float.
    """

    __slots__ = ()

    name = "at_least"

    @number_required
    @one_number_arg_required
    def __call__(self, val, *args, **kwargs):
        return max(val, args[0])


class Ceil(Filter):
    """Return the ceiling of x as an Integral.

    Accepts an int, float or a string representations of an int or float.
    """

    __slots__ = ()

    name = "ceil"

    @no_args
    @number_required
    def __call__(self, val, *args, **kwargs):
        return math.ceil(val)


class DividedBy(Filter):
    """Divide `val` by `args[0]`."""

    __slots__ = ()

    name = "divided_by"

    @number_required
    @one_number_arg_required
    def __call__(self, val, *args, **kwargs):
        div = args[0]
        if isinstance(div, float):
            return val / div
        return val // div


class Floor(Filter):
    """Return the floor of x as an Integral.

    Accepts an int, float or a string representations of an int or float.
    """

    __slots__ = ()

    name = "floor"

    @no_args
    @number_required
    def __call__(self, val, *args, **kwargs):
        return math.floor(val)


class Minus(Filter):
    """Subtract one number from another."""

    __slots__ = ()

    name = "minus"

    @number_required
    @one_number_arg_required
    def __call__(self, val, *args, **kwargs):
        sub = args[0]
        if isinstance(val, float) and isinstance(sub, float):
            return float(D(str(val)) - D(str(sub)))
        return val - sub


class Plus(Filter):
    """Add one number to another."""

    __slots__ = ()

    name = "plus"

    @number_required
    @one_number_arg_required
    def __call__(self, val, *args, **kwargs):
        plus = args[0]
        if isinstance(val, float) and isinstance(plus, float):
            return float(D(str(val)) + D(str(plus)))
        return val + plus


class Round(Filter):
    """Round a number to a given precision in decimal digits."""

    __slots__ = ()

    name = "round"

    @number_required
    def __call__(self, val, *args, **kwargs):
        arg = maybe_one_arg(self.name, args, kwargs)

        if arg:
            ndigits = expect_integer(self.name, args[0])
            return round(val, ndigits=ndigits)
        return round(val)


class Times(Filter):
    """Multiply a value by an integer or float."""

    __slots__ = ()

    name = "times"

    @number_required
    @one_number_arg_required
    def __call__(self, val, *args, **kwargs):
        mul = args[0]
        if isinstance(val, float) and isinstance(mul, float):
            return float(D(str(val)) * D(str(mul)))
        return val * mul


class Modulo(Filter):
    """Divide a value by a number and returns the remainder."""

    __slots__ = ()

    name = "modulo"

    @number_required
    @one_number_arg_required
    def __call__(self, val, *args, **kwargs):
        div = args[0]
        if isinstance(val, float) and isinstance(div, float):
            return float(D(str(val)) % D(str(div)))
        return val % div
