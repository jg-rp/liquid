"""Tag and node definition for the built-in "liquid" tag."""

import sys

from typing import List
from typing import Optional
from typing import TextIO
from typing import TYPE_CHECKING

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.lex import get_liquid_expression_lexer

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF


if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment

TAG_LIQUID = sys.intern("liquid")


class LiquidNode(Node):
    """Parse tree node for the built-in "liquid" tag."""

    __slots__ = ("tok", "block")

    def __init__(self, tok: Token, block: BlockNode):
        self.tok = tok
        self.block = block

    def __str__(self) -> str:
        return str(self.block)

    def __repr__(self) -> str:  # pragma: no cover
        return f"LiquidNode(tok={self.tok}, block={self.block!r})"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        return self.block.render(context, buffer)

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        return await self.block.render_async(context, buffer)

    def children(self) -> List[ChildNode]:
        return self.block.children()


class LiquidTag(Tag):
    """The built-in "liquid" tag."""

    name = TAG_LIQUID
    block = False

    def __init__(self, env: "Environment"):
        super().__init__(env)
        self.tokenize_liquid_expression = get_liquid_expression_lexer(
            comment_start_string=env.comment_start_string
        )

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_LIQUID)
        tok = stream.current
        stream.next_token()

        if stream.current.type == TOKEN_EOF:
            # Empty liquid tag. Empty block.
            block = BlockNode(tok, [])
        else:
            expect(stream, TOKEN_EXPRESSION)
            expr_stream = TokenStream(
                self.tokenize_liquid_expression(
                    stream.current.value, line_count=stream.current.linenum
                )
            )
            parser = get_parser(self.env)
            block = parser.parse_block(expr_stream, end=())

        return LiquidNode(tok, block=block)
