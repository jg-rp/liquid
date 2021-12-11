"""Parse tree node and pseudo "tag" for output statements."""
from typing import Any
from typing import Optional
from typing import TextIO

try:
    from markupsafe import escape
    from markupsafe import Markup
    from markupsafe import soft_str
except ImportError:
    from liquid.exceptions import escape  # type: ignore
    from liquid.exceptions import Markup  # type: ignore

    # pylint: disable=invalid-name
    soft_str = str  # type: ignore

from liquid.ast import Node
from liquid.context import Context
from liquid.expression import Expression
from liquid.lex import tokenize_filtered_expression

from liquid.parse import parse_filtered_expression
from liquid.parse import expect

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_STATEMENT


class StatementNode(Node):
    """Parse tree node representing an output statement."""

    __slots__ = ("tok", "expression")

    def __init__(self, tok: Token, expression: Expression):
        self.tok = tok
        self.expression = expression

    def __str__(self) -> str:
        return f"`{self.expression}`"

    def __repr__(self) -> str:  # pragma: no cover
        return f"StatementNode(tok={self.tok}, expression={self.expression!r})"

    # pylint: disable=no-self-use
    def _to_liquid_string(self, val: Any, autoescape: bool) -> str:
        if isinstance(val, str) or (autoescape and hasattr(val, "__html__")):
            pass
        elif isinstance(val, bool):
            val = str(val).lower()
        elif val is None:
            val = ""
        elif isinstance(val, list):
            if autoescape:
                val = Markup("").join(soft_str(itm) for itm in val)
            else:
                val = "".join(soft_str(itm) for itm in val)
        elif isinstance(val, range):
            val = f"{val.start}..{val.stop - 1}"
        else:
            val = str(val)

        if autoescape:
            val = escape(val)

        assert isinstance(val, str)
        return val

    # pylint: disable=useless-return
    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        val = self.expression.evaluate(context)
        buffer.write(self._to_liquid_string(val, context.autoescape))
        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        val = await self.expression.evaluate_async(context)
        buffer.write(self._to_liquid_string(val, context.autoescape))
        return None


class Statement(Tag):
    """Pseudo "tag" to register output statements with the environment."""

    name = TOKEN_STATEMENT

    def parse(self, stream: TokenStream) -> StatementNode:
        tok = stream.current
        expect(stream, TOKEN_STATEMENT)

        expr_iter = tokenize_filtered_expression(tok.value)
        node = StatementNode(tok, parse_filtered_expression(TokenStream(expr_iter)))
        return node
