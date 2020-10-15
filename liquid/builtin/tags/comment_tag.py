"""Tag and node definition for the built-in "comment" tag."""

import sys

from typing import Optional
from typing import TextIO

from liquid import ast
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import expect
from liquid.parse import eat_block

from liquid.token import Token
from liquid.token import TOKEN_TAG


TAG_COMMENT = sys.intern("comment")
RAG_ENDCOMMENT = sys.intern("endcomment")


class CommentNode(ast.Node):
    """Parse tree node for the built-in "comment" tag."""

    __slots__ = ("tok", "statements")

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "/* */"

    def render_to_output(
        self,
        context: Context,
        buffer: TextIO,
    ) -> Optional[bool]:
        return False


class CommentTag(Tag):
    """The built-in "comment" tag."""

    name = TAG_COMMENT
    end = RAG_ENDCOMMENT

    def parse(self, stream: TokenStream) -> CommentNode:
        expect(stream, TOKEN_TAG, value=TAG_COMMENT)
        stream.next_token()

        tag = CommentNode(stream.current)
        eat_block(stream, end=(RAG_ENDCOMMENT,))

        expect(stream, TOKEN_TAG, value=RAG_ENDCOMMENT)
        return tag
