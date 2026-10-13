from functools import cmp_to_key
from typing import Literal

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
