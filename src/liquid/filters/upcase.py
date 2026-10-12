from .._filter import FilterContext


def upcase(context: FilterContext, left: object) -> str:
    return context.to_str(left, "").upper()
