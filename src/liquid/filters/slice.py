from decimal import Decimal

from .._filter import FilterContext

MAX_SLICE_ARG: int = (2**53) - 1
MIN_SLICE_ARG: int = -(2**53) + 1


def slice_(
    context: FilterContext, left: object, offset: object, length: object
) -> str | list[object]:
    if not isinstance(left, (list, tuple, str)):
        left = context.to_str(left, "")

    offset = _clamp(_to_integer(context, offset))
    length = 1 if context.is_nil(length) else _clamp(_to_integer(context, length))

    start = len(left) + offset if offset < 0 else offset  # type: ignore
    return [] if length < 1 else left[start : start + length]  # type: ignore


def _clamp(i: int) -> int:
    return max(min(i, MAX_SLICE_ARG), MIN_SLICE_ARG)


def _to_integer(context: FilterContext, obj: object) -> int:
    if isinstance(obj, int):
        return obj

    if isinstance(obj, (float, Decimal)) and "." not in str(obj):
        return int(obj)

    if context.is_nil(obj):
        raise context.error("invalid integer")

    try:
        return int(context.to_str(obj, "").lstrip())
    except ValueError:
        raise context.error("invalid integer")
