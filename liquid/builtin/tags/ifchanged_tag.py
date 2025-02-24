"""The built-in _ifchanged_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.parse import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.context import RenderContext
    from liquid.stream import TokenStream


TAG_IFCHANGED = sys.intern("ifchanged")
TAG_ENDIFCHANGED = sys.intern("endifchanged")

ENDIFCHANGEDBLOCK = frozenset((TAG_ENDIFCHANGED,))


class IfChangedNode(Node):
    """The built-in _ifchanged_ tag."""

    __slots__ = ("block",)

    def __init__(self, token: Token, block: BlockNode):
        super().__init__(token)
        self.block = block
        # TODO: self.blank

    def __str__(self) -> str:
        return f"{{% ifchanged %}}{{ {self.block} }}{{% endifchanged %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        # Render to an intermediate buffer.
        buf = context.get_buffer(buffer)
        self.block.render(context, buf)
        val = buf.getvalue()

        # The context will update its namespace if needed.
        if context.ifchanged(val):
            return buffer.write(val)
        return 0

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        # Render to an intermediate buffer.
        buf = context.get_buffer(buffer)
        await self.block.render_async(context, buf)
        val = buf.getvalue()

        # The context will update its namespace if needed.
        if context.ifchanged(val):
            return buffer.write(val)
        return 0

    def children(self) -> list[ChildNode]:
        """Return this node's children."""
        return self.block.children()


class IfChangedTag(Tag):
    """The built-in _ifchanged_ tag."""

    name = TAG_IFCHANGED
    end = TAG_ENDIFCHANGED
    node_class = IfChangedNode

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        block = self.parser.parse_block(stream, ENDIFCHANGEDBLOCK)
        stream.expect(TOKEN_TAG, value=TAG_ENDIFCHANGED)
        return self.node_class(token, block)
