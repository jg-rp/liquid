"""Liquid tag base class."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from liquid.ast import IllegalNode
from liquid.ast import Node
from liquid.exceptions import Error
from liquid.parse import eat_block

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.stream import TokenStream


class Tag(ABC):
    """Base class for all built-in and custom template tags."""

    block = True
    name = ""
    end = ""

    def __init__(self, env: Environment):
        self.env = env

    def get_node(self, stream: TokenStream) -> Node:
        """Wraps `Tag.parse`, possibly returning an `IllegalNode`."""
        token = stream.current
        try:
            return self.parse(stream)
        except Error as err:
            if not err.token:
                err.token = token

            self.env.error(err)

            if self.block and hasattr(self, "end"):
                eat_block(stream, (self.end,))

            return IllegalNode(token)

    @abstractmethod
    def parse(self, stream: TokenStream) -> Node:
        """Return a parse tree node by parsing tokens from the given stream."""
