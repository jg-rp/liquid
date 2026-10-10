from .._filter import FilterContext


def lstrip(context: FilterContext, left: object) -> str:
    return context.to_str(left, "").lstrip()
