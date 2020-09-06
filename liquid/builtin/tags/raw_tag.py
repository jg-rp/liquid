""""""
import sys
from typing import List, TextIO

from liquid.token import Token, TOKEN_EOF, TOKEN_TAG_NAME
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream
from liquid.parse import expect

TAG_RAW = sys.intern("raw")
TAG_ENDRAW = sys.intern("endraw")


class RawNode(ast.Node):
    __slots__ = ("tok", "block")

    def __init__(self, tok: Token, block: List[Token] = None):
        self.tok = tok
        self.block = block or []

    def __str__(self) -> str:
        return "".join(tok.value for tok in self.block)

    def render_to_output(self, context: Context, buffer: TextIO):
        buffer.write(str(self))


class RawTag(Tag):

    name = TAG_RAW
    end = TAG_ENDRAW

    def parse(self, stream: TokenStream) -> RawNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_RAW)
        tag = RawNode(stream.current)
        stream.next_token()

        while (
            stream.current.type != TOKEN_TAG_NAME
            and stream.current.value != TAG_ENDRAW
            and stream.current.type != TOKEN_EOF
        ):
            tag.block.append(stream.current)
            stream.next_token()

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDRAW)
        return tag
