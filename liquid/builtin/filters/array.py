# type: ignore
"""Legacy, class-based implementations of filters that operate on arrays."""

from collections import OrderedDict

from operator import getitem

from typing import List
from typing import Any
from typing import Tuple

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup

from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError

from liquid.filter import Filter
from liquid.filter import expect_string
from liquid.filter import expect_array

from liquid import Undefined
from liquid import is_undefined

# pylint: disable=too-few-public-methods arguments-differ

# Send objects with missing keys to the end when sorting a list.
MAX_CH = chr(0x10FFFF)


class ArrayFilter(Filter):
    """Base class for built-in array filter functions."""

    __slots__ = ()

    name = "AbstractStringFilter"
    num_args: Tuple[int, ...] = (0,)
    msg = "{}: expected an array, found {}"

    def __call__(self, val, *args, **kwargs):
        if len(args) not in self.num_args:
            raise FilterArgumentError(
                f"{self.name}: expected {self.num_args} arguments, found {len(args)}"
            )

        # Do not allow array operations on strings or arbitrary iterables.
        if not isinstance(val, (list, tuple, Undefined)):
            raise FilterValueError(self.msg.format(self.name, type(val).__name__))

        try:
            return self.filter(val, *args)
        except (AttributeError, TypeError) as err:
            raise FilterArgumentError(
                self.msg.format(self.name, type(val).__name__)
            ) from err

    def filter(self, val, *args):
        """The filter's implementation."""
        raise NotImplementedError(":(")


def _str_if_not(val: object) -> str:
    if not isinstance(val, str):
        return str(val)
    return val


class Join(ArrayFilter):
    """Concatenate an array of strings."""

    __slots__ = ()

    name = "join"
    num_args = (0, 1)

    def filter(self, iterable, separator=" "):
        if not isinstance(separator, str):
            separator = str(separator)

        if self.env.autoescape and separator == " ":
            separator = Markup(" ")

        return separator.join(_str_if_not(item) for item in iterable)


class First(ArrayFilter):
    """Return the first item of an array"""

    __slots__ = ()

    name = "first"

    def filter(self, array):
        if array:
            return array[0]
        return None


class Last(ArrayFilter):
    """Return the last item of an array"""

    __slots__ = ()

    name = "last"

    def filter(self, array):
        if array:
            return array[-1]
        return None


class Concat(ArrayFilter):
    """Return two arrays joined together."""

    __slots__ = ()

    name = "concat"
    num_args = (1,)

    def filter(self, array, second_array):
        expect_array(self.name, second_array)
        if is_undefined(array):
            return second_array
        return array + second_array


def _getitem(sequence, key: str, default: Any = None) -> Any:
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


class Map(ArrayFilter):
    """Creates an array of values by extracting the values of a named property
    from another object."""

    __slots__ = ()

    name = "map"
    num_args = (1,)

    def filter(self, sequence, key):
        try:
            return [_getitem(itm, str(key)) for itm in sequence]
        except TypeError as err:
            raise FilterValueError(f"{self.name}: can't map sequence") from err


class Reverse(ArrayFilter):
    """Reverses the order of the items in an array."""

    __slots__ = ()

    name = "reverse"

    def filter(self, array):
        return list(reversed(array))


class Sort(ArrayFilter):
    """Sorts items in an array in case-sensitive order.

    When a key string is provided, objects without the key property should
    be at the end of the output list/array.
    """

    __slots__ = ()

    name = "sort"
    num_args = (0, 1)

    def filter(self, sequence, key=None):
        if key:
            expect_string(self.name, key)
            return list(sorted(sequence, key=lambda x: _getitem(x, key, MAX_CH)))

        try:
            return list(sorted(sequence))
        except TypeError as err:
            raise FilterValueError(f"{self.name}: can't sort sequence") from err


def _lower(val, default="") -> str:
    """Helper for the sort filter"""
    try:
        return val.lower()
    except AttributeError:
        return default


class SortNatural(ArrayFilter):
    """Sorts items in an array in case-insensitive order."""

    __slots__ = ()

    name = "sort_natural"
    num_args = (0, 1)

    def filter(self, sequence, key=None) -> List[Any]:
        if key:
            expect_string(self.name, key)
            return list(
                sorted(sequence, key=lambda x: _lower(_getitem(x, key, MAX_CH)))
            )

        return list(sorted(sequence, key=_lower))


class Where(ArrayFilter):
    """Creates an array including only the objects with a given property value,
    or any truthy value by default."""

    __slots__ = ()

    name = "where"
    num_args = (1, 2)

    def filter(self, sequence, attr, value=None):
        if value:
            return [itm for itm in sequence if _getitem(itm, attr) == value]

        return [itm for itm in sequence if _getitem(itm, attr) not in (False, None)]


class Uniq(ArrayFilter):
    """Removes any duplicate elements in an array. Input array order is not
    preserved."""

    __slots__ = ()

    name = "uniq"

    def filter(self, iterable):
        unique = OrderedDict.fromkeys(iterable)
        return list(unique.keys())


class Compact(ArrayFilter):
    """Removes any nil values from an array."""

    __slots__ = ()

    name = "compact"

    def filter(self, iterable):
        return [itm for itm in iterable if itm is not None]
