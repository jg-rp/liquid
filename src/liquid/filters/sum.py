from decimal import Decimal

from .._filter import FilterContext


def sum_(
    context: FilterContext, left: object, prop: object = None
) -> int | float | Decimal:
    if isinstance(left, (int, float, Decimal)):
        return left

    if context.is_nil(prop):
        return sum(context.to_numeric(obj, 0) for obj in context.input_array(left))

    return sum(
        context.to_numeric(context.get_item(obj, prop), 0)
        for obj in context.input_array(left)
    )
