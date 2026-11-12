from .._filter import FilterContext


def uniq(context: FilterContext, left: object, prop: object = None) -> list[object]:
    left = context.input_array(left)

    if context.is_nil(prop):
        return [obj for i, obj in enumerate(left) if left.index(obj) == i]

    keys = [context.get_item(obj, prop) for obj in left]
    return [left[i] for i, key in enumerate(keys) if keys.index(key) == i]
