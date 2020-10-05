""""""
import sys
from typing import TextIO

from liquid.token import Token, TOKEN_TAG_NAME, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream
from liquid.parse import expect

TAG_INCREMENT = sys.intern("increment")


class IncrementNode(ast.Node):
    __slots__ = ("tok", "identifier")

    def __init__(self, tok: Token, identifier: str):
        self.tok = tok
        self.identifier = identifier

    def __str__(self) -> str:
        return f"{self.identifier} += 1"

    def render_to_output(self, context: Context, buffer: TextIO):
        buffer.write(str(context.increment(self.identifier)))


class IncrementTag(Tag):

    name = TAG_INCREMENT
    block = False

    def parse(self, stream: TokenStream) -> IncrementNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_INCREMENT)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)

        # The tag expression is assumed to be an unquoted identifier.
        # TODO: Validate identifier
        return IncrementNode(tok=tok, identifier=stream.current.value)
