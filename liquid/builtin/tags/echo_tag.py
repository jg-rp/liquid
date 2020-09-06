"""Parse tree node and tag definition for the built in "echo" tag."""

import sys

from liquid.token import TOKEN_TAG_NAME, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.lex import TokenStream, get_expression_lexer
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

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> ast.Node:
        expect(stream, TOKEN_TAG_NAME, value=TAG_ECHO)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = get_expression_lexer(self.env).tokenize(stream.current.value)

        expr = parse_filtered_expression(expr_iter)
        return EchoNode(tok, expression=expr)
