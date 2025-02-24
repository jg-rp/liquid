"""Pseudo tag and node definition for template content."""

from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.context import RenderContext
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_LITERAL


class ContentNode(Node):
    """Parse tree node for template content."""

    def __str__(self) -> str:
        return self.token.value

    def render_to_output(  # noqa: D102
        self, _: RenderContext, buffer: TextIO
    ) -> int:
        return buffer.write(self.token.value)

    def children(self) -> list[ChildNode]:  # noqa: D102
        return []


class Literal(Tag):
    """Pseudo "tag" for template content."""

    name = TOKEN_LITERAL
    node_class = ContentNode

    def parse(self, stream: TokenStream) -> ContentNode:  # noqa: D102
        return self.node_class(stream.current)
