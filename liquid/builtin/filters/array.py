"""Filter functions that operate on arrays."""

from collections import OrderedDict
from collections import abc
from operator import getitem
from typing import List, Any

from liquid.exceptions import FilterArgumentError
from liquid.filter import Filter
from liquid.filter import (
    expect_string,
    array_of_hashable_required,
)

# pylint: disable=arguments-differ, too-few-public-methods

# Send objects with missing keys to the end when sorting a list.
MAX_CH = chr(0x10FFFF)


class ArrayFilter(Filter):

    name = "AbstractStringFilter"
    num_args = (0,)
    msg = "{}: expected an array, found {}"

    def __call__(self, val, *args):
        if len(args) not in self.num_args:
            raise FilterArgumentError(
                f"{self.name}: expected {self.num_args} arguments, found {len(args)}"
            )

        if not isinstance(val, abc.Sequence):
            raise FilterArgumentError(self.msg.format(self.name, type(val)))

        try:
            return self.filter(val, *args)
        except (AttributeError, TypeError) as err:
            raise FilterArgumentError(self.msg.format(self.name, type(val))) from err

    def filter(self, val, *args):
        raise NotImplementedError(":(")


class Join(ArrayFilter):
    """Concatenate an array of strings"""

    __slots__ = ()

    name = "join"
    num_args = (1,)

    def filter(self, iterable, separator):
        return str(separator).join(iterable)


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
    """Return two arrays joined togather."""

    __slots__ = ()

    name = "concat"
    num_args = (1,)

    def filter(self, array, second_array):
        return array + second_array


def _getitem(sequence, key: str, default: Any = None) -> Any:
    """Helper for the map filter.

    Same as sequence[key], but returns a default value if key does not exist
    in sequence.
    """
    try:
        return getitem(sequence, key)
    except (KeyError, IndexError, TypeError):
        return default


class Map(ArrayFilter):
    """Creates an array of values by extracting the values of a named property
    from another object."""

    __slots__ = ()

    name = "map"
    num_args = (1,)

    def filter(self, sequence, key):
        return [_getitem(itm, str(key)) for itm in sequence]


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

        return list(sorted(sequence))


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
        expect_string(self.name, attr)

        if value:
            expect_string(self.name, value)
            return [itm for itm in sequence if _getitem(itm, attr) == value]

        return [itm for itm in sequence if _getitem(itm, attr) not in (False, None)]


class Uniq(ArrayFilter):
    """Removes any duplicate elements in an array. Input array order is not preserved."""

    __slots__ = ()

    name = "uniq"

    @array_of_hashable_required
    def filter(self, iterable):
        unique = OrderedDict.fromkeys(iterable)
        return list(unique.keys())


class Compact(ArrayFilter):
    """Removes any nil values from an array."""

    __slots__ = ()

    name = "compact"

    def filter(self, iterable):
        return [itm for itm in iterable if itm is not None]
