"""The built-in _decrement_ tag."""

import sys
from typing import TextIO

from liquid import ast
from liquid.builtin.expressions import parse_identifier
from liquid.context import RenderContext
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_TAG
from liquid.token import Token

TAG_DECREMENT = sys.intern("decrement")


class DecrementNode(ast.Node):
    """The built-in _decrement_ tag."""

    __slots__ = ("name",)

    def __init__(self, token: Token, name: str):
        super().__init__(token)
        self.name = name
        self.blank = False

    def __str__(self) -> str:
        return f"{{% decrement {self.name} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        return buffer.write(str(context.decrement(self.name)))

    def children(self) -> list[ast.ChildNode]:
        """Return this node's expressions."""
        return [
            ast.ChildNode(
                linenum=self.token.start_index,
                template_scope=[self.name],
            )
        ]


class DecrementTag(Tag):
    """The built-in _decrement_ tag."""

    name = TAG_DECREMENT
    block = False
    node_class = DecrementNode

    def parse(self, stream: TokenStream) -> DecrementNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        return self.node_class(
            token,
            name=parse_identifier(self.env, stream.into_inner(eat=False)),
        )
