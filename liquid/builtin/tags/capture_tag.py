"""Parse tree node and tag definition for the built-in "capture" tag."""

import sys
from io import StringIO
from typing import TextIO

from liquid import Markup
from liquid import ast
from liquid.builtin.expressions import parse_identifier
from liquid.context import RenderContext
from liquid.parse import get_parser
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG
from liquid.token import Token

TAG_CAPTURE = sys.intern("capture")
TAG_ENDCAPTURE = sys.intern("endcapture")

ENDCAPTUREBLOCK = frozenset((TAG_ENDCAPTURE, TOKEN_EOF))


class CaptureNode(ast.Node):
    """Parse tree node for the built-in "capture" tag."""

    __slots__ = ("name", "block")

    def __init__(self, token: Token, name: str, block: ast.BlockNode):
        super().__init__(token)
        self.name = name
        self.block = block

    def __str__(self) -> str:
        # TODO: WC
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

    def children(self) -> list[ast.ChildNode]:
        """Return this node's children."""
        return [
            ast.ChildNode(
                linenum=self.token.start_index,
                node=self.block,
                template_scope=[self.name],
            )
        ]


class CaptureTag(Tag):
    """The built-in capture tag."""

    name = TAG_CAPTURE
    end = TAG_ENDCAPTURE
    node_class = CaptureNode

    def parse(self, stream: TokenStream) -> CaptureNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner()
        name = parse_identifier(self.env, tokens)
        tokens.expect_eos()
        block = get_parser(self.env).parse_block(stream, ENDCAPTUREBLOCK)
        stream.expect(TOKEN_TAG, value=TAG_ENDCAPTURE)
        return self.node_class(token, name, block)
