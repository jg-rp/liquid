""""""
import sys
from typing import Optional, TextIO

from liquid.token import Token, TOKEN_EOF, TOKEN_EXPRESSION, TOKEN_TAG_NAME
from liquid.parse import get_parser, expect, parse_boolean_expression
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream, get_expression_lexer
from liquid.expression import Expression

TAG_UNLESS = sys.intern("unless")
TAG_ENDUNLESS = sys.intern("endunless")

ENDUNLESSBLOCK = (TAG_ENDUNLESS, TOKEN_EOF)


class UnlessNode(ast.Node):
    __slots__ = ("tok", "condition", "consequence")

    def __init__(
        self,
        tok: Token,
        condition: Expression,
        consequence: Optional[ast.BlockNode] = None,
    ):
        self.tok = tok
        self.condition = condition
        self.consequence = consequence

    def __str__(self) -> str:
        return f"if !{self.condition} {{ {self.consequence} }}"

    def render_to_output(self, context: Context, buffer: TextIO):
        if not self.condition.evaluate(context):
            self.consequence.render(context, buffer)


class UnlessTag(Tag):

    name = TAG_UNLESS
    end = TAG_ENDUNLESS

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)
        lexer = get_expression_lexer(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_UNLESS)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = lexer.tokenize(stream.current.value)
        expr = parse_boolean_expression(expr_iter)

        tag = UnlessNode(tok, condition=expr)
        stream.next_token()
        tag.consequence = parser.parse_block(stream, ENDUNLESSBLOCK)

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDUNLESS)
        return tag
