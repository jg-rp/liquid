from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ..tokens import TOKEN_COMMENT, TOKEN_TAG_END, token_value

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class CommentTag:
    blank = True
    tag = "comment"

    __slots__ = ("text", "token")

    def __init__(self, token: Token, text: str) -> None:
        self.token = token
        self.text = text

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        comment = parser.eat(TOKEN_COMMENT)
        parser.eat_empty_tag("endcomment")
        return CommentTag(token, token_value(comment, parser.source))

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        return None

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        return None

    def children(self) -> list[Markup]:
        return []

    async def children_async(self) -> list[Markup]:
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
