"""The built-in _if_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import ConditionalBlockNode
from liquid.ast import IllegalNode
from liquid.ast import Node
from liquid.builtin.expressions import BooleanExpression
from liquid.exceptions import LiquidSyntaxError
from liquid.mode import Mode
from liquid.parser import eat_block
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream


TAG_IF = sys.intern("if")
TAG_ENDIF = sys.intern("endif")
TAG_ELSIF = sys.intern("elsif")
TAG_ELSE = sys.intern("else")

ENDIFBLOCK = frozenset((TAG_ENDIF, TAG_ELSIF, TAG_ELSE, TOKEN_EOF))
ENDELSIFBLOCK = frozenset((TAG_ENDIF, TAG_ELSIF, TAG_ELSE))
ENDIFELSEBLOCK = frozenset((TAG_ENDIF, TAG_ELSE, TAG_ELSIF))


class IfNode(Node):
    """The built-in _if_ tag."""

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
        alternatives: list[ConditionalBlockNode],
        default: Optional[BlockNode],
    ):
        super().__init__(token)
        self.condition = condition
        self.consequence = consequence
        self.alternatives = alternatives
        self.default = default

        self.blank = (
            consequence.blank
            and all(node.blank for node in alternatives)
            and (not default or default.blank)
        )

        self.consequence.blank = self.blank

        for node in self.alternatives:
            node.blank = self.blank

        if self.default:
            self.default.blank = self.blank

    def __str__(self) -> str:
        alts = "".join(str(alt) for alt in self.alternatives)
        default = ""

        if self.default:
            default = f"{{% else %}}{self.default}"

        return (
            f"{{% if {self.condition} %}}{self.consequence}{alts}{default}{{% endif %}}"
        )

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        if self.condition.evaluate(context):
            return self.consequence.render(context, buffer)

        for alternative in self.alternatives:
            if alternative.expression.evaluate(context):
                return alternative.block.render(context, buffer)

        if self.default:
            return self.default.render(context, buffer)

        return 0

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        if await self.condition.evaluate_async(context):
            return await self.consequence.render_async(context, buffer)

        for alternative in self.alternatives:
            if await alternative.expression.evaluate_async(context):
                return await alternative.render_async(context, buffer)

        if self.default:
            return await self.default.render_async(context, buffer)

        return 0

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.consequence
        yield from self.alternatives
        if self.default:
            yield self.default

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.condition


class IfTag(Tag):
    """The built-in _if_ tag."""

    name = TAG_IF
    end = TAG_ENDIF
    node_class = IfNode

    mode = Mode.LAX
    """Tag specific parsing mode, independent from environment tolerance mode."""

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token)
        condition = BooleanExpression.parse(self.env, tokens)
        parse_block = get_parser(self.env).parse_block
        consequence = parse_block(stream, ENDIFBLOCK)
        alternatives = []

        while stream.current.is_tag(TAG_ELSIF):
            # If the expression can't be parsed, eat the "elsif" block and
            # continue to parse more "elsif" expression, if any.
            try:
                expr = BooleanExpression.parse(
                    self.env, stream.into_inner(tag=next(stream))
                )
            except LiquidSyntaxError as err:
                self.env.error(err)
                eat_block(stream, ENDELSIFBLOCK)
                return IllegalNode(token)

            alt_tok = stream.current
            alt_block = parse_block(stream, ENDELSIFBLOCK)

            alternatives.append(
                ConditionalBlockNode(alt_tok, expression=expr, block=alt_block)
            )

        default: Optional[BlockNode] = None

        if stream.current.is_tag(TAG_ELSE):
            next(stream)
            if stream.current.kind == TOKEN_EXPRESSION:
                if self.mode == Mode.LAX:
                    # Superfluous expressions inside an `else` tag are ignored.
                    next(stream)
                else:
                    raise LiquidSyntaxError(
                        "found an 'else' tag expression, did you mean 'elsif'?",
                        token=stream.current,
                    )
            default = parse_block(stream, ENDIFELSEBLOCK)

        # Extraneous `else` and `elsif` blocks are ignored.
        if not stream.current.is_tag(TAG_ENDIF) and self.mode == Mode.LAX:
            while stream.current.kind != TOKEN_EOF:
                if (
                    stream.current.kind == TOKEN_TAG
                    and stream.current.value == TAG_ENDIF
                ):
                    break
                next(stream)

        stream.expect(TOKEN_TAG, value=TAG_ENDIF)

        return self.node_class(
            token=token,
            condition=condition,
            consequence=consequence,
            alternatives=alternatives,
            default=default,
        )
