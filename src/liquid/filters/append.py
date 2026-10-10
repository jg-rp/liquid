from .._filter import FilterContext


def append(context: FilterContext, left: object, right: object) -> str:
    left = context.to_str(left, "")
    right = context.to_str(right, "")
    return left + right
