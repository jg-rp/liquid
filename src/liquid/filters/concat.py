from .._filter import FilterContext


def concat(context: FilterContext, left: object, right: object) -> list[object]:
    if not isinstance(right, (list, tuple)):
        raise context.error("concat requires an array argument")

    if context.is_nil(left):
        return right  # type: ignore

    return context.input_array(left) + right  # type: ignore
