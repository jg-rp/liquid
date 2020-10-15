from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Protocol
from typing import Union
from typing import Type
from typing import Optional
from typing import Any

from liquid.ast import Node
from liquid.ast import IllegalNode
from liquid.exceptions import Error
from liquid.parse import eat_block
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
    """Base class for all built-in and custom template tags."""

    block = True
    name = ""

    def __init__(self, env: Env):
        self.env = env

    def get_node(self, stream: TokenStream) -> Node:
        """Wraps `Tag.parse`, possibly returning an `IllegalNode`."""
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

    @abstractmethod
    def parse(self, stream: TokenStream) -> Node:
        """Return a parse tree node py parsing tokens from the given stream."""
