from .._filter import FilterContext


def capitalize(context: FilterContext, left: object) -> str:
    return context.to_str(left, "").capitalize()
