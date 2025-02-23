"""Tag and node definition for the built-in "assign" tag."""

import re
import sys
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.context import RenderContext
from liquid.exceptions import LiquidSyntaxError
from liquid.expression import Expression
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG
from liquid.token import Token

# ruff: noqa: D102

# TODO:
RE_ASSIGNMENT = re.compile(rf"^(TODO)\s*=\s*(.+)$")

TAG_ASSIGN = sys.intern("assign")


class AssignNode(Node):
    """Parse tree node for the built-in "assign" tag."""

    __slots__ = ("tok", "expression")

    def __init__(self, tok: Token, expression: Expression):
        self.tok = tok
        self.expression = expression

    def __str__(self) -> str:
        return f"var ({self.expression})"

    def render_to_output(self, context: RenderContext, _: TextIO) -> Optional[bool]:
        self.expression.evaluate(context)
        return False

    async def render_to_output_async(
        self, context: RenderContext, _: TextIO
    ) -> Optional[bool]:
        await self.expression.evaluate_async(context)
        return False

    def children(self) -> list[ChildNode]:
        return [
            ChildNode(
                linenum=self.tok.start_index,
                expression=self.expression,
                template_scope=[self.expression.name],
            )
        ]


class AssignTag(Tag):
    """The built-in cycle tag."""

    name = TAG_ASSIGN
    block = False
    node_class = AssignNode

    def _parse_expression(self, value: str, parent_token: Token) -> Expression:
        return self.env.parse_filtered_expression_value(value, linenum)

    def parse(self, stream: TokenStream) -> AssignNode:
        stream.expect(TOKEN_TAG, value=TAG_ASSIGN)
        tok = stream.next_token()
        stream.expect(TOKEN_EXPRESSION)

        match = RE_ASSIGNMENT.match(stream.current.value)
        if match:
            name, right = match.groups()
        else:
            raise LiquidSyntaxError(
                f'invalid assignment expression "{stream.current.value}"',
                token=stream.current,
            )

        return self.node_class(
            tok,
            AssignmentExpression(
                name,
                self._parse_expression(right, stream.current),
            ),
        )
