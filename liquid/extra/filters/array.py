"""Extra array filters."""
from typing import Sequence
from liquid.filter import array_filter


@array_filter
def index(left: Sequence[object], obj: object) -> object:
    """Return the zero-based index of an item in an array, or None if
    the items is not in the array.
    """
    try:
        return left.index(obj)
    except ValueError:
        return None
