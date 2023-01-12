"""Extra array filters."""
import math
import re

from decimal import Decimal
from operator import getitem

from typing import Any
from typing import List
from typing import Sequence
from typing import Tuple
from typing import Union

from liquid.filter import array_filter
from liquid.filter import sequence_filter

from liquid.limits import to_int


@array_filter
def index(left: Sequence[object], obj: object) -> object:
    """Return the zero-based index of an item in an array, or None if
    the items is not in the array.
    """
    try:
        return left.index(obj)
    except ValueError:
        return None


RE_NUMERIC = re.compile(r"-?\d+")


@sequence_filter
def sort_numeric(left: Sequence[object], key: object = None) -> List[object]:
    """Return a copy of the input sequence sorted by any numeric values found in
    the sequence's items."""
    if key:
        _key = str(key)
        return sorted(left, key=lambda item: _ints(_getitem(item, _key)))
    return sorted(left, key=_ints)


def _getitem(sequence: Any, key: object, default: object = None) -> Any:
    """Item getter for the ``sort_numeric`` filter."""
    try:
        return getitem(sequence, key)
    except (KeyError, IndexError, TypeError):
        return default


def _ints(obj: object) -> Tuple[Union[int, float, Decimal], ...]:
    """Key function for the ``sort_numeric`` filter."""
    if isinstance(obj, bool):
        # isinstance(False, int) == True
        return (math.inf,)
    if isinstance(obj, (int, float, Decimal)):
        return (obj,)

    ints = tuple(to_int(n) for n in RE_NUMERIC.findall(str(obj)))

    if not ints:
        return (math.inf,)
    return ints
