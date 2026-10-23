from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .._drop import AbstractDrop
from .._nothing import NOTHING
from .._slice import slice_range
from .iterable import IterableDrop

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint


class Range(AbstractDrop):
    __slots__ = ("start", "stop")

    def __init__(self, start: int, stop: int) -> None:
        self.start = start
        self.stop = stop

    def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
        match name:
            case "first":
                return self.start
            case "last":
                return self.stop
            case "size":
                return len(self)
            case _:
                raise KeyError

    def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
        return name in ("first", "last", "size")

    def __liquid_iter__(
        self, offset: int, limit: int | None, reversed_: bool
    ) -> IterableDrop[int]:
        it = slice_range(range(self.start, self.stop), offset, limit, reversed_)
        return IterableDrop(it, len(it))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Range)
            and self.start == other.start
            and self.stop == other.stop
        )

    def __len__(self) -> int:
        return 0 if self.stop < self.start else self.stop - self.start + 1

    def __bool__(self) -> bool:
        return len(self) > 0

    def __str__(self) -> str:
        return f"{self.start}..{self.stop}"

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

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start, self.stop + 1))
