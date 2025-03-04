"""The built-in _increment_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import TextIO

from liquid.ast import Node
from liquid.builtin.expressions import parse_identifier
from liquid.tag import Tag
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.builtin.expressions import Identifier
    from liquid.context import RenderContext
    from liquid.stream import TokenStream


TAG_INCREMENT = sys.intern("increment")


class IncrementNode(Node):
    """The built-in _increment_ tag."""

    __slots__ = ("name",)

    def __init__(self, token: Token, name: Identifier):
        super().__init__(token)
        self.name = name
        self.blank = False

    def __str__(self) -> str:
        return f"{{% increment {self.name} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        return buffer.write(str(context.increment(self.name)))

    def template_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the template local scope."""
        yield self.name


class IncrementTag(Tag):
    """The built-in _increment_ tag."""

    name = TAG_INCREMENT
    block = False
    node_class = IncrementNode

    def parse(self, stream: TokenStream) -> IncrementNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        return self.node_class(
            token,
            name=parse_identifier(self.env, stream.into_inner(tag=token, eat=False)),
        )
