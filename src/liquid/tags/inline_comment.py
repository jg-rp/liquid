from __future__ import annotations

import re
from typing import TYPE_CHECKING, TextIO

from ..exceptions import LiquidSyntaxError
from ..tokens import TOKEN_COMMENT, TOKEN_TAG_END, token_value

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token

RE_INVALID_INLINE_COMMENT = re.compile(r"\n\s*[^#\s]")


class InlineCommentTag:
    blank = True
    tag = "#"

    __slots__ = ("text", "token")

    def __init__(self, token: Token, text: str) -> None:
        self.token = token
        self.text = text

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        comment_token = parser.eat(TOKEN_COMMENT)
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        comment_text = token_value(comment_token, parser.source)

        if RE_INVALID_INLINE_COMMENT.search(comment_text):
            raise LiquidSyntaxError(
                "every line of an inline comment must start with a '#' character",
                token=comment_token,
                source=parser.source,
                name=parser.template_name,
            )

        return InlineCommentTag(token, comment_text)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        return None

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
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
