from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ..tokens import TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class IncrementTag:
    blank = False
    tag = "increment"

    __slots__ = ("name", "token")

    def __init__(self, token: Token, name: Name) -> None:
        self.token = token
        self.name = name

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        name = parser.parse_identifier()
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return IncrementTag(token, name)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        buffer.write(str(context.increment(self.name.value)))

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        buffer.write(str(context.increment(self.name.value)))

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return []

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return [self.name]

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []
