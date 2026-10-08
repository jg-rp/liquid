from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from .._markup import is_blank_block, render_block, render_block_async
from ..tokens import (
    TOKEN_TAG_END,
    TOKEN_TAG_NAME,
    TOKEN_TAG_START,
)
from .else_ import ElseBlock

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class IfTag:
    tag = "if"

    __slots__ = ("blank", "blocks", "token")

    def __init__(
        self, token: Token, blocks: list[IfBlock | ElsIfBlock | ElseBlock]
    ) -> None:
        self.token = token
        self.blocks = blocks
        self.blank = all(block.blank for block in self.blocks)

        if self.blank:
            for block in self.blocks:
                block.filter_strings()

    @classmethod
    def parse(cls, token: Token, parser: Parser) -> Markup:
        blocks: list[IfBlock | ElsIfBlock | ElseBlock] = []

        parser.expect_expression()
        expression = parser.parse_expression(infix=True)
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        block = parser.parse_block(("else", "elsif", "endif"))
        blocks.append(IfBlock(token, expression, block))

        while 1:
            tag_name = parser.tags(("else", "elsif"))

            if tag_name == "elsif":
                blocks.append(cls.parse_else_if(parser))
            elif tag_name == "else":
                name_token = parser.eat_tag("else")
                blocks.append(
                    ElseBlock(
                        name_token, parser.parse_block(("else", "elsif", "endif"))
                    )
                )
            else:
                break

        parser.eat_empty_tag("endif")
        return IfTag(token, blocks)

    @classmethod
    def parse_else_if(cls, parser: Parser) -> ElsIfBlock:
        parser.eat(TOKEN_TAG_START)
        parser.skip_whitespace_control()
        token = parser.eat(TOKEN_TAG_NAME)
        parser.expect_expression()
        expression = parser.parse_expression(infix=True)
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return ElsIfBlock(
            token, expression, parser.parse_block(("else", "elsif", "endif"))
        )

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        for block in self.blocks:
            if context.env.truthy(block.expression.evaluate(context), context):
                block.render(context, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        for block in self.blocks:
            if context.env.truthy(
                await block.expression.evaluate_async(context), context
            ):
                await block.render_async(context, buffer)

    def children(self) -> list[Markup]:
        return list(self.blocks)

    async def children_async(self) -> list[Markup]:
        return self.children()

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


class IfBlock:
    tag = "if"

    __slots__ = ("blank", "block", "expression", "token")

    def __init__(self, token: Token, expression: Expression, block: Block) -> None:
        self.token = token
        self.expression = expression
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
        return [self.expression]

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


class ElsIfBlock(IfBlock):
    tag = "elsif"
