"""Parse tree node and pseudo "tag" for output statements."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterable
from typing import TextIO

from liquid.ast import Node
from liquid.builtin.expressions import FilteredExpression
from liquid.builtin.expressions import tokenize
from liquid.stream import TokenStream
from liquid.stringify import to_liquid_string
from liquid.tag import Tag
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_OUTPUT
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression


class OutputNode(Node):
    """Parse tree node representing an output statement."""

    __slots__ = ("expression",)

    def __init__(self, token: Token, expression: Expression):
        super().__init__(token)
        self.expression = expression
        self.blank = False

    def __str__(self) -> str:
        return f"{{{{ {self.expression} }}}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        return buffer.write(
            to_liquid_string(self.expression.evaluate(context), context.autoescape)
        )

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        return buffer.write(
            to_liquid_string(
                await self.expression.evaluate_async(context), context.autoescape
            )
        )

    def expressions(self) -> Iterable[Expression]:
        """Return this node's children."""
        yield self.expression


class Output(Tag):
    """Pseudo "tag" to register output statements with the environment."""

    name = TOKEN_OUTPUT
    block = False
    node_class = OutputNode

    def parse(self, stream: TokenStream) -> OutputNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_OUTPUT)
        expr_token = stream.expect(TOKEN_EXPRESSION)
        return self.node_class(
            token,
            FilteredExpression.parse(
                self.env, TokenStream(tokenize(expr_token.value, expr_token))
            ),
        )
