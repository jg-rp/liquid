"""Parse tree node and Tag definition for the built-in "assign" tag."""

import re
import sys
from typing import TextIO

from liquid.token import Token, TOKEN_TAG, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.lex import tokenize_filtered_expression
from liquid.expression import AssignmentExpression
from liquid.exceptions import LiquidSyntaxError
from liquid.parse import expect, parse_filtered_expression

RE_ASSIGNMENT = re.compile(r"^(\w[a-zA-Z0-9_\-]*)\s*=\s*(.+)$")

TAG_ASSIGN = sys.intern("assign")


class AssignNode(ast.Node):
    __slots__ = ("tok", "expression")

    statement = False

    def __init__(self, tok: Token, expression: AssignmentExpression):
        self.tok = tok
        self.expression = expression

    def __str__(self) -> str:
        return f"var ({self.expression})"

    def render_to_output(self, context: Context, buffer: TextIO):
        self.expression.evaluate(context)


class AssignTag(Tag):

    name = TAG_ASSIGN
    block = False

    def parse(self, stream: TokenStream) -> AssignNode:

        expect(stream, TOKEN_TAG, value=TAG_ASSIGN)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)

        if match := RE_ASSIGNMENT.match(stream.current.value):
            name, expression = match.groups()
        else:
            raise LiquidSyntaxError(
                f'invalid assignment expression "{stream.current.value}"',
                linenum=stream.current.linenum,
            )

        expr_iter = tokenize_filtered_expression(expression)
        expr = parse_filtered_expression(TokenStream(expr_iter))
        return AssignNode(tok, AssignmentExpression(tok, name, expr))
