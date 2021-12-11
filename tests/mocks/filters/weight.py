"""Mock filter functions for displaying values as weights."""
# pylint: disable=missing-function-docstring
from liquid.filter import math_filter


@math_filter
def weight(grams):
    return f"{grams / 1000:.2f}"


@math_filter
def weight_with_unit(grams):
    return f"{grams / 1000:.2f} kg"
