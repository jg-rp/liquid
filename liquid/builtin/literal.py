"""Pseudo tag and node definition for template literals."""

from typing import List
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_LITERAL
from liquid.token import Token


class LiteralNode(Node):
    """Parse tree node for template literals."""

    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return self.tok.value

    def __repr__(self) -> str:  # pragma: no cover
        return f"LiteralNode(tok={self.tok})"

    def render_to_output(  # noqa: D102
        self, _: Context, buffer: TextIO
    ) -> Optional[bool]:
        buffer.write(self.tok.value)
        return None

    def children(self) -> List[ChildNode]:  # noqa: D102
        return []


class Literal(Tag):
    """Pseudo "tag" for template literals."""

    name = TOKEN_LITERAL
    node_class = LiteralNode

    def parse(self, stream: TokenStream) -> LiteralNode:  # noqa: D102
        return self.node_class(stream.current)
