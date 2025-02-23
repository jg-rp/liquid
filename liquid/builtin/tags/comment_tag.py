"""The built-in _comment_ tag."""

import sys
from typing import Optional
from typing import TextIO

from liquid import ast
from liquid.context import RenderContext
from liquid.parse import eat_block
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG
from liquid.token import Token

# ruff: noqa: D102

TAG_COMMENT = sys.intern("comment")
TAG_ENDCOMMENT = sys.intern("endcomment")

END_COMMENTBLOCK = frozenset((TAG_ENDCOMMENT,))


class CommentNode(ast.Node):
    """The built-in _comment_ tag."""

    __slots__ = ("text",)

    def __init__(self, token: Token, text: Optional[str] = None):
        super().__init__(token)
        self.text = text

    def __str__(self) -> str:
        return f"{{% comment %}}{self.text}{{% endcomment %}}"

    def render_to_output(self, _: RenderContext, __: TextIO) -> int:
        return 0

    def children(self) -> list[ast.ChildNode]:
        return []


class CommentTag(Tag):
    """The built-in _comment_ tag.

    This implementation does not include comment text in the resulting
    AST node.
    """

    name = TAG_COMMENT
    end = TAG_ENDCOMMENT
    node_class = CommentNode

    def parse(self, stream: TokenStream) -> CommentNode:
        node = self.node_class(stream.eat(TOKEN_TAG))
        eat_block(stream, end=END_COMMENTBLOCK)
        return node


class CommentTextTag(CommentTag):
    """An implementation of the built-in _comment_ tag that retains comment text.

    Some Liquid markup might be stripped out by the lexer, so comment text is not
    guaranteed to be identical to that in the source document.
    """

    name = TAG_COMMENT
    end = TAG_ENDCOMMENT

    def parse(self, stream: TokenStream) -> CommentNode:
        token = stream.eat(TOKEN_TAG)

        text = []
        while stream.current.kind != TOKEN_EOF:
            if (
                stream.current.kind == TOKEN_TAG
                and stream.current.value == TAG_ENDCOMMENT
            ):
                break
            text.append(stream.current.value)
            next(stream)

        return self.node_class(token, text="".join(text))
