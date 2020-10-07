"""Parse tree node and tag definition for the built in "echo" tag."""

import sys

from liquid.token import TOKEN_TAG, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.stream import TokenStream
from liquid.lex import tokenize_filtered_expression
from liquid.parse import parse_filtered_expression, expect
from liquid.builtin.statement import StatementNode

TAG_ECHO = sys.intern("echo")


class EchoNode(StatementNode):
    """Parse tree node representing an "echo" tag."""

    __slots__ = ("tok", "expression")

    def __repr__(self):  # pragma: no cover
        return f"EchoNode(tok={self.tok}, expression={self.expression!r})"


class EchoTag(Tag):
    """"""

    name = TAG_ECHO
    block = False

    def parse(self, stream: TokenStream) -> ast.Node:
        expect(stream, TOKEN_TAG, value=TAG_ECHO)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_filtered_expression(stream.current.value)

        expr = parse_filtered_expression(TokenStream(expr_iter))
        return EchoNode(tok, expression=expr)
