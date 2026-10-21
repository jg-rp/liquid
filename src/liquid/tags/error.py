from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import LiquidSyntaxError

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._io import StringBuffer
    from .._markup import Expression, Markup, Partial
    from ..expressions import Name
    from ..tokens import Token


class ErrorNode:
    blank = True
    tag = ""

    __slots__ = ("err", "token")

    def __init__(self, token: Token, err: LiquidSyntaxError) -> None:
        self.token = token
        self.err = err

    def __str__(self) -> str:
        return self.err.detailed_message()

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        return None

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        return None

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return []

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []
