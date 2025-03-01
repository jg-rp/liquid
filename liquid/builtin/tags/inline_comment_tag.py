"""The built-in inline comment tag."""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

from liquid.builtin.tags.comment_tag import CommentNode
from liquid.exceptions import LiquidSyntaxError
from liquid.tag import Tag
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG

if TYPE_CHECKING:
    from liquid.stream import TokenStream


RE_INVALID_INLINE_COMMENT = re.compile(r"\n\s*[^#\s]")


class InlineCommentNode(CommentNode):
    """The built-in inline comment tag."""

    def __str__(self) -> str:
        return f"{{% # {self.text} %}}"


class InlineCommentTag(Tag):
    """The built-in inline comment tag."""

    block = False
    name = sys.intern("#")
    node_class = InlineCommentNode

    def parse(self, stream: TokenStream) -> InlineCommentNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.expect(TOKEN_TAG)
        # Empty comment tag?
        if stream.peek.kind == TOKEN_EXPRESSION:
            next(stream)
            if RE_INVALID_INLINE_COMMENT.search(stream.current.value):
                raise LiquidSyntaxError(
                    "every line of an inline comment must start with a '#' character",
                    token=stream.current,
                )
        return self.node_class(token, text=stream.current.value)
