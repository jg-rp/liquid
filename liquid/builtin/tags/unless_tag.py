"""The built-in _unless_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Optional
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import ChildNode
from liquid.ast import ConditionalBlockNode
from liquid.ast import IllegalNode
from liquid.ast import Node
from liquid.builtin.expressions import BooleanExpression
from liquid.exceptions import LiquidSyntaxError
from liquid.mode import Mode
from liquid.parse import eat_block
from liquid.parse import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream


TAG_UNLESS = sys.intern("unless")
TAG_ENDUNLESS = sys.intern("endunless")
TAG_ELSIF = sys.intern("elsif")
TAG_ELSE = sys.intern("else")

ENDUNLESSBLOCK = frozenset((TAG_ENDUNLESS, TAG_ELSIF, TAG_ELSE, TOKEN_EOF))
ENDELSIFBLOCK = frozenset((TAG_ENDUNLESS, TAG_ELSIF, TAG_ELSE))
ENDUNLESSELSEBLOCK = frozenset((TAG_ENDUNLESS, TAG_ELSIF, TAG_ELSE))


class UnlessNode(Node):
    """The built-in _unless_ tag."""

    __slots__ = (
        "condition",
        "consequence",
        "alternatives",
        "default",
    )

    def __init__(
        self,
        token: Token,
        condition: Expression,
        consequence: BlockNode,
        alternatives: Optional[list[ConditionalBlockNode]] = None,
        default: Optional[BlockNode] = None,
    ):
        super().__init__(token)
        self.condition = condition
        self.consequence = consequence
        self.alternatives = alternatives or []
        self.default = default

        self.blank = (
            consequence.blank
            and all(node.blank for node in self.alternatives)
            and (not default or default.blank)
        )

    def __str__(self) -> str:
        alts = "".join(str(alt) for alt in self.alternatives)
        default = ""

        if self.default:
            default = f"{{% else %}}{self.default}"

        return (
            f"{{% unless {self.condition} %}}"
            f"{self.consequence}"
            f"{alts}"
            f"{default}"
            f"{{% endunless %}}"
        )

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        if not self.condition.evaluate(context):
            return self.consequence.render(context, buffer)

        for alternative in self.alternatives:
            if alternative.condition.evaluate(context):
                return alternative.block.render(context, buffer)

        if self.default:
            return self.default.render(context, buffer)

        return 0

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        if not await self.condition.evaluate_async(context):
            return await self.consequence.render_async(context, buffer)

        for alternative in self.alternatives:
            if await alternative.condition.evaluate_async(context):
                return await alternative.block.render_async(context, buffer)

        if self.default:
            return await self.default.render_async(context, buffer)

        return 0

    def children(self) -> list[ChildNode]:
        """Return this node's children."""
        _children = [
            ChildNode(
                linenum=self.consequence.token.start_index,
                node=self.consequence,
                expression=self.condition,
            )
        ]
        _children.extend(
            [
                ChildNode(
                    linenum=alt.token.start_index,
                    node=alt.block,
                    expression=alt.condition,
                )
                for alt in self.alternatives
            ]
        )
        if self.default:
            _children.append(
                ChildNode(
                    linenum=self.default.token.start_index,
                    node=self.default,
                    expression=None,
                )
            )
        return _children


class UnlessTag(Tag):
    """The built-in "unless" tag."""

    name = TAG_UNLESS
    end = TAG_ENDUNLESS
    node_class = UnlessNode

    mode = Mode.STRICT
    """Tag specific parsing mode, independent from environment tolerance mode."""

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner()
        condition = BooleanExpression.parse(self.env, tokens)
        parse_block = get_parser(self.env).parse_block
        consequence = parse_block(stream, ENDUNLESSBLOCK)
        alternatives = []

        while stream.current.is_tag(TAG_ELSIF):
            stream.next_token()

            # If the expression can't be parsed, eat the "elsif" block and
            # continue to parse more "elsif" expression, if any.
            try:
                expr = BooleanExpression.parse(self.env, stream.into_inner())
            except LiquidSyntaxError as err:
                self.env.error(err)
                eat_block(stream, ENDELSIFBLOCK)
                return IllegalNode(token)

            alt_tok = stream.current
            alt_block = parse_block(stream, ENDELSIFBLOCK)

            alternatives.append(
                ConditionalBlockNode(alt_tok, condition=expr, block=alt_block)
            )

        alternative: Optional[BlockNode] = None

        if stream.current.is_tag(TAG_ELSE):
            stream.next_token()
            if stream.current.kind == TOKEN_EXPRESSION:
                if self.mode == Mode.LAX:
                    # Superfluous expressions inside an `else` tag are ignored.
                    stream.next_token()
                else:
                    raise LiquidSyntaxError(
                        "found an 'else' tag expression, did you mean 'elsif'?",
                        token=stream.current,
                    )
            alternative = parse_block(stream, ENDUNLESSELSEBLOCK)

        # Extraneous `else` and `elsif` blocks are ignored.
        if not stream.current.is_tag(TAG_ENDUNLESS) and self.mode == Mode.LAX:
            while stream.current.kind != TOKEN_EOF:
                if (
                    stream.current.kind == TOKEN_TAG
                    and stream.current.value == TAG_ENDUNLESS
                ):
                    break
                stream.next_token()

        stream.expect(TOKEN_TAG, value=TAG_ENDUNLESS)

        return self.node_class(
            token=token,
            condition=condition,
            consequence=consequence,
            alternatives=alternatives,
            default=alternative,
        )
