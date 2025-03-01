"""Pseudo tag and node definition for template content."""

from typing import TextIO

from liquid.ast import Node
from liquid.context import RenderContext
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_CONTENT
from liquid.token import Token


class ContentNode(Node):
    """Parse tree node for template content."""

    __slots__ = ("text",)

    def __init__(self, token: Token, text: str):
        super().__init__(token)
        self.blank = not text or text.isspace()
        self.text = text

    def __str__(self) -> str:
        return self.text

    def render_to_output(self, _: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        return buffer.write(self.text)


class Literal(Tag):
    """Pseudo "tag" for template content."""

    name = TOKEN_CONTENT
    block = False
    node_class = ContentNode

    def parse(self, stream: TokenStream) -> ContentNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.expect(TOKEN_CONTENT)
        return self.node_class(token, token.value)
