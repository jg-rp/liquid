"""Filter functions that operate on arrays."""
from __future__ import annotations

from decimal import Decimal
from functools import partial
from itertools import chain
from itertools import islice
from operator import getitem
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import List
from typing import Sequence
from typing import Tuple
from typing import Union

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterError
from liquid.expression import NIL
from liquid.filter import array_filter
from liquid.filter import decimal_arg
from liquid.filter import liquid_filter
from liquid.filter import sequence_filter
from liquid.filter import with_environment
from liquid.undefined import is_undefined

if TYPE_CHECKING:
    from liquid import Environment

ArrayT = Union[List[Any], Tuple[Any, ...]]
"""Array-like objects."""

# Send objects with missing keys to the end when sorting a list.
MAX_CH = chr(0x10FFFF)

# Unique object for use with the uniq filter.
MISSING = object()


def _str_if_not(val: object) -> str:
    if not isinstance(val, str):
        return str(val)
    return val


def _getitem(sequence: Any, key: object, default: object = None) -> Any:
    """Helper for the map filter.

    Same as sequence[key], but returns a default value if key does not exist
    in sequence.
    """
    try:
        return getitem(sequence, key)
    except (KeyError, IndexError):
        return default
    except TypeError:
        if not hasattr(sequence, "__getitem__"):
            raise
        return default


def _lower(obj: Any) -> str:
    """Helper for the sort filter."""
    try:
        return str(obj).lower()
    except AttributeError:
        return ""


@with_environment
@sequence_filter
def join(
    sequence: Iterable[object],
    separator: object = " ",
    *,
    environment: Environment,
) -> str:
    """Return a string by joining items in _sequence_, separated by _separator_."""
    if not isinstance(separator, str):
        separator = str(separator)

    if environment.autoescape and separator == " ":
        separator = Markup(" ")

    return separator.join(_str_if_not(item) for item in sequence)


@liquid_filter
def first(obj: Any) -> object:
    """Return the first item of collection _obj_."""
    if isinstance(obj, str):
        return None

    if isinstance(obj, dict):
        obj = list(islice(obj.items(), 1))

    try:
        return getitem(obj, 0)
    except (TypeError, KeyError, IndexError):
        return None


@liquid_filter
def last(obj: Sequence[Any]) -> object:
    """Return the last item of array-like object _obj_."""
    if isinstance(obj, str):
        return None

    try:
        return getitem(obj, -1)
    except (TypeError, KeyError, IndexError):
        return None


@sequence_filter
def concat(sequence: ArrayT, second_array: ArrayT) -> ArrayT:
    """Return the concatenation of _sequence_ and _second_array_."""
    if not isinstance(second_array, (list, tuple)):
        raise FilterArgumentError(
            f"concat expected an array, found {type(second_array).__name__}"
        )

    if is_undefined(sequence):
        return second_array

    return list(chain(sequence, second_array))


@sequence_filter
def map_(sequence: ArrayT, key: object) -> List[object]:
    """Return an array/list of items in _sequence_ selected by _key_."""
    try:
        return [_getitem(itm, str(key), default=NIL) for itm in sequence]
    except TypeError as err:
        raise FilterError("can't map sequence") from err


@array_filter
def reverse(array: ArrayT) -> List[object]:
    """Reverses the order of the items in an array."""
    return list(reversed(array))


@array_filter
def sort(sequence: ArrayT, key: object = None) -> List[object]:
    """Return a copy of _sequence_ in ascending order.

    When a key string is provided, objects without the key property will
    be at the end of the output list/array.
    """
    if key:
        key_func = partial(_getitem, key=str(key), default=MAX_CH)
        return sorted(sequence, key=key_func)

    try:
        return sorted(sequence)
    except TypeError as err:
        raise FilterError("can't sort sequence") from err


@array_filter
def sort_natural(sequence: ArrayT, key: object = None) -> List[object]:
    """Return a copy of _sequence_ in ascending order, with case-insensitive comparison.

    When a key string is provided, objects without the key property will
    be at the end of the output list/array.
    """
    if key:
        item_getter = partial(_getitem, key=str(key), default=MAX_CH)
        return sorted(sequence, key=lambda obj: _lower(item_getter(obj)))

    return sorted(sequence, key=_lower)


@sequence_filter
def where(sequence: ArrayT, attr: object, value: object = None) -> List[object]:
    """Return a list of items from _sequence_ where _attr_ equals _value_."""
    if value is not None and not is_undefined(value):
        return [itm for itm in sequence if _getitem(itm, attr) == value]

    return [itm for itm in sequence if _getitem(itm, attr) not in (False, None)]


@sequence_filter
def uniq(sequence: ArrayT, key: object = None) -> List[object]:
    """Return a copy of _sequence_ with duplicate elements removed."""
    # Note that we're not using a dict or set for deduplication because we need
    # to handle sequences containing unhashable objects, like dictionaries.

    # This is probably quite slow.
    if key is not None:
        keys = []
        result = []
        for obj in sequence:
            try:
                item = obj[key]
            except KeyError:
                item = MISSING
            except TypeError as err:
                raise FilterArgumentError(
                    f"can't read property '{key}' of {obj}"
                ) from err

            if item not in keys:
                keys.append(item)
                result.append(obj)

        return result

    return [obj for i, obj in enumerate(sequence) if sequence.index(obj) == i]


@sequence_filter
def compact(sequence: ArrayT, key: object = None) -> List[object]:
    """Return a copy of _sequence_ with any nil values removed."""
    if key is not None:
        try:
            return [itm for itm in sequence if itm[key] is not None]
        except TypeError as err:
            raise FilterArgumentError(f"can't read property '{key}'") from err
    return [itm for itm in sequence if itm is not None]


@sequence_filter
def sum_(sequence: ArrayT, key: object = None) -> Union[float, int, Decimal]:
    """Return the sum of all numeric elements in _sequence_.

    If _key_ is given, it is assumed that sequence items are mapping-like,
    and the values at _item[key]_ will be summed instead.
    """
    if key is not None and not is_undefined(key):
        rv = sum(decimal_arg(_getitem(elem, key, 0), 0) for elem in sequence)
    else:
        rv = sum(decimal_arg(elem, 0) for elem in sequence)
    if isinstance(rv, Decimal):
        return float(rv)
    return rv
