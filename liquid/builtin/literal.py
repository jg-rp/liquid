"""Parse tree node and pseudo "tag" for template literals."""

from typing import TextIO

from liquid.token import Token
from liquid.token import TOKEN_LITERAL
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream


class LiteralNode(ast.Node):
    """Parse tree node representing a template literal."""

    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return self.tok.value

    def __repr__(self) -> str:  # pragma: no cover
        return f"LiteralNode(tok={self.tok})"

    def render_to_output(self, context: Context, buffer: TextIO):
        buffer.write(self.tok.value)


class Literal(Tag):
    """Pseudo "tag" to register template literals with the environment."""

    name = TOKEN_LITERAL

    def parse(self, stream: TokenStream) -> LiteralNode:
        return LiteralNode(stream.current)
