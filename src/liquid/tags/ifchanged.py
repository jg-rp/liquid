from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from .._markup import render_block, render_block_async
from ..tokens import TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class IfChangedTag:
    blank = False
    tag = "ifchanged"

    __slots__ = ("block", "token")

    def __init__(self, token: Token, block: Block) -> None:
        self.token = token
        self.block = block

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        block = parser.parse_block(end=("endcapture",))
        parser.eat_empty_tag("endifchanged")
        return IfChangedTag(token, block)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        buf = context.env.buffer_factory()
        render_block(self.block, context, buf)
        buffered = buf.getvalue()

        if buffered != context.get_register("ifchanged", str):
            buffer.write(buffered)
            context.registers["ifchanged"] = buffered

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        buf = context.env.buffer_factory()
        await render_block_async(self.block, context, buf)
        buffered = buf.getvalue()

        if buffered != context.get_register("ifchanged", str):
            buffer.write(buffered)
            context.registers["ifchanged"] = buffered

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
