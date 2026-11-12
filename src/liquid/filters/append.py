from .._filter import FilterContext


def append(context: FilterContext, left: object, right: object) -> str:
    return context.to_str(left, "") + context.to_str(right, "")
