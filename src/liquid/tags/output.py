from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from ..expressions import Name
    from ..tokens import Token


class OutputStatement:
    blank = False
    tag = ""

    __slots__ = ("expression", "token")

    def __init__(self, token: Token, expression: Expression) -> None:
        self.token = token
        self.expression = expression

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        buffer.write(
            context.env.serialize(
                self.expression.evaluate(context), context, self.expression.span
            )
        )

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        buffer.write(
            context.env.serialize(
                await self.expression.evaluate_async(context),
                context,
                self.expression.span,
            )
        )

    def children(self) -> list[Markup]:
        return []

    async def children_async(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return [self.expression]

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []
