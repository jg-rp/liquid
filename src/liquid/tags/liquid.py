from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from .._markup import is_blank_block, render_block, render_block_async
from ..tokens import TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class LiquidTag:
    tag = "liquid"

    __slots__ = ("blank", "block", "token")

    def __init__(self, token: Token, block: Block) -> None:
        self.token = token
        self.block = block
        self.blank = is_blank_block(block)

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        block = parser.parse_line_statements()
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return LiquidTag(token, block)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        render_block(self.block, context, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        await render_block_async(self.block, context, buffer)

    def children(self) -> list[Markup]:
        return [node for node in self.block if not isinstance(node, str)]

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
