"""The built-in _case_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import TextIO

from liquid.ast import Node
from liquid.builtin.expressions import parse_primitive
from liquid.builtin.expressions.logical import _eq
from liquid.exceptions import LiquidSyntaxError
from liquid.expression import Expression
from liquid.parse import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_ELSE
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import TokenStream
    from liquid.ast import BlockNode
    from liquid.context import RenderContext


TAG_CASE = sys.intern("case")
TAG_ENDCASE = sys.intern("endcase")
TAG_WHEN = sys.intern("when")
TAG_ELSE = sys.intern("else")

ENDWHENBLOCK = frozenset((TAG_ENDCASE, TAG_WHEN, TAG_ELSE, TOKEN_EOF))
ENDCASEBLOCK = frozenset((TAG_ENDCASE,))


class CaseNode(Node):
    """The built-in _case_ tag."""

    __slots__ = ("whens", "default", "expression")

    def __init__(
        self,
        token: Token,
        expression: Expression,
        whens: list[MultiExpressionBlockNode],
        default: Optional[BlockNode] = None,
    ):
        super().__init__(token)
        self.expression = expression
        self.whens = whens
        self.default = default

        self.blank = all(node.blank for node in self.whens) and (
            not self.default or self.default.blank
        )

    def __str__(self) -> str:
        default = ""

        if self.default:
            default = f"{{% else %}}{self.default}"

        return (
            f"{{% case {self.expression} %}}\n"
            f"{''.join(str(w) for w in self.whens)}"
            f"{default}"
            f"{{% endcase %}}"
        )

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        count = 0
        for when in self.whens:
            count += when.render(context, buffer)

        if not count and self.default is not None:
            count += self.default.render(context, buffer)

        return count

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        count = 0
        for when in self.whens:
            count += await when.render_async(context, buffer)

        if not count and self.default is not None:
            count += await self.default.render_async(context, buffer)

        return count

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield from self.whens

        if self.default:
            yield self.default

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.expression


class CaseTag(Tag):
    """The built-in _case_ tag."""

    name = TAG_CASE
    end = TAG_ENDCASE
    node_class = CaseNode

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner()
        left = parse_primitive(self.env, tokens)
        tokens.expect_eos()

        # Eat whitespace or junk between `case` and when/else/endcase
        while (
            stream.current.kind != TOKEN_TAG
            and stream.current.value not in ENDWHENBLOCK
        ):
            stream.next_token()

        whens: list[MultiExpressionBlockNode] = []
        default: BlockNode | None = None

        parse_block = get_parser(self.env).parse_block

        while stream.current.is_tag(TAG_WHEN):
            alternative_token = next(stream)
            expressions = self._parse_when_expression(stream.into_inner())
            alternative_block = parse_block(stream, ENDWHENBLOCK)

            whens.append(
                MultiExpressionBlockNode(
                    alternative_token,
                    alternative_block,
                    _AnyExpression(alternative_token, left, expressions),
                )
            )

        if stream.current.kind == TOKEN_TAG and stream.current.value == TOKEN_ELSE:
            next(stream)  # else
            default = parse_block(stream, ENDCASEBLOCK)

        stream.expect(TOKEN_TAG, TAG_ENDCASE)

        return self.node_class(
            token,
            left,
            whens,
            default,
        )

    def _parse_when_expression(self, stream: TokenStream) -> list[Expression]:
        expressions: list[Expression] = [parse_primitive(self.env, stream)]
        while stream.current.kind in (TOKEN_COMMA, TOKEN_OR):
            next(stream)
            try:
                expressions.append(parse_primitive(self.env, stream))
            except LiquidSyntaxError:
                # Use expressions we have so far an discard the rest.
                return expressions

        return expressions


class _AnyExpression(Expression):
    __slots__ = (
        "left",
        "expressions",
    )

    def __init__(
        self, token: Token, left: Expression, expressions: list[Expression]
    ) -> None:
        super().__init__(token)
        self.left = left
        self.expressions = expressions

    def __str__(self) -> str:
        return ", ".join(str(expr) for expr in self.expressions)

    def evaluate(self, context: RenderContext) -> int:
        left = self.left.evaluate(context)
        return [_eq(left, right.evaluate(context)) for right in self.expressions].count(
            True
        )

    async def evaluate_async(self, context: RenderContext) -> int:
        left = await self.left.evaluate_async(context)
        return [
            _eq(left, await right.evaluate_async(context)) for right in self.expressions
        ].count(True)

    def children(self) -> list[Expression]:
        return self.expressions


class MultiExpressionBlockNode(Node):
    """A node containing a sequence of nodes guarded by a choice of expressions."""

    __slots__ = ("block", "expression")

    def __init__(
        self,
        token: Token,
        block: BlockNode,
        expression: _AnyExpression,
    ) -> None:
        super().__init__(token)
        self.block = block
        self.expression = expression
        self.blank = self.block.blank

    def __str__(self) -> str:
        return f"{{% when {self.expression} %}}{self.block}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        return sum(
            self.block.render(context, buffer)
            for _ in range(self.expression.evaluate(context))
        )

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        return sum(
            [
                await self.block.render_async(context, buffer)
                for _ in range(await self.expression.evaluate_async(context))
            ]
        )

    # TODO:
    # def children(
    #     self,
    #     static_context: RenderContext,  # noqa: ARG002
    #     *,
    # ) -> Iterable[Node]:
    #     """Return this node's children."""
    #     yield self.block

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.expression
