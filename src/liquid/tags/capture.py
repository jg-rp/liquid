from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from .._markup import render_block, render_block_async
from ..exceptions import LiquidSyntaxError
from ..tokens import TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class CaptureTag:
    blank = True
    tag = "capture"

    __slots__ = ("block", "name", "token")

    def __init__(self, token: Token, name: Name, block: Block) -> None:
        self.token = token
        self.name = name
        self.block = block

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

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        block = parser.parse_block(end=("endcapture",))
        parser.eat_empty_tag("endcapture")
        return CaptureTag(token, name, block)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        buf = context.env.buffer_factory()
        render_block(self.block, context, buf)
        # TODO: HTML safe
        context.assign(self.name.value, buf.getvalue())

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        buf = context.env.buffer_factory()
        await render_block_async(self.block, context, buf)
        # TODO: HTML safe
        context.assign(self.name.value, buf.getvalue())

    def children(self) -> list[Markup]:
        return [node for node in self.block if not isinstance(node, str)]

    async def children_async(self) -> list[Markup]:
        return self.children()

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
