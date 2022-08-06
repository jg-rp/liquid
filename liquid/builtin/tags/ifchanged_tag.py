"""Tag and node definition for the built-in "ifchanged" tag."""
from __future__ import annotations
import sys

from typing import List
from typing import Optional
from typing import TextIO
from typing import TYPE_CHECKING

from liquid.token import Token
from liquid.token import TOKEN_TAG

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.stream import TokenStream
from liquid.tag import Tag

if TYPE_CHECKING:  # pragma: no cover
    from liquid.context import Context
    from liquid import Environment


TAG_IFCHANGED = sys.intern("ifchanged")
TAG_ENDIFCHANGED = sys.intern("endifchanged")

ENDIFCHANGEDBLOCK = frozenset((TAG_ENDIFCHANGED,))


class IfChangedNode(Node):
    """Parse tree node for the built-in "ifchanged" tag"""

    __slots__ = ("tok", "block")

    def __init__(self, tok: Token, block: BlockNode):
        self.tok = tok
        self.block = block

    def __str__(self) -> str:
        return f"ifchanged {{ {self.block} }}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"IfChanged(tok={self.tok})"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        # Render to an intermediate buffer.
        buf = context.get_buffer(buffer)
        self.block.render(context, buf)
        val = buf.getvalue()

        # The context will update its namespace if needed.
        if context.ifchanged(val):
            buffer.write(val)
            return True
        return False

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        # Render to an intermediate buffer.
        buf = context.get_buffer(buffer)
        await self.block.render_async(context, buf)
        val = buf.getvalue()

        # The context will update its namespace if needed.
        if context.ifchanged(val):
            buffer.write(val)
            return True
        return False

    def children(self) -> List[ChildNode]:
        return self.block.children()


class IfChangedTag(Tag):
    """The built-in "ifchanged" tag"""

    name = TAG_IFCHANGED
    end = TAG_ENDIFCHANGED

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_IFCHANGED)
        tok = stream.current
        stream.next_token()

        block = self.parser.parse_block(stream, ENDIFCHANGEDBLOCK)
        expect(stream, TOKEN_TAG, value=TAG_ENDIFCHANGED)

        return IfChangedNode(tok=tok, block=block)
