from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ..tokens import TOKEN_TAG_END, TOKEN_TEXT, token_value

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class RawTag:
    blank = False
    tag = "raw"

    __slots__ = ("text", "token")

    def __init__(self, token: Token, text: str) -> None:
        self.token = token
        self.text = text

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        text = parser.eat(TOKEN_TEXT)
        parser.eat_empty_tag("endraw")
        return RawTag(token, token_value(text, parser.source))

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        buffer.write(self.text)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        buffer.write(self.text)

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
