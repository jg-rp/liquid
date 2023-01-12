"""Parse tree node and pseudo "tag" for output statements."""
from typing import List
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node

from liquid.context import Context
from liquid.expression import Expression
from liquid.parse import expect

from liquid.stream import TokenStream
from liquid.stringify import to_liquid_string
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_STATEMENT


class StatementNode(Node):
    """Parse tree node representing an output statement."""

    __slots__ = ("tok", "expression")

    force_output = True

    def __init__(self, tok: Token, expression: Expression):
        self.tok = tok
        self.expression = expression

    def __str__(self) -> str:
        return f"`{self.expression}`"

    def __repr__(self) -> str:  # pragma: no cover
        return f"StatementNode(tok={self.tok}, expression={self.expression!r})"

    # pylint: disable=useless-return
    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        val = self.expression.evaluate(context)
        buffer.write(to_liquid_string(val, context.autoescape))
        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        val = await self.expression.evaluate_async(context)
        buffer.write(to_liquid_string(val, context.autoescape))
        return None

    def children(self) -> List[ChildNode]:
        return [ChildNode(linenum=self.tok.linenum, expression=self.expression)]


class Statement(Tag):
    """Pseudo "tag" to register output statements with the environment."""

    name = TOKEN_STATEMENT
    block = False

    def parse(self, stream: TokenStream) -> StatementNode:
        tok = stream.current
        expect(stream, TOKEN_STATEMENT)
        return StatementNode(tok, self.env.parse_filtered_expression_value(tok.value))
