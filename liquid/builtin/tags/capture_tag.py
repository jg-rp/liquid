""""""
import sys
from io import StringIO
from typing import TextIO

from liquid.token import Token, TOKEN_TAG_NAME, TOKEN_EOF, TOKEN_EXPRESSION
from liquid.parse import expect, get_parser
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream


TAG_CAPTURE = sys.intern("capture")
TAG_ENDCAPTURE = sys.intern("endcapture")

ENDCAPTUREBLOCK = (TAG_ENDCAPTURE, TOKEN_EOF)


class CaptureNode(ast.Node):
    __slots__ = ("tok", "identifier", "block")

    statement = False

    def __init__(self, tok: Token, identifier: str, block: ast.BlockNode = None):
        self.tok = tok
        self.identifier = identifier  # TODO: Validate identifier
        self.block = block

    def __str__(self) -> str:
        return f"var {self.identifier} = {{ {self.block} }}"

    def __repr__(self):  # pragma: no cover
        return f"CaptureNode(tok={self.tok}, identifier={self.identifier}, block='{self.block}')"

    def render_to_output(self, context: Context, buffer: TextIO):
        buf = StringIO()
        self.block.render(context, buf)
        context.assign(str(self.identifier), buf.getvalue())


class CaptureTag(Tag):

    name = TAG_CAPTURE
    end = TAG_ENDCAPTURE

    def parse(self, stream: TokenStream) -> CaptureNode:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_CAPTURE)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        node = CaptureNode(tok, stream.current.value)
        stream.next_token()

        node.block = parser.parse_block(stream, ENDCAPTUREBLOCK)

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDCAPTURE)
        return node
