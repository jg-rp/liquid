"""Tag an node definition for the built-in "inline comment" tag."""
import re
import sys

from liquid.builtin.tags.comment_tag import CommentNode
from liquid.exceptions import LiquidSyntaxError
from liquid.parse import expect
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG

RE_INVALID_INLINE_COMMENT = re.compile(r"\n\s*[^#\s]")


class InlineCommentTag(Tag):
    """The built-in inline comment ("#") tag."""

    block = False
    name = sys.intern("#")
    node_class = CommentNode

    def parse(self, stream: TokenStream) -> CommentNode:  # noqa: D102
        expect(stream, TOKEN_TAG, value=self.name)
        tok = stream.current
        # Empty comment tag?
        if stream.peek.type == TOKEN_EXPRESSION:
            next(stream)
            if RE_INVALID_INLINE_COMMENT.search(stream.current.value):
                raise LiquidSyntaxError(
                    "every line of an inline comment must start with a '#' character",
                    linenum=stream.current.linenum,
                )
        return self.node_class(tok, text=stream.current.value)
