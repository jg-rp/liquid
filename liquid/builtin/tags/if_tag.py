"""Tag and node definition for the built-in "if" tag."""
from __future__ import annotations
import sys

from typing import Optional
from typing import List
from typing import TextIO
from typing import TYPE_CHECKING

from liquid.token import Token
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

from liquid.ast import Node
from liquid.ast import BlockNode
from liquid.ast import ConditionalBlockNode

from liquid.exceptions import LiquidSyntaxError
from liquid.lex import tokenize_boolean_expression

from liquid.parse import expect
from liquid.parse import parse_boolean_expression
from liquid.parse import get_parser
from liquid.parse import eat_block

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.ast import IllegalNode

if TYPE_CHECKING:
    from liquid.context import Context
    from liquid import Environment
    from liquid.expression import Expression

TAG_IF = sys.intern("if")
TAG_ENDIF = sys.intern("endif")
TAG_ELSIF = sys.intern("elsif")
TAG_ELSE = sys.intern("else")

ENDIFBLOCK = (TAG_ENDIF, TAG_ELSIF, TAG_ELSE, TOKEN_EOF)
ENDELSIFBLOCK = (TAG_ENDIF, TAG_ELSIF, TAG_ELSE)
ENDIFELSEBLOCK = (TAG_ENDIF,)


class IfNode(Node):
    """Parse tree node for the built-in "if" tag."""

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
        consequence: BlockNode,
        conditional_alternatives: List[ConditionalBlockNode],
        alternative: Optional[BlockNode],
    ):
        self.tok = tok
        self.condition = condition
        self.consequence = consequence
        self.conditional_alternatives = conditional_alternatives
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

    def __repr__(self) -> str:  # pragma: no cover
        return f"IfNode(tok={self.tok}, condition='{self.condition}')"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
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

        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        if await self.condition.evaluate_async(context):
            await self.consequence.render_async(context, buffer)
        else:
            rendered = False
            for alt in self.conditional_alternatives:
                if await alt.render_async(context, buffer):
                    rendered = True
                    break

            if not rendered and self.alternative:
                await self.alternative.render_async(context, buffer)

        return None


class IfTag(Tag):
    """The built-in "if" tag."""

    name = TAG_IF
    end = TAG_ENDIF

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse_expression(self, stream: TokenStream) -> Expression:
        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_boolean_expression(stream.current.value)
        return parse_boolean_expression(TokenStream(expr_iter))

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_IF)
        tok = stream.current
        stream.next_token()

        condition = self.parse_expression(stream)
        stream.next_token()

        consequence = self.parser.parse_block(stream, ENDIFBLOCK)
        conditional_alternatives = []

        while stream.current.istag(TAG_ELSIF):
            stream.next_token()

            # If the expression can't be parsed, eat the "elsif" block and
            # continue to parse more "elsif" expression, if any.
            try:
                expr = self.parse_expression(stream)
            except LiquidSyntaxError as err:
                self.env.error(err)
                eat_block(stream, ENDELSIFBLOCK)
                return IllegalNode(tok)

            alt_tok = stream.current
            stream.next_token()
            alt_block = self.parser.parse_block(stream, ENDELSIFBLOCK)

            conditional_alternatives.append(
                ConditionalBlockNode(alt_tok, condition=expr, block=alt_block)
            )

        alternative: Optional[BlockNode] = None

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            alternative = self.parser.parse_block(stream, ENDIFELSEBLOCK)

        expect(stream, TOKEN_TAG, value=TAG_ENDIF)
        return IfNode(
            tok=tok,
            condition=condition,
            consequence=consequence,
            conditional_alternatives=conditional_alternatives,
            alternative=alternative,
        )
