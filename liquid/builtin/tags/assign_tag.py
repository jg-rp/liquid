"""Tag and node definition for the built-in "assign" tag."""

import re
import sys

from typing import Optional
from typing import TextIO

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

from liquid.ast import Node
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.lex import tokenize_filtered_expression
from liquid.expression import AssignmentExpression
from liquid.exceptions import LiquidSyntaxError
from liquid.parse import expect, parse_filtered_expression

RE_ASSIGNMENT = re.compile(r"^(\w[a-zA-Z0-9_\-]*)\s*=\s*(.+)$")

TAG_ASSIGN = sys.intern("assign")


class AssignNode(Node):
    """Parse tree node for the built-in "assign" tag."""

    __slots__ = ("tok", "expression")

    def __init__(self, tok: Token, expression: AssignmentExpression):
        self.tok = tok
        self.expression = expression

    def __str__(self) -> str:
        return f"var ({self.expression})"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        self.expression.evaluate(context)
        return None

    async def render_to_output_async(
        self, context: Context, _: TextIO
    ) -> Optional[bool]:
        await self.expression.evaluate_async(context)
        return None


class AssignTag(Tag):
    """The built-in cycle tag."""

    name = TAG_ASSIGN
    block = False

    def parse(self, stream: TokenStream) -> AssignNode:

        expect(stream, TOKEN_TAG, value=TAG_ASSIGN)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)

        match = RE_ASSIGNMENT.match(stream.current.value)
        if match:
            name, expression = match.groups()
        else:
            raise LiquidSyntaxError(
                f'invalid assignment expression "{stream.current.value}"',
                linenum=stream.current.linenum,
            )

        expr_iter = tokenize_filtered_expression(expression)
        expr = parse_filtered_expression(TokenStream(expr_iter))
        return AssignNode(tok, AssignmentExpression(name, expr))
