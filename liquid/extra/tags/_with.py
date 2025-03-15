"""The extra _with_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import KeywordArgument
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream

TAG_WITH = sys.intern("with")
TAG_ENDWITH = sys.intern("endwith")


class WithNode(Node):
    __slots__ = ("args", "block")

    def __init__(self, token: Token, args: list[KeywordArgument], block: BlockNode):
        super().__init__(token)
        self.args = args
        self.block = block
        self.blank = self.block.blank

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        namespace = dict(arg.evaluate(context) for arg in self.args)

        with context.extend(namespace):
            return self.block.render(context, buffer)

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        namespace = dict([await arg.evaluate_async(context) for arg in self.args])
        with context.extend(namespace):
            return await self.block.render_async(context, buffer)

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.block

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield from (arg.value for arg in self.args)

    def block_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the node's block scope."""
        yield from (Identifier(p.name, token=p.token) for p in self.args)


class WithTag(Tag):
    """The extra _with_ tag."""

    name = TAG_WITH
    end = TAG_ENDWITH
    node_class = WithNode

    def parse(self, stream: TokenStream) -> Node:
        token = stream.eat(TOKEN_TAG)
        args = KeywordArgument.parse(self.env, stream.into_inner(tag=token))

        # Parse the block
        block = get_parser(self.env).parse_block(stream, (TAG_ENDWITH, TOKEN_EOF))
        stream.expect(TOKEN_TAG, value=TAG_ENDWITH)
        return self.node_class(token, args=args, block=block)
