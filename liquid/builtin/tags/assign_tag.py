"""Tag and node definition for the built-in "assign" tag."""
import re
import sys

from typing import List
from typing import Optional
from typing import TextIO

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.expression import Expression
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.expression import AssignmentExpression
from liquid.exceptions import LiquidSyntaxError

from liquid.parse import expect
from liquid.expressions.common import ASSIGN_IDENTIFIER_PATTERN

RE_ASSIGNMENT = re.compile(rf"^({ASSIGN_IDENTIFIER_PATTERN})\s*=\s*(.+)$")

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
        return False

    async def render_to_output_async(
        self, context: Context, _: TextIO
    ) -> Optional[bool]:
        await self.expression.evaluate_async(context)
        return False

    def children(self) -> List[ChildNode]:
        return [
            ChildNode(
                linenum=self.tok.linenum,
                expression=self.expression,
                template_scope=[self.expression.name],
            )
        ]


class AssignTag(Tag):
    """The built-in cycle tag."""

    name = TAG_ASSIGN
    block = False

    def _parse_expression(self, value: str) -> Expression:
        return self.env.parse_filtered_expression_value(value)

    def parse(self, stream: TokenStream) -> AssignNode:
        expect(stream, TOKEN_TAG, value=TAG_ASSIGN)
        tok = stream.next_token()
        expect(stream, TOKEN_EXPRESSION)

        match = RE_ASSIGNMENT.match(stream.current.value)
        if match:
            name, right = match.groups()
        else:
            raise LiquidSyntaxError(
                f'invalid assignment expression "{stream.current.value}"',
                linenum=stream.current.linenum,
            )

        return AssignNode(
            tok, AssignmentExpression(name, self._parse_expression(right))
        )
