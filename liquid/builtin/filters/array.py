"""Filter functions that operate on arrays."""

from collections import OrderedDict
from operator import getitem
from typing import List, Any

from liquid.filter import Filter
from liquid.filter import (
    one_maybe_two_args,
    expect_string,
    array_required,
    no_args,
    one_string_arg_required,
    one_array_arg_required,
    array_of_strings_required,
    array_of_hashable_required,
    maybe_one_arg_required,
    one_maybe_two_args_required,
)

# pylint: disable=arguments-differ, too-few-public-methods

# Send objects with missing keys to the end when sorting a list.
MAX_CH = chr(0x10FFFF)


class Join(Filter):
    """Concatenate an array of strings"""

    __slots__ = ()

    name = "join"

    @array_of_strings_required
    @one_string_arg_required
    def __call__(self, iterable, separator):
        return separator.join(iterable)


class First(Filter):
    """Return the first item of an array"""

    __slots__ = ()

    name = "first"

    @array_required
    @no_args
    def __call__(self, array):
        if array:
            return array[0]
        return None


class Last(Filter):
    """Return the last item of an array"""

    __slots__ = ()

    name = "last"

    @array_required
    @no_args
    def __call__(self, array):
        if array:
            return array[-1]
        return None


class Concat(Filter):
    """Return two arrays joined togather."""

    __slots__ = ()

    name = "concat"

    @array_required
    @one_array_arg_required
    def __call__(self, array, second_array):
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


class Map(Filter):
    """Creates an array of values by extracting the values of a named property
    from another object."""

    __slots__ = ()

    name = "map"

    @array_required
    @one_string_arg_required
    def __call__(self, sequence, key):
        return [_getitem(itm, key) for itm in sequence]


class Reverse(Filter):
    """Reverses the order of the items in an array."""

    __slots__ = ()

    name = "reverse"

    @array_required
    @no_args
    def __call__(self, array):
        return list(reversed(array))


class Sort(Filter):
    """Sorts items in an array in case-sensitive order.

    When a key string is provided, objects without the key property should
    be at the end of the output list/array.
    """

    __slots__ = ()

    name = "sort"

    @array_required
    @maybe_one_arg_required
    def __call__(self, sequence, key=None):
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


class SortNatural(Filter):
    """Sorts items in an array in case-insensitive order."""

    __slots__ = ()

    name = "sort_natural"

    @array_required
    @maybe_one_arg_required
    def __call__(self, sequence, key=None) -> List[Any]:
        if key:
            expect_string(self.name, key)
            return list(
                sorted(sequence, key=lambda x: _lower(_getitem(x, key, MAX_CH)))
            )

        return list(sorted(sequence, key=_lower))


class Where(Filter):
    """Creates an array including only the objects with a given property value,
    or any truthy value by default."""

    __slots__ = ()

    name = "where"

    @array_required
    @one_maybe_two_args_required
    def __call__(self, sequence, attr, value=None):
        expect_string(self.name, attr)

        if value:
            expect_string(self.name, value)
            return [itm for itm in sequence if _getitem(itm, attr) == value]

        return [itm for itm in sequence if _getitem(itm, attr) not in (False, None)]


class Uniq(Filter):
    """Removes any duplicate elements in an array. Input array order is not preserved."""

    __slots__ = ()

    name = "uniq"

    @array_of_hashable_required
    @no_args
    def __call__(self, iterable):
        unique = OrderedDict.fromkeys(iterable)
        return list(unique.keys())


class Compact(Filter):
    """Removes any nil values from an array."""

    __slots__ = ()

    name = "compact"

    @array_required
    @no_args
    def __call__(self, iterable):
        return [itm for itm in iterable if itm is not None]
