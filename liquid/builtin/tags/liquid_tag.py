"""Parse tree node and tag definition for the built in "echo" tag."""

import sys
from typing import TextIO

from liquid.token import Token, TOKEN_TAG_NAME, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream, get_liquid_lexer
from liquid.parse import expect, get_parser

TAG_LIQUID = sys.intern("liquid")


class LiquidNode(ast.Node):
    """Parse tree node representing a "liquid" tag."""

    __slots__ = ("tok", "block")

    def __init__(self, tok: Token, block: ast.BlockNode):
        self.tok = tok
        self.block = block

    def __str__(self):
        return str(self.block)

    def __repr__(self):  # pragma: no cover
        return f"LiquidNode(tok={self.tok}, block={self.block!r})"

    def render_to_output(self, context: Context, buffer: TextIO):
        return self.block.render(context, buffer)


class LiquidTag(Tag):
    """"""

    name = TAG_LIQUID

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> ast.Node:
        expect(stream, TOKEN_TAG_NAME, value=TAG_LIQUID)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = get_liquid_lexer(self.env).tokenize(stream.current.value)

        parser = get_parser(self.env)
        block = parser.parse_block(expr_stream, end=())
        return LiquidNode(tok, block=block)
