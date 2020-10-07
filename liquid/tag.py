from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol, Union, Type, Optional, Any

from liquid.ast import IllegalNode
from liquid.exceptions import Error
from liquid.parse import eat_block
from liquid import ast
from liquid.stream import TokenStream


class Env(Protocol):
    def error(
        self: Any,
        exc: Union[Type[Error], Error],
        msg: Optional[str] = ...,
        linenum: Optional[int] = ...,
    ) -> None:
        ...


class Tag(ABC):

    block = True
    name = ""

    def __init__(self, env: Env):
        """
        Args:
            block: If True, indicates that this tag is a block tag, where we
                expect an "end" tag to follow and enclose more literals,
                statements or tags.
        """

        self.env = env

    @abstractmethod
    def parse(self, stream: TokenStream) -> ast.Node:
        """Build a parse tree node from a stream of tokens."""

    def get_node(self, stream: TokenStream) -> ast.Node:
        """Return an IllegalNode if an error is raised when calling `parse`."""
        tok = stream.current
        try:
            return self.parse(stream)
        except Error as err:
            if not err.linenum:
                err.linenum = tok.linenum

            self.env.error(err)

            if self.block and hasattr(self, "end"):
                eat_block(stream, (getattr(self, "end"),))

            return IllegalNode(tok)
