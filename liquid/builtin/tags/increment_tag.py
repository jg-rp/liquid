"""Tag and node definition for the built-in "increment" tag."""

import sys

from typing import Optional
from typing import TextIO

from liquid.ast import Node
from liquid.context import Context
from liquid.lex import tokenize_identifier
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import expect
from liquid.parse import parse_unchained_identifier

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

TAG_INCREMENT = sys.intern("increment")


class IncrementNode(Node):
    """Parse tree node for the built-in "increment" tag."""

    __slots__ = ("tok", "identifier")

    def __init__(self, tok: Token, identifier: str):
        self.tok = tok
        self.identifier = identifier

    def __str__(self) -> str:
        return f"{self.identifier} += 1"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        buffer.write(str(context.increment(self.identifier)))
        return None


class IncrementTag(Tag):
    """The built-in "increment" tag."""

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
