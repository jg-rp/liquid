"""Parse tree node and tag definition for the built-in "capture" tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import TextIO

from liquid import Markup
from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.builtin.expressions import parse_identifier
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from io import StringIO

    from liquid.builtin.expressions import Identifier
    from liquid.context import RenderContext
    from liquid.stream import TokenStream


TAG_CAPTURE = sys.intern("capture")
TAG_ENDCAPTURE = sys.intern("endcapture")

ENDCAPTUREBLOCK = frozenset((TAG_ENDCAPTURE, TOKEN_EOF))


class CaptureNode(Node):
    """Parse tree node for the built-in "capture" tag."""

    __slots__ = ("name", "block")

    def __init__(self, token: Token, name: Identifier, block: BlockNode):
        super().__init__(token)
        self.name = name
        self.block = block

    def __str__(self) -> str:
        return f"{{% capture {self.name} %}}{self.block}{{% endcapture %}}"

    def _assign(self, context: RenderContext, buf: StringIO) -> None:
        if context.autoescape:
            context.assign(self.name, Markup(buf.getvalue()))
        else:
            context.assign(self.name, buf.getvalue())

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        buf = context.get_buffer(buffer)
        self.block.render(context, buf)
        self._assign(context, buf)
        return False

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        buf = context.get_buffer(buffer)
        await self.block.render_async(context, buf)
        self._assign(context, buf)
        return False

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.block

    def template_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the template local scope."""
        yield self.name


class CaptureTag(Tag):
    """The built-in capture tag."""

    name = TAG_CAPTURE
    end = TAG_ENDCAPTURE
    node_class = CaptureNode

    def parse(self, stream: TokenStream) -> CaptureNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token)
        name = parse_identifier(self.env, tokens)
        tokens.expect_eos()
        block = get_parser(self.env).parse_block(stream, ENDCAPTUREBLOCK)
        stream.expect(TOKEN_TAG, value=TAG_ENDCAPTURE)
        return self.node_class(token, name, block)
