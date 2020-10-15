"""Parse tree node and pseudo "tag" for output statements."""
from typing import TextIO


from liquid.ast import Node
from liquid.expression import Expression
from liquid.context import Context
from liquid.lex import tokenize_filtered_expression
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import parse_filtered_expression
from liquid.parse import expect

from liquid.token import Token
from liquid.token import TOKEN_STATEMENT


class StatementNode(Node):
    """Parse tree node representing an output statement."""

    __slots__ = ("tok", "expression")

    def __init__(self, tok: Token, expression: Expression):
        self.tok = tok
        self.expression = expression

    def __str__(self):
        return f"`{self.expression}`"

    def __repr__(self):  # pragma: no cover
        return f"StatementNode(tok={self.tok}, expression={self.expression!r})"

    def render_to_output(self, context: Context, buffer: TextIO):
        val = self.expression.evaluate(context)
        if isinstance(val, str):
            # shortcut for common case.
            pass
        elif isinstance(val, bool):
            val = str(val).lower()
        elif val is None:
            val = ""
        elif isinstance(val, (list, tuple)):
            val = "".join(str(v) for v in val)
        else:
            val = str(val)

        buffer.write(val)


class Statement(Tag):
    """Pseudo "tag" to register output statements with the environment."""

    name = TOKEN_STATEMENT

    def parse(self, stream: TokenStream) -> Node:
        tok = stream.current
        expect(stream, TOKEN_STATEMENT)

        expr_iter = tokenize_filtered_expression(tok.value)
        node = StatementNode(tok, parse_filtered_expression(TokenStream(expr_iter)))
        return node
