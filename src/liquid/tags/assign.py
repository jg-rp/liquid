from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ..exceptions import LiquidSyntaxError
from ..tokens import TOKEN_ASSIGN, TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class AssignTag:
    blank = True
    tag = "assign"

    __slots__ = ("expression", "name", "token")

    def __init__(self, token: Token, name: Name, expression: Expression) -> None:
        self.token = token
        self.name = name
        self.expression = expression

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        name = parser.parse_identifier()

        if name.value.endswith("?"):
            raise LiquidSyntaxError(
                "invalid variable name",
                token=name.span,
                source=parser.source,
                name=parser.template_name,
            )

        parser.eat(TOKEN_ASSIGN)
        expression = parser.parse_filtered_expression()
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return AssignTag(token, name, expression)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        context.assign(self.name.value, self.expression.evaluate(context))

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        context.assign(self.name.value, await self.expression.evaluate_async(context))

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return [self.expression]

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return [self.name]

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []
