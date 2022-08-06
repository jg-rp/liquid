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

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode
from liquid.ast import ConditionalBlockNode

from liquid.exceptions import LiquidSyntaxError

from liquid.parse import expect
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

ENDIFBLOCK = frozenset((TAG_ENDIF, TAG_ELSIF, TAG_ELSE, TOKEN_EOF))
ENDELSIFBLOCK = frozenset((TAG_ENDIF, TAG_ELSIF, TAG_ELSE))
ENDIFELSEBLOCK = frozenset((TAG_ENDIF,))


class IfNode(Node):
    """Parse tree node for the built-in "if" tag."""

    __slots__ = (
        "tok",
        "condition",
        "consequence",
        "conditional_alternatives",
        "alternative",
        "forced_output",
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

        self.forced_output = any(
            getattr(n, "forced_output", False)
            for n in (
                self.consequence,
                *self.conditional_alternatives,
                self.alternative,
            )
            if n
        )

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
        # This intermediate buffer is used to detect and possibly suppress blocks that,
        # when rendered, contain only whitespace.
        buf = context.get_buffer(buffer)

        if self.condition.evaluate(context):
            rendered = self.consequence.render(context, buf)
        else:
            rendered = False
            for alt in self.conditional_alternatives:
                if alt.render(context, buf):
                    rendered = True
                    break

            if not rendered and self.alternative:
                rendered = self.alternative.render(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        buf = context.get_buffer(buffer)

        if await self.condition.evaluate_async(context):
            rendered = await self.consequence.render_async(context, buf)
        else:
            rendered = False
            for alt in self.conditional_alternatives:
                if await alt.render_async(context, buf):
                    rendered = True
                    break

            if not rendered and self.alternative:
                rendered = await self.alternative.render_async(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    def children(self) -> List[ChildNode]:
        _children = [
            ChildNode(
                linenum=self.tok.linenum,
                node=self.consequence,
                expression=self.condition,
            )
        ]
        _children.extend(
            [
                ChildNode(
                    linenum=alt.tok.linenum,
                    node=alt.block,
                    expression=alt.condition,
                )
                for alt in self.conditional_alternatives
            ]
        )
        if self.alternative:
            _children.append(
                ChildNode(
                    linenum=self.alternative.tok.linenum,
                    node=self.alternative,
                    expression=None,
                )
            )

        return _children


class IfTag(Tag):
    """The built-in "if" tag."""

    name = TAG_IF
    end = TAG_ENDIF

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse_expression(self, stream: TokenStream) -> Expression:
        """Pare a boolean expression from a stream of tokens."""
        expect(stream, TOKEN_EXPRESSION)
        return self.env.parse_boolean_expression_value(stream.current.value)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_IF)
        tok = stream.current
        stream.next_token()

        condition = self.parse_expression(stream)
        stream.next_token()

        consequence = self.parser.parse_block(stream, ENDIFBLOCK)
        conditional_alternatives = []

        parse_block = self.parser.parse_block
        parse_expression = self.parse_expression

        while stream.current.istag(TAG_ELSIF):
            stream.next_token()

            # If the expression can't be parsed, eat the "elsif" block and
            # continue to parse more "elsif" expression, if any.
            try:
                expr = parse_expression(stream)
            except LiquidSyntaxError as err:
                self.env.error(err)
                eat_block(stream, ENDELSIFBLOCK)
                return IllegalNode(tok)

            alt_tok = stream.current
            stream.next_token()
            alt_block = parse_block(stream, ENDELSIFBLOCK)

            conditional_alternatives.append(
                ConditionalBlockNode(alt_tok, condition=expr, block=alt_block)
            )

        alternative: Optional[BlockNode] = None

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            alternative = parse_block(stream, ENDIFELSEBLOCK)

        expect(stream, TOKEN_TAG, value=TAG_ENDIF)
        return IfNode(
            tok=tok,
            condition=condition,
            consequence=consequence,
            conditional_alternatives=conditional_alternatives,
            alternative=alternative,
        )
