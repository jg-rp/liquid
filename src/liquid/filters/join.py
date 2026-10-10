from .._filter import FilterContext


def join(context: FilterContext, left: object, sep: object) -> str:
    left = context.input_array(left)
    sep = context.to_str(sep, " ")
    return sep.join(context.to_str(obj, "") for obj in left)
