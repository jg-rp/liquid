"""Liquid template parser."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Container
from typing import Iterator

from .ast import BlockNode
from .ast import Node
from .exceptions import LiquidError
from .token import TOKEN_COMMENT
from .token import TOKEN_CONTENT
from .token import TOKEN_DOC
from .token import TOKEN_EOF
from .token import TOKEN_ILLEGAL
from .token import TOKEN_OUTPUT
from .token import TOKEN_TAG

if TYPE_CHECKING:
    from .environment import Environment
    from .stream import TokenStream


class Parser:
    """A Liquid template parser. Create a parse tree from a stream of tokens."""

    __slots__ = ("env",)

    def __init__(self, env: Environment):
        self.env = env

    def parse(self, stream: TokenStream) -> list[Node]:
        """Parse tokens from _stream_ into a list of nodes."""
        return list(self._parse(stream))

    def _parse(self, stream: TokenStream) -> Iterator[Node]:
        tags = self.env.tags
        illegal = tags[TOKEN_ILLEGAL]
        content = tags[TOKEN_CONTENT]
        output = tags[TOKEN_OUTPUT]

        while stream.current.kind != TOKEN_EOF:
            token = stream.current
            kind = token.kind

            try:
                if kind == TOKEN_OUTPUT:
                    yield output.get_node(stream)
                elif kind == TOKEN_DOC:
                    yield tags.get(TOKEN_DOC, illegal).get_node(stream)
                elif stream.current.kind == TOKEN_TAG:
                    yield tags.get(token.value, illegal).get_node(stream)
                elif kind == "COMMENT":
                    yield tags.get(TOKEN_COMMENT, illegal).get_node(stream)
                else:
                    yield content.get_node(stream)
            except LiquidError as err:
                self.env.error(err, token=stream.current)

            next(stream)

    def parse_block(self, stream: TokenStream, end: Container[str]) -> BlockNode:
        """Parse tokens from _stream_ until we reach a token in _end_."""
        tags = self.env.tags
        illegal = tags[TOKEN_ILLEGAL]
        content = tags[TOKEN_CONTENT]
        output = tags[TOKEN_OUTPUT]

        nodes: list[Node] = []

        while stream.current.kind != TOKEN_EOF:
            if stream.current.kind == TOKEN_TAG and stream.current.value in end:
                break
            token = stream.current
            kind = token.kind

            try:
                if kind == TOKEN_OUTPUT:
                    nodes.append(output.get_node(stream))
                elif kind == TOKEN_DOC:
                    nodes.append(tags.get(TOKEN_DOC, illegal).get_node(stream))
                elif stream.current.kind == TOKEN_TAG:
                    nodes.append(tags.get(token.value, illegal).get_node(stream))
                elif kind == "COMMENT":
                    nodes.append(tags.get(TOKEN_COMMENT, illegal).get_node(stream))
                else:
                    nodes.append(content.get_node(stream))
            except LiquidError as err:
                self.env.error(err, token=stream.current)

            next(stream)

        return BlockNode(stream.current, nodes)


def eat_block(stream: TokenStream, end: Container[str]) -> None:
    """Advance the stream until we reach a token in _end_.

    This is used to discard blocks after a syntax error is found, in the hope
    that we can continue to parse more of the stream after the offending block.
    """
    while stream.current.kind != TOKEN_EOF:
        if stream.current.kind == TOKEN_TAG and stream.current.value in end:
            break
        next(stream)


@lru_cache(maxsize=128)
def get_parser(env: Environment) -> Parser:
    """Return a template parser for the given environment."""
    return Parser(env)
