from .._filter import FilterContext


def prepend(context: FilterContext, left: object, right: object) -> str:
    return context.to_str(right, "") + context.to_str(left, "")
