from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._drop import ContextHint


class Nothing:
    def __str__(self) -> str:
        return ""

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string":
                return ""
            case "data":
                return None
            case "numeric":
                return 0
            case "boolean":
                return False
            case "array":
                return []


NOTHING = Nothing()
