"""Filter functions that operate on arrays."""
from __future__ import annotations

from collections import OrderedDict
from functools import partial
from operator import getitem

from typing import Any
from typing import Iterable
from typing import List
from typing import Sequence
from typing import Tuple
from typing import TypeVar
from typing import TYPE_CHECKING

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from liquid.filter import with_environment
from liquid.filter import array_filter

from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError

from liquid import is_undefined

if TYPE_CHECKING:
    from liquid import Environment

ArrayT = TypeVar("ArrayT", List[Any], Tuple[Any, ...])

# Send objects with missing keys to the end when sorting a list.
MAX_CH = chr(0x10FFFF)


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
    """Helper for the sort filter"""
    try:
        return str(obj.lower())
    except AttributeError:
        return ""


@with_environment
@array_filter
def join(
    iterable: Iterable[object], separator: object = " ", *, environment: Environment
) -> str:
    """Concatenate an array of strings."""
    if not isinstance(separator, str):
        separator = str(separator)

    if environment.autoescape and separator == " ":
        separator = Markup(" ")

    return separator.join(_str_if_not(item) for item in iterable)


@array_filter
def first(array: Sequence[Any]) -> object:
    """Return the first item of an array"""
    if array:
        return array[0]
    return None


@array_filter
def last(array: Sequence[Any]) -> object:
    """Return the last item of an array"""
    if array:
        return array[-1]
    return None


@array_filter
def concat(array: ArrayT, second_array: ArrayT) -> ArrayT:
    """Return two arrays joined together."""
    if not isinstance(second_array, (list, tuple)):
        raise FilterArgumentError(
            f"concat expected an array, found {type(second_array).__name__}"
        )

    if is_undefined(array):
        return second_array
    return array + second_array


@array_filter
def map_(sequence: ArrayT, key: object) -> List[object]:
    """Creates an array of values by extracting the values of a named property
    from another object."""
    try:
        return [_getitem(itm, str(key)) for itm in sequence]
    except TypeError as err:
        raise FilterValueError("can't map sequence") from err


@array_filter
def reverse(array: ArrayT) -> List[object]:
    """Reverses the order of the items in an array."""
    return list(reversed(array))


@array_filter
def sort(sequence: ArrayT, key: object = None) -> List[object]:
    """Sorts items in an array in case-sensitive order.

    When a key string is provided, objects without the key property should
    be at the end of the output list/array.
    """
    if key:
        key_func = partial(_getitem, key=str(key), default=MAX_CH)
        return list(sorted(sequence, key=key_func))

    try:
        return list(sorted(sequence))
    except TypeError as err:
        raise FilterValueError("can't sort sequence") from err


@array_filter
def sort_natural(sequence: ArrayT, key: object = None) -> List[object]:
    """Sorts items in an array in case-insensitive order."""
    if key:
        item_getter = partial(_getitem, key=str(key), default=MAX_CH)
        return list(sorted(sequence, key=lambda obj: _lower(item_getter(obj))))

    return list(sorted(sequence, key=_lower))


@array_filter
def where(sequence: ArrayT, attr: object, value: object = None) -> List[object]:
    """Creates an array including only the objects with a given property value,
    or any truthy value by default."""
    if value:
        return [itm for itm in sequence if _getitem(itm, attr) == value]

    return [itm for itm in sequence if _getitem(itm, attr) not in (False, None)]


@array_filter
def uniq(iterable: ArrayT) -> List[object]:
    """Removes any duplicate elements in an array. Input array order is not
    preserved."""
    unique = OrderedDict.fromkeys(iterable)
    return list(unique.keys())


@array_filter
def compact(iterable: ArrayT) -> List[object]:
    """Removes any nil values from an array."""
    return [itm for itm in iterable if itm is not None]
