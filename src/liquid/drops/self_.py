from __future__ import annotations

from typing import TYPE_CHECKING

from .._nothing import NOTHING

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint


class Self:
    __slots__ = ("context",)

    def __init__(self, context: RenderContext) -> None:
        super().__init__()
        self.context = context

    def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
        # Argument context is not necessarily the same as instance context.
        return name in self.context.scope

    def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
        # Argument context is not necessarily the same as instance context.
        return self.context.resolve(name)

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "output" | "string":
                return str(self)
            case "object":
                return self
            case "array":
                return [self]
            case _:
                return NOTHING

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Self) and self.context is other.context

    def __str__(self) -> str:
        return "Liquid::SelfDrop"

    def __contains__(self, item: object) -> bool:
        return False
