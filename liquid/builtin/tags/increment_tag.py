"""Tag and node definition for the built-in "increment" tag."""

import sys
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.context import RenderContext
from liquid.expressions.common import parse_unchained_identifier
from liquid.expressions.filtered.lex import tokenize
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG
from liquid.token import Token

# ruff: noqa: D102

TAG_INCREMENT = sys.intern("increment")


class IncrementNode(Node):
    """Parse tree node for the built-in "increment" tag."""

    __slots__ = ("tok", "identifier")

    def __init__(self, tok: Token, identifier: str):
        self.tok = tok
        self.identifier = identifier

    def __str__(self) -> str:
        return f"{self.identifier} += 1"

    def render_to_output(
        self, context: RenderContext, buffer: TextIO
    ) -> Optional[bool]:
        buffer.write(str(context.increment(self.identifier)))
        return True

    def children(self) -> list[ChildNode]:
        return [ChildNode(linenum=self.tok.linenum, template_scope=[self.identifier])]


class IncrementTag(Tag):
    """The built-in "increment" tag."""

    name = TAG_INCREMENT
    block = False
    node_class = IncrementNode

    def parse(self, stream: TokenStream) -> IncrementNode:
        stream.expect(TOKEN_TAG, value=TAG_INCREMENT)
        tok = stream.current
        stream.next_token()
        stream.expect(TOKEN_EXPRESSION)
        return self.node_class(
            tok=tok,
            identifier=str(
                parse_unchained_identifier(
                    TokenStream(tokenize(stream.current.value, stream.current.linenum))
                )
            ),
        )
