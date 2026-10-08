from __future__ import annotations

from typing import TYPE_CHECKING

from .undefined import Undefined

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint


class Blank:
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string" | "data":
                return ""
            case "numeric":
                return 0
            case _:
                return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Blank, Empty)):
            return False

        if other is None or other == False or isinstance(other, Undefined):
            return True

        if isinstance(other, str):
            return other.isspace()

        if isinstance(other, (list, tuple, dict)):
            return not other

        return False

    def __str__(self) -> str:
        return ""


BLANK = Blank()


class Empty:
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string" | "data":
                return ""
            case "numeric":
                return 0
            case _:
                return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Empty):
            return True

        if other is None or isinstance(other, Blank):
            return False

        if isinstance(other, (list, tuple, dict, str)):
            return not other

        return False

    def __str__(self) -> str:
        return ""


EMPTY = Empty()
