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
        expect(stream, TOKEN_TAG, value=TAG_INCREMENT)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        tokens = TokenStream(tokenize_identifier(stream.current.value))
        ident = parse_unchained_identifier(tokens)

        return IncrementNode(tok=tok, identifier=str(ident))
