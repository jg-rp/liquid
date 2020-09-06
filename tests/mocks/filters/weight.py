from liquid.filter import Filter, number_required, no_args

# pylint: disable=arguments-differ, too-few-public-methods


class Weight(Filter):

    __slots__ = ()

    name = "weight"

    @number_required
    @no_args
    def __call__(self, grams):
        return f"{grams / 1000:.2f}"


class WeightWithUnit(Filter):

    __slots__ = ()

    name = "weight_with_unit"

    @number_required
    @no_args
    def __call__(self, grams):
        return f"{grams / 1000:.2f} kg"
