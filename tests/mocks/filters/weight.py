from liquid.filter import math_filter


@math_filter
def weight(grams):
    return f"{grams / 1000:.2f}"


@math_filter
def weight_with_unit(grams):
    return f"{grams / 1000:.2f} kg"
