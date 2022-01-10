"""Tag and node definition for the built-in "unless" tag."""
from __future__ import annotations
import sys

from io import StringIO

from typing import List
from typing import Optional
from typing import TextIO
from typing import TYPE_CHECKING
from typing import Union

from liquid.ast import Node
from liquid.ast import BlockNode
from liquid.ast import ConditionalBlockNode
from liquid.ast import IllegalNode

from liquid.context import Context
from liquid.exceptions import LiquidSyntaxError
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import eat_block
from liquid.parse import expect
from liquid.parse import get_parser

from liquid.token import Token
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid.expression import Expression

TAG_UNLESS = sys.intern("unless")
TAG_ENDUNLESS = sys.intern("endunless")
TAG_ELSIF = sys.intern("elsif")
TAG_ELSE = sys.intern("else")

ENDUNLESSBLOCK = (TAG_ENDUNLESS, TAG_ELSIF, TAG_ELSE, TOKEN_EOF)
ENDELSIFBLOCK = (TAG_ENDUNLESS, TAG_ELSIF, TAG_ELSE)
ENDUNLESSELSEBLOCK = (TAG_ENDUNLESS,)


class UnlessNode(Node):
    """Parse tree node for the built-in "unless" tag."""

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
        conditional_alternatives: Optional[List[ConditionalBlockNode]] = None,
        alternative: Optional[BlockNode] = None,
    ):
        self.tok = tok
        self.condition = condition
        self.consequence = consequence
        self.conditional_alternatives = conditional_alternatives or []
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
            f"if !{self.condition} {{ {self.consequence} }}",
        ]

        for alt in self.conditional_alternatives:
            buf.append(f"elsif {alt}")

        if self.alternative:
            buf.append(f"else {{ {self.alternative} }}")
        return " ".join(buf)

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        # This intermediate buffer is used to detect and possibly suppress blocks that,
        # when rendered, contain only whitespace.
        buf = StringIO()

        if not self.condition.evaluate(context):
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
        # This intermediate buffer is used to detect and possibly suppress blocks that,
        # when rendered, contain only whitespace.
        buf = StringIO()

        if not await self.condition.evaluate_async(context):
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


class UnlessTag(Tag):
    """The built-in "unless" tag."""

    name = TAG_UNLESS
    end = TAG_ENDUNLESS

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    # pylint: disable=no-self-use
    def parse_expression(self, stream: TokenStream) -> Expression:
        """Parse a boolean expression from a stream of tokens."""
        expect(stream, TOKEN_EXPRESSION)
        return self.env.parse_boolean_expression_value(stream.current.value)

    def parse(self, stream: TokenStream) -> Union[UnlessNode, IllegalNode]:

        expect(stream, TOKEN_TAG, value=TAG_UNLESS)
        tok = stream.current
        stream.next_token()

        condition = self.parse_expression(stream)
        stream.next_token()

        consequence = self.parser.parse_block(stream, ENDUNLESSBLOCK)

        conditional_alternatives = []

        while stream.current.istag(TAG_ELSIF):
            stream.next_token()

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
            alternative = self.parser.parse_block(stream, ENDUNLESSELSEBLOCK)

        expect(stream, TOKEN_TAG, value=TAG_ENDUNLESS)
        return UnlessNode(
            tok,
            condition=condition,
            consequence=consequence,
            conditional_alternatives=conditional_alternatives,
            alternative=alternative,
        )
