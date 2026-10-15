from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .._drop import Drop
from .._nothing import NOTHING
from .._slice import slice_range
from .iterable import IterableDrop

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint


class Range(Drop):
    __slots__ = ("start", "stop")

    def __init__(self, start: int, stop: int) -> None:
        self.start = start
        self.stop = stop

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Range)
            and self.start == other.start
            and self.stop == other.stop
        )

    def __len__(self):
        return 0 if self.stop < self.start else self.stop - self.start + 1

    def __getitem__(self, key: str | int) -> int:
        match key:
            case "first":
                return self.start
            case "last":
                return self.stop
            case "size":
                return len(self)
            case _:
                raise KeyError

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start, self.stop + 1))

    def __contains__(self, item: object) -> bool:
        return isinstance(item, int) and item >= self.start and item <= self.stop

    def __bool__(self) -> bool:
        return len(self) > 0

    def __str__(self) -> str:
        return f"{self.start}..{self.stop}"

    def __liquid_iter__(
        self, offset: int, limit: int | None, reversed_: bool
    ) -> IterableDrop[int]:
        it = slice_range(range(self.start, self.stop), offset, limit, reversed_)
        return IterableDrop(it, len(it))

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string":
                return str(self)
            case "data":
                return self
            case "boolean":
                return len(self) > 0
            case _:
                return NOTHING
