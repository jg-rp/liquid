from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .._drop import AbstractDrop
from .._nothing import NOTHING

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint


class ForLoop(AbstractDrop):
    __slots__ = ("index", "length", "name", "parent_loop")

    def __init__(self, name: str, length: int, parent_loop: ForLoop | None) -> None:
        self.name = name
        self.length = length
        self.parent_loop = parent_loop or NOTHING
        self.index = -1

    def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
        return name in (
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

    def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
        if name == "first":
            return self.index == 0

        if name == "index":
            return self.index + 1

        if name == "index0":
            return self.index

        if name == "last":
            return self.index == self.length - 1

        if name == "length":
            return self.length

        if name == "name":
            return self.name

        if name == "parentloop":
            return self.parent_loop

        if name == "rindex":
            return self.length - self.index

        if name == "rindex0":
            return self.length - self.index - 1

        raise AttributeError

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

    def __bool__(self) -> bool:
        return True

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string" | "data":
                return str(self)
            case _:
                return NOTHING
