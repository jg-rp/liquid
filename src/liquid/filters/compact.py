from .._filter import FilterContext


def compact(context: FilterContext, left: object, prop: object = None) -> list[object]:
    if prop is None:
        return [item for item in context.input_array(left) if not context.is_nil(item)]

    result: list[object] = []

    for obj in context.input_array(left):
        val = context.get_item(obj, prop)

        if val == context.missing:
            raise context.error(f"can't read property {prop!r}")

        if not context.is_nil(val):
            result.append(val)

    return result
