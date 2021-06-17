"""Tag and node definition for the built-in "echo" tag."""

import sys


from liquid.ast import Node
from liquid.builtin.statement import StatementNode
from liquid.lex import tokenize_filtered_expression

from liquid.parse import parse_filtered_expression
from liquid.parse import expect

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

TAG_ECHO = sys.intern("echo")


class EchoNode(StatementNode):
    """Parse tree node for the built-in "echo" tag."""

    __slots__ = ("tok", "expression")

    def __repr__(self) -> str:  # pragma: no cover
        return f"EchoNode(tok={self.tok}, expression={self.expression!r})"


class EchoTag(Tag):
    """The built-in "echo" tag."""

    name = TAG_ECHO
    block = False

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_ECHO)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_filtered_expression(stream.current.value)

        expr = parse_filtered_expression(TokenStream(expr_iter))
        return EchoNode(tok, expression=expr)
