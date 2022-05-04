"""Tag and node definition for the built-in "decrement" tag."""

import sys

from typing import List
from typing import TextIO
from typing import Optional

from liquid import ast
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.parse import expect

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

from liquid.expressions import TokenStream as ExprTokenStream
from liquid.expressions.common import parse_unchained_identifier
from liquid.expressions.filtered.lex import tokenize

TAG_DECREMENT = sys.intern("decrement")


class DecrementNode(ast.Node):
    """Parse tree node for the built-in "decrement" tag."""

    __slots__ = ("tok", "identifier")

    def __init__(self, tok: Token, identifier: str):
        self.tok = tok
        self.identifier = identifier

    def __str__(self) -> str:
        return f"{self.identifier} -= 1"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        buffer.write(str(context.decrement(self.identifier)))
        return True

    def children(self) -> List[ast.ChildNode]:
        return [
            ast.ChildNode(
                linenum=self.tok.linenum,
                template_scope=[self.identifier],
            )
        ]


class DecrementTag(Tag):
    """The built-in "decrement" tag."""

    name = TAG_DECREMENT
    block = False

    def parse(self, stream: TokenStream) -> DecrementNode:
        expect(stream, TOKEN_TAG, value=TAG_DECREMENT)
        tok = stream.current
        stream.next_token()
        expect(stream, TOKEN_EXPRESSION)
        return DecrementNode(
            tok=tok,
            identifier=str(
                parse_unchained_identifier(
                    ExprTokenStream(tokenize(stream.current.value))
                )
            ),
        )
