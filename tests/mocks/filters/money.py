from liquid.filter import Filter, no_args, number_required

# pylint: disable=arguments-differ, too-few-public-methods


class MoneyWithCurrency(Filter):

    __slots__ = ()

    name = "money_with_currency"

    @no_args
    @number_required
    def __call__(self, money):
        return f"$ {money / 100.0:.2f} USD"


class Money(Filter):

    __slots__ = ()

    name = "money"

    @no_args
    @number_required
    def __call__(self, money):
        return f"$ {money / 100.0:.2f}"
