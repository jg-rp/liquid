""""""
import sys
from typing import TextIO

from liquid.token import Token, TOKEN_TAG, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.lex import tokenize_identifier
from liquid.parse import expect, parse_unchained_identifier

TAG_DECREMENT = sys.intern("decrement")


class DecrementNode(ast.Node):
    __slots__ = ("tok", "identifier")

    def __init__(self, tok: Token, identifier: str):
        self.tok = tok
        self.identifier = identifier

    def __str__(self) -> str:
        return f"{self.identifier} -= 1"

    def render_to_output(self, context: Context, buffer: TextIO):
        buffer.write(str(context.decrement(self.identifier)))


class DecrementTag(Tag):
    """

    Increment and decrement tags share a namespace.
    """

    name = TAG_DECREMENT
    block = False

    def parse(self, stream: TokenStream) -> DecrementNode:
        expect(stream, TOKEN_TAG, value=TAG_DECREMENT)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        tokens = TokenStream(tokenize_identifier(stream.current.value))
        ident = parse_unchained_identifier(tokens)

        return DecrementNode(tok=tok, identifier=str(ident))
