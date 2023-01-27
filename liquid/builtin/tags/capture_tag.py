"""Parse tree node and tag definition for the built-in "capture" tag."""

import re
import sys

from io import StringIO

from typing import List
from typing import Optional
from typing import TextIO

from liquid import ast
from liquid import Markup
from liquid.context import Context
from liquid.exceptions import LiquidSyntaxError

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION

from liquid.stream import TokenStream


RE_CAPTURE = re.compile(r"^\w[a-zA-Z0-9_\-]*$")

TAG_CAPTURE = sys.intern("capture")
TAG_ENDCAPTURE = sys.intern("endcapture")

ENDCAPTUREBLOCK = frozenset((TAG_ENDCAPTURE, TOKEN_EOF))


class CaptureNode(ast.Node):
    """Parse tree node for the built-in "capture" tag."""

    __slots__ = ("tok", "name", "block")

    def __init__(self, tok: Token, name: str, block: ast.BlockNode):
        self.tok = tok
        self.name = name
        self.block = block

    def __str__(self) -> str:
        return f"var {self.name} = {{ {self.block} }}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"CaptureNode(tok={self.tok}, name={self.name}, block='{self.block}')"

    def _assign(self, context: Context, buf: StringIO) -> None:
        if context.autoescape:
            context.assign(self.name, Markup(buf.getvalue()))
        else:
            context.assign(self.name, buf.getvalue())

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        self.block.render(context, buf)
        self._assign(context, buf)
        return False

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        await self.block.render_async(context, buf)
        self._assign(context, buf)
        return False

    def children(self) -> List[ast.ChildNode]:
        return [
            ast.ChildNode(
                linenum=self.tok.linenum,
                node=self.block,
                template_scope=[self.name],
            )
        ]


class CaptureTag(Tag):
    """The built-in capture tag."""

    name = TAG_CAPTURE
    end = TAG_ENDCAPTURE

    def parse(self, stream: TokenStream) -> CaptureNode:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG, value=TAG_CAPTURE)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)

        match = RE_CAPTURE.match(stream.current.value)
        if match:
            name = match.group()
        else:
            raise LiquidSyntaxError(
                f'invalid capture identifier "{stream.current.value}"',
                linenum=stream.current.linenum,
            )

        stream.next_token()
        block = parser.parse_block(stream, ENDCAPTUREBLOCK)
        expect(stream, TOKEN_TAG, value=TAG_ENDCAPTURE)

        return CaptureNode(tok, name, block=block)
