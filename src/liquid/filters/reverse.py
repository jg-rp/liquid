from .._filter import FilterContext


def reverse(context: FilterContext, left: object) -> list[object]:
    return list(reversed(context.input_array(left)))
