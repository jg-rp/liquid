from .._filter import FilterContext


def prepend(context: FilterContext, left: object, right: object) -> str:
    left = context.to_str(left, "")
    right = context.to_str(right, "")
    return right + left
