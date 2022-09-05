"""Tag and node definition for the built-in "comment" tag."""

import sys

from typing import List
from typing import Optional
from typing import TextIO

from liquid import ast
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import expect
from liquid.parse import eat_block

from liquid.token import Token
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG


TAG_COMMENT = sys.intern("comment")
TAG_ENDCOMMENT = sys.intern("endcomment")

END_COMMENTBLOCK = frozenset((TAG_ENDCOMMENT,))


class CommentNode(ast.Node):
    """Parse tree node for the built-in "comment" tag."""

    __slots__ = ("tok", "text")

    def __init__(self, tok: Token, text: Optional[str] = None):
        self.tok = tok
        self.text = text

    def __str__(self) -> str:
        if self.text:
            return f"/* {self.text} */"
        return "/* */"

    def render_to_output(
        self,
        context: Context,
        buffer: TextIO,
    ) -> Optional[bool]:
        return False

    def children(self) -> List[ast.ChildNode]:
        return []


class CommentTag(Tag):
    """The built-in "comment" tag.

    This implementation does not include comment text in the resulting
    AST node.
    """

    name = TAG_COMMENT
    end = TAG_ENDCOMMENT

    def parse(self, stream: TokenStream) -> CommentNode:
        expect(stream, TOKEN_TAG, value=TAG_COMMENT)
        stream.next_token()
        node = CommentNode(stream.current)
        eat_block(stream, end=END_COMMENTBLOCK)
        return node


class CommentTextTag(CommentTag):
    """An implementation of the built-in "comment" tag that includes
    comment text in a template's AST.

    Some Liquid markup might be stripped out by the lexer, so comment
    text is not guaranteed to be identical to that in the source document.
    """

    name = TAG_COMMENT
    end = TAG_ENDCOMMENT

    def parse(self, stream: TokenStream) -> CommentNode:
        expect(stream, TOKEN_TAG, value=TAG_COMMENT)
        stream.next_token()
        tok = stream.current

        text = []
        while stream.current.type != TOKEN_EOF:
            if (
                stream.current.type == TOKEN_TAG
                and stream.current.value == TAG_ENDCOMMENT
            ):
                break
            text.append(stream.current.value)
            stream.next_token()

        return CommentNode(tok, text="".join(text))
