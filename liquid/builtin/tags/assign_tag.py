"""The built-in _assign_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import TextIO

from liquid.ast import Node
from liquid.builtin.expressions import FilteredExpression
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import parse_identifier
from liquid.tag import Tag
from liquid.token import TOKEN_ASSIGN
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream


TAG_ASSIGN = sys.intern("assign")


class AssignNode(Node):
    """The built-in _assign_ tag."""

    __slots__ = ("name", "expression")

    def __init__(self, token: Token, *, name: Identifier, expression: Expression):
        super().__init__(token)
        self.name = name
        self.expression = expression

    def __str__(self) -> str:
        return f"{{% assign {self.name} = {self.expression} %}}"

    def render_to_output(self, context: RenderContext, _: TextIO) -> int:
        """Render the node to the output buffer."""
        context.assign(self.name, self.expression.evaluate(context))
        return 0

    async def render_to_output_async(self, context: RenderContext, _: TextIO) -> int:
        """Render the node to the output buffer."""
        context.assign(self.name, await self.expression.evaluate_async(context))
        return 0

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.expression

    def template_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the template local scope."""
        yield self.name


class AssignTag(Tag):
    """The built-in _assign_ tag."""

    name = TAG_ASSIGN
    block = False
    node_class = AssignNode

    def parse(self, stream: TokenStream) -> AssignNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token, eat=False)
        name = parse_identifier(self.env, tokens, allow_trailing_question_mark=False)
        tokens.eat(TOKEN_ASSIGN)
        return self.node_class(
            token, name=name, expression=FilteredExpression.parse(self.env, tokens)
        )
