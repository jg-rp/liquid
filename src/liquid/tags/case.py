from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, TextIO

from .._markup import is_blank_block, render_block, render_block_async
from ..tokens import (
    TOKEN_COMMA,
    TOKEN_OR,
    TOKEN_TAG_END,
    TOKEN_TAG_NAME,
    TOKEN_TAG_START,
    TOKEN_TEXT,
)
from .else_ import ElseBlock

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class CaseTag:
    tag = "case"

    __slots__ = ("blank", "blocks", "expression", "token")

    def __init__(
        self,
        token: Token,
        expression: Expression,
        blocks: Sequence[WhenBlock | ElseBlock],
    ) -> None:
        self.token = token
        self.expression = expression
        self.blocks = blocks

        self.blank = all(block.blank for block in blocks)

        if self.blank:
            # Discard blank strings from all blocks.
            for block in blocks:
                block.filter_strings()

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        parser.expect_expression()
        expression = parser.parse_expression()
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        if parser.kind() == TOKEN_TEXT:
            # Junk between `{% case %}` and first `{% when %}`.
            parser.eat(TOKEN_TEXT)

        blocks: list[WhenBlock | ElseBlock] = []

        while 1:
            tag_name = parser.tags(("when", "else"))

            if tag_name == "when":
                blocks.append(CaseTag.parse_when(parser))
            elif tag_name == "else":
                name_token = parser.eat_tag("else")
                blocks.append(
                    ElseBlock(
                        name_token, parser.parse_block(("endcase", "when", "else"))
                    )
                )
            else:
                break

        parser.eat_empty_tag("endcase")
        return CaseTag(token, expression, blocks)

    @staticmethod
    def parse_when(parser: Parser) -> WhenBlock:
        parser.eat(TOKEN_TAG_START)
        parser.skip_whitespace_control()
        token = parser.eat(TOKEN_TAG_NAME)

        if parser.kind() == TOKEN_COMMA:
            parser.next()

        right: list[Expression] = []

        while 1:
            right.append(parser.parse_expression())

            if parser.kind() not in (TOKEN_COMMA, TOKEN_OR):
                break

            parser.next()

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        block = parser.parse_block(("endcase", "when", "else"))
        return WhenBlock(token, right, block)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        left = self.expression.evaluate(context)
        alt = True

        # NOTE: This does not stop at the first truthy expression, nor does it stop
        # at the first `else` block.

        for block in self.blocks:
            if isinstance(block, ElseBlock):
                if alt:
                    block.render(context, buffer)
                continue

            for expr in block.right:
                if context.env.eq(left, expr.evaluate(context), context, expr.span):
                    alt = False
                    block.render(context, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        left = await self.expression.evaluate_async(context)
        alt = True

        # NOTE: This does not stop at the first truthy expression, nor does it stop
        # at the first `else` block.

        for block in self.blocks:
            if isinstance(block, ElseBlock):
                if alt:
                    await block.render_async(context, buffer)
                continue

            for expr in block.right:
                if context.env.eq(
                    left, await expr.evaluate_async(context), context, expr.span
                ):
                    alt = False
                    await block.render_async(context, buffer)

    def children(self) -> list[Markup]:
        return list(self.blocks)

    async def children_async(self) -> list[Markup]:
        return self.children()

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


class WhenBlock:
    tag = "when"

    def __init__(self, token: Token, right: list[Expression], block: Block) -> None:
        self.token = token
        self.right = right
        self.block = block
        self.blank = is_blank_block(block)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        render_block(self.block, context, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        await render_block_async(self.block, context, buffer)

    def children(self) -> list[Markup]:
        return [node for node in self.block if not isinstance(node, str)]

    async def children_async(self) -> list[Markup]:
        return self.children()

    def expressions(self) -> list[Expression]:
        return self.right

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
