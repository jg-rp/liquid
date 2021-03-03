"""Parse tree node and tag definition for the built-in "capture" tag."""

import re
import sys
from io import StringIO
from typing import TextIO

from liquid.token import Token, TOKEN_TAG, TOKEN_EOF, TOKEN_EXPRESSION
from liquid.parse import expect, get_parser
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.exceptions import LiquidSyntaxError

RE_CAPTURE = re.compile(r"^\w[a-zA-Z0-9_\-]*$")

TAG_CAPTURE = sys.intern("capture")
TAG_ENDCAPTURE = sys.intern("endcapture")

ENDCAPTUREBLOCK = (TAG_ENDCAPTURE, TOKEN_EOF)


class CaptureNode(ast.Node):
    """Parse tree node for the built-in "capture" tag."""

    __slots__ = ("tok", "name", "block")

    def __init__(self, tok: Token, name: str, block: ast.BlockNode):
        self.tok = tok
        self.name = name
        self.block = block

    def __str__(self) -> str:
        return f"var {self.name} = {{ {self.block} }}"

    def __repr__(self):  # pragma: no cover
        return f"CaptureNode(tok={self.tok}, name={self.name}, block='{self.block}')"

    def render_to_output(self, context: Context, buffer: TextIO):
        buf = StringIO()
        self.block.render(context, buf)
        context.assign(self.name, buf.getvalue())


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
