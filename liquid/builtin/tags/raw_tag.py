""""""
import sys

from liquid.token import TOKEN_TAG_NAME
from liquid.tag import Tag
from liquid.lex import TokenStream
from liquid.parse import expect
from liquid.builtin.literal import LiteralNode

TAG_RAW = sys.intern("raw")
TAG_ENDRAW = sys.intern("endraw")


class RawTag(Tag):

    name = TAG_RAW
    end = TAG_ENDRAW

    def parse(self, stream: TokenStream) -> LiteralNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_RAW)
        stream.next_token()

        tag = LiteralNode(stream.current)
        stream.next_token()

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDRAW)
        return tag
