"""Parse tree node and tag definition for the built in "if" tag."""

import sys
from typing import Optional, List, TextIO

from liquid.token import (
    Token,
    TOKEN_EOF,
    TOKEN_TAG_NAME,
    TOKEN_EXPRESSION,
)
from liquid.parse import expect, parse_boolean_expression, get_parser, eat_block
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream, get_expression_lexer
from liquid.expression import Expression
from liquid.exceptions import LiquidSyntaxError
from liquid.builtin.illegal import IllegalNode

TAG_IF = sys.intern("if")
TAG_ENDIF = sys.intern("endif")
TAG_ELSIF = sys.intern("elsif")
TAG_ELSE = sys.intern("else")

ENDIFBLOCK = (TAG_ENDIF, TAG_ELSIF, TAG_ELSE, TOKEN_EOF)
ENDELSIFBLOCK = (TAG_ENDIF, TAG_ELSIF, TAG_ELSE)
ENDIFELSEBLOCK = (TAG_ENDIF,)


class IfNode(ast.Node):
    """Parse tree node for "if" block tags."""

    __slots__ = (
        "tok",
        "condition",
        "consequence",
        "conditional_alternatives",
        "alternative",
    )

    def __init__(
        self,
        tok: Token,
        condition: Expression,
        consequence: Optional[ast.BlockNode] = None,
        conditional_alternatives: List[ast.ConditionalBlockNode] = None,
        alternative: Optional[ast.BlockNode] = None,
    ):
        self.tok = tok
        self.condition = condition
        self.consequence = consequence
        self.conditional_alternatives = conditional_alternatives or []
        self.alternative = alternative

    def __str__(self) -> str:
        buf = [
            f"if {self.condition} {{ {self.consequence} }}",
        ]

        for alt in self.conditional_alternatives:
            buf.append(f"elsif {alt}")

        if self.alternative:
            buf.append(f"else {{ {self.alternative} }}")
        return " ".join(buf)

    def __repr__(self):  # pragma: no cover
        return f"IfNode(tok={self.tok}, condition='{self.condition}')"

    def render_to_output(self, context: Context, buffer: TextIO):
        if self.condition.evaluate(context):
            self.consequence.render(context, buffer)
        else:
            rendered = False
            for alt in self.conditional_alternatives:
                if alt.render(context, buffer):
                    rendered = True
                    break

            if not rendered and self.alternative:
                self.alternative.render(context, buffer)


class IfTag(Tag):
    """"""

    name = TAG_IF
    end = TAG_ENDIF

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_IF)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = self.expr_lexer.tokenize(stream.current.value)

        # If the expression can't be parsed, eat the whole "if" tag, including
        # any alternatives. See `Tag.get_node`.
        expr = parse_boolean_expression(expr_iter)

        node = IfNode(tok, expr)
        stream.next_token()

        node.consequence = parser.parse_block(stream, ENDIFBLOCK)

        while stream.current.istag(TAG_ELSIF):
            stream.next_token()
            expect(stream, TOKEN_EXPRESSION)

            expr_iter = self.expr_lexer.tokenize(stream.current.value)

            # If the expression can't be parsed, eat the "elsif" block and
            # continue to parse more "elsif" expression, if any.
            try:
                expr = parse_boolean_expression(expr_iter)
            except LiquidSyntaxError as err:
                self.env.error(err)
                eat_block(stream, ENDELSIFBLOCK)
                return IllegalNode(node.tok)

            alt = ast.ConditionalBlockNode(
                stream.current,
                condition=expr,
            )
            stream.next_token()
            alt.block = parser.parse_block(stream, ENDELSIFBLOCK)
            node.conditional_alternatives.append(alt)

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            node.alternative = parser.parse_block(stream, ENDIFELSEBLOCK)

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDIF)
        return node
