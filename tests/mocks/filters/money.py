from liquid.filter import math_filter


@math_filter
def money_with_currency(money):
    return f"$ {money / 100.0:.2f} USD"


@math_filter
def money_(money):
    return f"$ {money / 100.0:.2f}"
