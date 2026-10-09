from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ..tokens import (
    TOKEN_TAG_END,
    TOKEN_TAG_NAME,
    TOKEN_TAG_START,
)
from .else_ import ElseBlock
from .if_ import ElsIfBlock, IfBlock

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class UnlessTag:
    tag = ""

    __slots__ = ("blank", "blocks", "token")

    def __init__(
        self, token: Token, blocks: list[UnlessBlock | ElsIfBlock | ElseBlock]
    ) -> None:
        self.token = token
        self.blocks = blocks
        self.blank = all(block.blank for block in self.blocks)

        if self.blank:
            for block in self.blocks:
                block.filter_strings()

    @classmethod
    def parse(cls, token: Token, parser: Parser) -> Markup:
        blocks: list[UnlessBlock | ElsIfBlock | ElseBlock] = []

        parser.expect_expression()
        expression = parser.parse_expression(infix=True)
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        block = parser.parse_block(("else", "elsif", "endunless"))
        blocks.append(UnlessBlock(token, expression, block))

        while 1:
            tag_name = parser.tags(("else", "elsif"))

            if tag_name == "elsif":
                blocks.append(cls.parse_else_if(parser))
            elif tag_name == "else":
                name_token = parser.eat_tag("else")
                blocks.append(
                    ElseBlock(
                        name_token, parser.parse_block(("else", "elsif", "endunless"))
                    )
                )
            else:
                break

        parser.eat_empty_tag("endunless")
        return UnlessTag(token, blocks)

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
            token, expression, parser.parse_block(("else", "elsif", "endunless"))
        )

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        for block in self.blocks:
            if isinstance(block, UnlessBlock):
                if not context.env.truthy(block.expression.evaluate(context), context):
                    return block.render(context, buffer)
            elif context.env.truthy(block.expression.evaluate(context), context):
                return block.render(context, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        for block in self.blocks:
            if isinstance(block, UnlessBlock):
                if not context.env.truthy(
                    await block.expression.evaluate_async(context), context
                ):
                    return await block.render_async(context, buffer)
            elif context.env.truthy(
                await block.expression.evaluate_async(context), context
            ):
                return await block.render_async(context, buffer)

    def children(self) -> list[Markup]:
        return list(self.blocks)

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


class UnlessBlock(IfBlock):
    tag = "unless"
