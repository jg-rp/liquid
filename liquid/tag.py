"""Liquid tag base class."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from .ast import IllegalNode
from .ast import Node
from .exceptions import LiquidError
from .parser import eat_block

if TYPE_CHECKING:
    from .environment import Environment
    from .stream import TokenStream


class Tag(ABC):
    """Base class for all built-in and custom template tags."""

    block = True
    name = ""
    end = ""

    def __init__(self, env: Environment):
        self.env = env

    def get_node(self, stream: TokenStream) -> Node:
        """Wraps `Tag.parse`, possibly returning an `IllegalNode`."""
        try:
            return self.parse(stream)
        except LiquidError as err:
            token = stream.current
            if not err.token:
                err.token = token

            self.env.error(err)

            if self.block and hasattr(self, "end"):
                eat_block(stream, (self.end,))

            return IllegalNode(token)

    @abstractmethod
    def parse(self, stream: TokenStream) -> Node:
        """Return a parse tree node by parsing tokens from the given stream."""
