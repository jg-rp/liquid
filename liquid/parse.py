"""Liquid template parser."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Container

from .ast import BlockNode
from .ast import IllegalNode
from .ast import Node
from .ast import ParseTree
from .exceptions import Error
from .exceptions import LiquidSyntaxError
from .token import TOKEN_EOF
from .token import TOKEN_ILLEGAL
from .token import TOKEN_LITERAL
from .token import TOKEN_STATEMENT
from .token import TOKEN_TAG

if TYPE_CHECKING:
    from .environment import Environment
    from .stream import TokenStream


class Parser:
    """A Liquid template parser. Create a parse tree from a stream of tokens."""

    __slots__ = ("tags", "illegal", "literal", "statement", "env")

    def __init__(self, env: Environment):
        self.tags = env.tags
        self.env = env

        self.illegal = self.tags[TOKEN_ILLEGAL]
        self.literal = self.tags[TOKEN_LITERAL]
        self.statement = self.tags[TOKEN_STATEMENT]

    def parse(self, stream: TokenStream) -> ParseTree:
        """Parse the given stream of tokens into a tree."""
        root = ParseTree()
        statements = root.statements

        # TODO: factor in parse_statement
        # TODO: benchmark with local tag vars
        while stream.current.type != TOKEN_EOF:
            try:
                statements.append(self.parse_statement(stream))
            except Error as err:
                self.env.error(err, linenum=stream.current.linenum)

            stream.next_token()

        return root

    def parse_statement(self, stream: TokenStream) -> Node:
        """Parse a node from a stream of tokens."""
        if stream.current.type == TOKEN_STATEMENT:
            node = self.statement.get_node(stream)
        elif stream.current.type == TOKEN_TAG:
            tag = self.tags.get(stream.current.value, self.illegal)
            node = tag.get_node(stream)

            # Tag parse functions can choose to return an IllegalNode.
            if isinstance(node, IllegalNode):
                raise LiquidSyntaxError(
                    f"unexpected tag '{node.token().value}'",
                    linenum=node.token().linenum,
                )
        else:
            node = self.literal.get_node(stream)

        return node

    def parse_block(self, stream: TokenStream, end: Container[str]) -> BlockNode:
        """Parse multiple nodes from a stream of tokens.

        Stop parsing nodes when we find a token in `end` or we reach the end of the
        stream.
        """
        block = BlockNode(stream.current)
        statements = block.statements

        while stream.current.type != TOKEN_EOF:
            if stream.current.type == TOKEN_TAG and stream.current.value in end:
                break
            stmt = self.parse_statement(stream)
            statements.append(stmt)
            # Detect output nodes in any of this block's children. This is used by
            # some tags to automatically suppress whitespace when no other output is
            # present.
            if (
                self.env.render_whitespace_only_blocks
                or stmt.force_output
                or getattr(stmt, "forced_output", False)
            ):
                block.forced_output = True
            stream.next_token()

        return block


# TODO: move to TokenStream.eat_block()
def eat_block(stream: TokenStream, end: Container[str]) -> None:
    """Advance the stream pointer past the next end tag.

    This is used to discard blocks after a syntax error is found, in the hope
    that we can continue to parse more of the stream after the offending block.
    """
    while stream.current.type != TOKEN_EOF:
        if stream.current.type == TOKEN_TAG and stream.current.value in end:
            break
        stream.next_token()


@lru_cache(maxsize=128)
def get_parser(env: Environment) -> Parser:
    """Return a template parser for the given environment."""
    return Parser(env)
