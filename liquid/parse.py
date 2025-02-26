"""Liquid template parser."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Container

from .ast import BlockNode
from .ast import IllegalNode
from .ast import Node
from .exceptions import Error
from .exceptions import LiquidSyntaxError
from .token import TOKEN_CONTENT
from .token import TOKEN_EOF
from .token import TOKEN_ILLEGAL
from .token import TOKEN_OUTOUT
from .token import TOKEN_TAG

if TYPE_CHECKING:
    from .environment import Environment
    from .stream import TokenStream


class Parser:
    """A Liquid template parser. Create a parse tree from a stream of tokens."""

    __slots__ = ("tags", "illegal", "content", "statement", "env")

    def __init__(self, env: Environment):
        self.tags = env.tags
        self.env = env

        self.illegal = self.tags[TOKEN_ILLEGAL]
        self.content = self.tags[TOKEN_CONTENT]
        self.statement = self.tags[TOKEN_OUTOUT]

    def parse(self, stream: TokenStream) -> list[Node]:
        """Parse the given stream of tokens into a tree."""
        nodes: list[Node] = []

        # TODO: factor in parse_statement
        # TODO: benchmark with local tag vars
        while stream.current.kind != TOKEN_EOF:
            try:
                nodes.append(self.parse_statement(stream))
            except Error as err:
                self.env.error(err, token=stream.current)

        next(stream)

        return nodes

    def parse_statement(self, stream: TokenStream) -> Node:
        """Parse a node from a stream of tokens."""
        if stream.current.kind == TOKEN_OUTOUT:
            node = self.statement.get_node(stream)
        elif stream.current.kind == TOKEN_TAG:
            tag = self.tags.get(stream.current.value, self.illegal)
            node = tag.get_node(stream)

            # Tag parse functions can choose to return an IllegalNode.
            if isinstance(node, IllegalNode):
                raise LiquidSyntaxError(
                    f"unexpected tag '{node.token.value}'",
                    token=node.token,
                )
        else:
            node = self.content.get_node(stream)

        return node

    def parse_block(self, stream: TokenStream, end: Container[str]) -> BlockNode:
        """Parse multiple nodes from a stream of tokens.

        Stop parsing nodes when we find a token in `end` or we reach the end of the
        stream.
        """
        block = BlockNode(stream.current, [])
        nodes = block.nodes

        while stream.current.kind != TOKEN_EOF:
            if stream.current.kind == TOKEN_TAG and stream.current.value in end:
                break
            nodes.append(self.parse_statement(stream))
            next(stream)

        return block


# TODO: move to TokenStream.eat_block()
def eat_block(stream: TokenStream, end: Container[str]) -> None:
    """Advance the stream pointer past the next end tag.

    This is used to discard blocks after a syntax error is found, in the hope
    that we can continue to parse more of the stream after the offending block.
    """
    while stream.current.kind != TOKEN_EOF:
        if stream.current.kind == TOKEN_TAG and stream.current.value in end:
            break
        stream.next_token()


@lru_cache(maxsize=128)
def get_parser(env: Environment) -> Parser:
    """Return a template parser for the given environment."""
    return Parser(env)
