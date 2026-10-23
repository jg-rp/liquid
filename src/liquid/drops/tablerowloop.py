from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from .._drop import AbstractDrop

if TYPE_CHECKING:
    from .._context import RenderContext


class TableRowLoop(AbstractDrop):
    """Table row helper variables."""

    __slots__ = (
        "col",
        "cols",
        "index",
        "length",
        "row",
    )

    def __init__(self, length: int, cols: int) -> None:
        self.length = length
        self.cols = cols

        self.col = 1
        self.index = 0
        self.row = 1

    def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
        return name in (
            "length",
            "index",
            "index0",
            "rindex",
            "rindex0",
            "first",
            "last",
            "col",
            "col0",
            "col_first",
            "col_last",
            "row",
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

        if name == "rindex":
            return self.length - self.index

        if name == "rindex0":
            return self.length - self.index - 1

        if name == "col":
            return self.col

        if name == "col_first":
            return self.col == 1

        if name == "col_last":
            return self.col == self.cols

        if name == "col0":
            return self.col - 1

        if name == "row":
            return self.row

        raise AttributeError

    def __getitem__(self, key: str) -> int:
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

        if key == "rindex":
            return self.length - self.index

        if key == "rindex0":
            return self.length - self.index - 1

        if key == "col":
            return self.col

        if key == "col_first":
            return self.col == 1

        if key == "col_last":
            return self.col == self.cols

        if key == "col0":
            return self.col - 1

        if key == "row":
            return self.row

        raise KeyError(key)

    def __len__(self) -> int:
        return 12

    def __iter__(self) -> Iterator[str]:
        return iter(
            (
                "length",
                "index",
                "index0",
                "rindex",
                "rindex0",
                "first",
                "last",
                "col",
                "col0",
                "col_first",
                "col_last",
                "row",
            )
        )

    def __bool__(self) -> bool:
        return True

    def step(self) -> None:
        self.index += 1

        if self.col == self.cols:
            self.col = 1
            self.row += 1
        else:
            self.col += 1
