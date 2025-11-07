"""The built-in _snippet_ tag.

New in Python Liquid version 2.2.0.
New in Shopify/liquid version 5.10.0.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.builtin.expressions import parse_identifier
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.template import BoundTemplate
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from collections.abc import Iterable

    from liquid.builtin.expressions import Identifier
    from liquid.context import RenderContext
    from liquid.stream import TokenStream


class SnippetNode(Node):
    """The built-in _snippet_ tag."""

    __slots__ = ("name", "block")

    def __init__(self, token: Token, name: Identifier, block: BlockNode):
        super().__init__(token)
        self.name = name
        self.block = block

    def __str__(self) -> str:
        return f"{{% snippet {self.name} %}}{self.block}{{% endsnippet %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:  # noqa: ARG002
        """Render the node to the output buffer."""
        # Don't render anything, just bind the block to its name.
        context.assign(
            self.name,
            SnippetDrop(
                context.env,
                self.block.nodes,
                context.template.name,
                context.template.path,
            ),
        )
        return 0

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        # Snippets are only visited when rendered so we get accurate variable
        # scope analysis.
        static_context.assign(
            self.name,
            SnippetDrop(
                static_context.env,
                self.block.nodes,
                static_context.template.name,
                static_context.template.path,
            ),
        )
        return []

    def template_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the template local scope."""
        yield self.name


class SnippetTag(Tag):
    """The built-in _snippet_ tag."""

    block = True
    name = "snippet"
    end = "endsnippet"
    node_class = SnippetNode

    ENDSNIPPETBLOCK = frozenset((end, TOKEN_EOF))

    def parse(self, stream: TokenStream) -> SnippetNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token)
        name = parse_identifier(self.env, tokens)
        tokens.expect_eos()
        block = get_parser(self.env).parse_block(stream, self.ENDSNIPPETBLOCK)
        stream.expect(TOKEN_TAG, value=self.end)
        return self.node_class(token, name, block)


class SnippetDrop(BoundTemplate):
    """An template suitable for storing in a render context."""

    def __str__(self) -> str:
        return "SnippetDrop"
