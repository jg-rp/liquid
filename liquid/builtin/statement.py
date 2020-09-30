"""Parse tree node and pseudo "tag" for output statements."""
from typing import TextIO

from liquid.token import Token, TOKEN_STATEMENT
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream
from liquid.parse import parse_filtered_expression, expect
from liquid.expression import Expression


class StatementNode(ast.Node):
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
        if isinstance(val, (list, tuple)):
            val = "".join(str(v) for v in val)
        elif isinstance(val, bool):
            val = str(val).lower()
        elif val is None:
            val = ""
        else:
            val = str(val)

        buffer.write(val)


class Statement(Tag):
    """Pseudo "tag" to register output statements with the environment."""

    name = TOKEN_STATEMENT

    def parse(self, stream: TokenStream) -> ast.Node:
        tok = stream.current
        expect(stream, TOKEN_STATEMENT)

        # expr_iter = get_expression_lexer(self.env).tokenize(tok.value)
        expr_iter = self.expr_lexer.tokenize(tok.value)
        node = StatementNode(tok, parse_filtered_expression(expr_iter))
        return node
