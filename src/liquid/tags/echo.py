from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ..tokens import TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class EchoTag:
    blank = False
    tag = "echo"

    __slots__ = ("expression", "token")

    def __init__(self, token: Token, expression: Expression) -> None:
        self.token = token
        self.expression = expression

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        expr = parser.parse_filtered_expression()
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return EchoTag(token, expr)

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
