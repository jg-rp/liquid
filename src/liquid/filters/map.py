from .._filter import FilterContext


def map_(context: FilterContext, left: object, prop: object) -> list[object]:
    return [context.get_item(obj, prop) for obj in context.input_array(left)]
