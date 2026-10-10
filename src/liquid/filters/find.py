from .._filter import FilterContext


def find(
    context: FilterContext, left: object, prop: object, value: object = None
) -> object:
    left = context.input_array(left)

    if context.is_nil(value):
        for obj in left:
            val = context.get_item(obj, prop)
            if not context.is_nil(val) and not val is False:
                return obj

    for obj in left:
        if context.get_item(obj, prop) == value:
            return obj

    return None


def find_index(
    context: FilterContext, left: object, prop: object, value: object = None
) -> int | None:
    left = context.input_array(left)

    if context.is_nil(value):
        for i, obj in enumerate(left):
            val = context.get_item(obj, prop)
            if not context.is_nil(val) and not val is False:
                return i

    for i, obj in enumerate(left):
        if context.get_item(obj, prop) == value:
            return i

    return None


def has(
    context: FilterContext, left: object, prop: object, value: object = None
) -> bool:
    left = context.input_array(left)

    if context.is_nil(value):
        for obj in left:
            val = context.get_item(obj, prop)
            if not context.is_nil(val) and not val is False:
                return True

    for obj in left:
        if context.get_item(obj, prop) == value:
            return True

    return False
