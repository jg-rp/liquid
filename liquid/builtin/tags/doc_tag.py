"""The built-in _doc_ tag."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional
from typing import TextIO

from liquid.ast import Node
from liquid.exceptions import LiquidSyntaxError
from liquid.tag import Tag
from liquid.token import TOKEN_DOC
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG

if TYPE_CHECKING:
    from liquid import RenderContext
    from liquid import TokenStream
    from liquid.token import Token


class DocNode(Node):
    """The built-in _doc_ tag."""

    def __init__(self, token: Token, text: Optional[str] = None):
        super().__init__(token)
        self.text = text

    def __str__(self) -> str:
        return f"{{% doc %}}{self.text}{{% enddoc %}}"

    def render_to_output(self, _: RenderContext, __: TextIO) -> int:
        """Render the node to the output buffer."""
        return 0


class DocTag(Tag):
    """The built-in _doc_ tag."""

    block = True
    name = "doc"
    end = "enddoc"
    node_class = DocNode

    def parse(self, stream: TokenStream) -> DocNode:
        """Parse tokens from _stream_ into an AST node."""
        if stream.current.kind == TOKEN_DOC:
            return self.node_class(stream.current, text=stream.current.value)

        # This only happens if the doc tag is malformed
        token = stream.eat(TOKEN_TAG)
        text = []

        if stream.current.kind == TOKEN_EXPRESSION:
            raise LiquidSyntaxError("unexpected expression", token=stream.current)

        while True:
            if stream.current.is_tag(self.name):
                raise LiquidSyntaxError("nested doc tags are not allowed", token=token)
            if stream.current.is_tag(self.end):
                break
            if stream.current.kind == TOKEN_EOF:
                raise LiquidSyntaxError("doc tag wad never closed", token=token)
            text.append(stream.current.value)
            next(stream)

        return self.node_class(token, text="".join(text))
