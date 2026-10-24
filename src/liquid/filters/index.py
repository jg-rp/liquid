from .._filter import FilterContext


def index(context: FilterContext, left: object, obj: object) -> object:
    """Return the zero-based index of an array item.

    `None` is returned if `obj` is not in `left`.
    """
    try:
        return context.input_array(left).index(obj)
    except ValueError:
        return None
