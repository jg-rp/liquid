""""""
import sys
from typing import TextIO

from liquid.token import Token, TOKEN_TAG_NAME, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream, get_expression_lexer
from liquid.expression import AssignmentExpression
from liquid.parse import expect, parse_assignment_expression

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

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> AssignNode:
        lexer = get_expression_lexer(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_ASSIGN)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = lexer.tokenize(stream.current.value)
        return AssignNode(
            tok,
            parse_assignment_expression(expr_iter),
        )
