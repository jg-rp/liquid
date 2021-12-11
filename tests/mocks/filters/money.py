"""Mock currency filters."""
from liquid.filter import math_filter


@math_filter
def money_with_currency(money):
    """A filter function that returns a number formatted with currency info."""
    return f"$ {money / 100.0:.2f} USD"


@math_filter
def money_(money):
    """A filter function that returns a number formatted as money."""
    return f"$ {money / 100.0:.2f}"
