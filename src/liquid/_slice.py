from collections.abc import Iterator, Sequence

from .exceptions import LiquidValueError


def slice_sequence[T](
    seq: Sequence[T], offset: int, limit: int | None, reversed_: bool = False
) -> tuple[Iterator[T], int]:
    if limit is not None and limit <= 0:
        return iter(()), 0

    start = max(0, offset)
    end = len(seq) if limit is None else max(0, offset + limit)
    indices = range(start, min(len(seq), end))
    length = len(indices)

    if reversed_:
        indices = reversed(indices)

    def it_() -> Iterator[T]:
        for i in indices:
            yield seq[i]

    return it_(), length


def slice_range(
    it: range, offset: int, limit: int | None, reversed_: bool = False
) -> range:
    if limit is not None and limit <= 0:
        return range(0)

    stop_inclusive = it.stop + (1 if it.step > 0 else -1)
    full_range = range(it.start, stop_inclusive, it.step)

    start = max(0, offset)

    try:
        end = len(full_range) if limit is None else max(0, offset + limit)
    except OverflowError:
        raise LiquidValueError("range literal length limit reached")

    sliced = full_range[start:end]
    return sliced[::-1] if reversed_ else sliced
