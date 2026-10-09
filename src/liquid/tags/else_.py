from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from .._markup import is_blank_block, render_block, render_block_async
from ..expressions import BooleanLiteral

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from ..expressions import Name
    from ..tokens import Token


class ElseBlock:
    tag = "else"

    __slots__ = ("blank", "block", "expression", "token")

    def __init__(self, token: Token, block: Block) -> None:
        self.token = token
        self.block = block
        self.blank = is_blank_block(self.block)
        self.expression = BooleanLiteral(token, True)

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

    def filter_strings(self) -> None:
        markup: Block = [node for node in self.block if not isinstance(node, str)]
        self.block = markup
