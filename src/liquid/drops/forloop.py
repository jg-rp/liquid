from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING

from .._nothing import NOTHING

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint


class ForLoop(Mapping[str, object]):
    __slots__ = ("index", "length", "name", "parent_loop")

    def __init__(self, name: str, length: int, parent_loop: ForLoop | None) -> None:
        self.name = name
        self.length = length
        self.parent_loop = parent_loop or NOTHING
        self.index = -1

    def __getitem__(self, key: str) -> object:
        if key == "first":
            return self.index == 0

        if key == "index":
            return self.index + 1

        if key == "index0":
            return self.index

        if key == "last":
            return self.index == self.length - 1

        if key == "length":
            return self.length

        if key == "name":
            return self.name

        if key == "parentloop":
            return self.parent_loop

        if key == "rindex":
            return self.length - self.index

        if key == "rindex0":
            return self.length - self.index - 1

        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(
            (
                "name",
                "length",
                "index",
                "index0",
                "rindex",
                "rindex0",
                "first",
                "last",
                "parentloop",
            )
        )

    def __len__(self) -> int:
        return 9

    def step(self) -> None:
        self.index += 1

    def __str__(self) -> str:
        return "Liquid::ForLoopDrop"

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string" | "data":
                return str(self)
            case _:
                return NOTHING
