"""Tag and node definition for the built-in "unless" tag."""
from __future__ import annotations

import sys

from typing import Optional
from typing import TextIO
from typing import TYPE_CHECKING

from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.lex import tokenize_boolean_expression
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import get_parser
from liquid.parse import expect
from liquid.parse import parse_boolean_expression

from liquid.token import Token
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.expression import Expression

TAG_UNLESS = sys.intern("unless")
TAG_ENDUNLESS = sys.intern("endunless")

ENDUNLESSBLOCK = (TAG_ENDUNLESS, TOKEN_EOF)


class UnlessNode(Node):
    """Parse tree node for the built-in "unless" tag."""

    __slots__ = ("tok", "condition", "consequence")

    def __init__(self, tok: Token, condition: Expression, consequence: BlockNode):
        self.tok = tok
        self.condition = condition
        self.consequence = consequence

    def __str__(self) -> str:
        return f"if !{self.condition} {{ {self.consequence} }}"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        if not self.condition.evaluate(context):
            self.consequence.render(context, buffer)
        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        if not await self.condition.evaluate_async(context):
            await self.consequence.render_async(context, buffer)
        return None


class UnlessTag(Tag):
    """The built-in "unless" tag."""

    name = TAG_UNLESS
    end = TAG_ENDUNLESS

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse_expression(self, stream: TokenStream) -> Expression:
        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_boolean_expression(stream.current.value)
        return parse_boolean_expression(TokenStream(expr_iter))

    def parse(self, stream: TokenStream) -> UnlessNode:

        expect(stream, TOKEN_TAG, value=TAG_UNLESS)
        tok = stream.current
        stream.next_token()

        expr = self.parse_expression(stream)
        stream.next_token()

        consequence = self.parser.parse_block(stream, ENDUNLESSBLOCK)

        expect(stream, TOKEN_TAG, value=TAG_ENDUNLESS)
        return UnlessNode(tok, condition=expr, consequence=consequence)
