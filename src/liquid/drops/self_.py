from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._context import RenderContext


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

    def __eq__(self, other: object) -> bool:
        print("**", other.__class__.__name__)
        if isinstance(other, Self):
            print("!!!", id(self.context) == id(other.context))
        return isinstance(other, Self) and self.context is other.context

    def __str__(self) -> str:
        return "Liquid::SelfDrop"

    def __contains__(self, item: object) -> bool:
        return False
