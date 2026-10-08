from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING

from .._nothing import NOTHING
from .iterable import IterableDrop

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint


class Range(Mapping[str | int, int]):
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
        return iter(self.__liquid_iter__(0, None, False))

    def __str__(self) -> str:
        return f"({self.start}..{self.stop})"

    def __liquid_iter__(
        self, start: int, end: int | None, reversed_: bool
    ) -> IterableDrop[int]:
        if end is not None:
            end = min(end, end)
        else:
            end = self.stop

        if reversed_:
            it = range(0) if start > end else range(end, start - 1)
        else:
            it = range(0) if start > end else range(start, end + 1)

        return IterableDrop(it, len(it))

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string":
                return str(self)
            case "data":
                # TODO: limit
                return list(self.__liquid_iter__(0, None, False))
            case "boolean":
                return len(self) > 0
            case _:
                return NOTHING
