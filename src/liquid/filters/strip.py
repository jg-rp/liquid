from .._filter import FilterContext


def strip(context: FilterContext, left: object) -> str:
    return context.to_str(left, "").strip()


def lstrip(context: FilterContext, left: object) -> str:
    return context.to_str(left, "").lstrip()


def rstrip(context: FilterContext, left: object) -> str:
    return context.to_str(left, "").rstrip()
