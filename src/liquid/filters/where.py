from .._filter import FilterContext


def where(
    context: FilterContext, left: object, prop: object, value: object = None
) -> list[object]:
    left = context.input_array(left)

    if context.is_nil(prop):
        return []

    def _filter(obj: object) -> bool:
        return context.truthy(context.get_item(obj, prop))

    if context.is_nil(value):
        return list(filter(_filter, left))

    return [obj for obj in left if context.get_item(obj, prop) == value]
