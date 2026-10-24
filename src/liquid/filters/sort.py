import math
import re
from decimal import Decimal
from functools import cmp_to_key
from operator import getitem
from typing import Any, Literal

from .._filter import FilterContext


def sort(context: FilterContext, left: object, key: object = None) -> list[object]:
    left = context.input_array(left)

    def compare(a: object, b: object) -> Literal[-1, 0, 1]:
        nil_a = context.is_nil(a)
        nil_b = context.is_nil(b)

        if nil_a and nil_b:
            return 0

        if nil_a and not nil_b:
            return 1

        if not nil_a and nil_b:
            return -1

        try:
            if a < b:  # type: ignore
                return -1
            elif a > b:  # type: ignore
                return 1
            else:
                return 0
        except TypeError:
            raise context.error(
                f"comparison with {type(a).__class__!r} and {type(b).__class__!r} failed"
            )

    if context.is_nil(key):
        return sorted(context.input_array(left), key=cmp_to_key(compare))

    return sorted(
        context.input_array(left),
        key=cmp_to_key(
            lambda a, b: compare(
                context.get_item(a, key, None), context.get_item(b, key, None)
            )
        ),
    )


def sort_natural(
    context: FilterContext, left: object, key: object = None
) -> list[object]:
    left = context.input_array(left)

    def compare(a: object, b: object) -> Literal[-1, 0, 1]:
        nil_a = context.is_nil(a)
        nil_b = context.is_nil(b)

        if nil_a and nil_b:
            return 0

        if nil_a and not nil_b:
            return 1

        if not nil_a and nil_b:
            return -1

        a = context.to_str(a, "").lower()
        b = context.to_str(b, "").lower()

        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    if context.is_nil(key):
        return sorted(context.input_array(left), key=cmp_to_key(compare))

    return sorted(
        context.input_array(left),
        key=cmp_to_key(
            lambda a, b: compare(
                context.get_item(a, key, None), context.get_item(b, key, None)
            )
        ),
    )


RE_NUMERIC = re.compile(r"-?\d+")


def sort_numeric(
    context: FilterContext, left: object, key: object = None
) -> list[object]:
    left = context.input_array(left)

    def compare(a: object, b: object) -> Literal[-1, 0, 1]:
        a = _ints(a)
        b = _ints(b)

        try:
            if a < b:
                return -1
            elif a > b:
                return 1
            else:
                return 0
        except TypeError:
            raise context.error(
                f"comparison with {type(a).__class__!r} and {type(b).__class__!r} failed"
            )

    if context.is_nil(key):
        return sorted(context.input_array(left), key=cmp_to_key(compare))

    return sorted(
        context.input_array(left),
        key=cmp_to_key(
            lambda a, b: compare(_getitem(a, key, None), _getitem(b, key, None))
        ),
    )


def _getitem(sequence: Any, key: object, default: object = None) -> Any:
    try:
        return getitem(sequence, key)
    except (KeyError, IndexError, TypeError):
        return default


def _ints(obj: object) -> tuple[int | float | Decimal, ...]:
    if isinstance(obj, bool):
        return (math.inf,)
    if isinstance(obj, (int, float, Decimal)):
        return (obj,)

    ints = tuple(int(n) for n in RE_NUMERIC.findall(str(obj)))

    if not ints:
        return (math.inf,)
    return ints
