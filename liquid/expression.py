"""The base class for all built-in expressions."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context import RenderContext
    from .token import Token


class Expression(ABC):
    """The base class for all built-in expressions."""

    __slots__ = ("token",)

    def __init__(self, token: Token):
        self.token = token

    @abstractmethod
    def evaluate(self, context: RenderContext) -> object:
        """Evaluate this expression an return the result."""

    async def evaluate_async(self, context: RenderContext) -> object:
        """Evaluate this expression asynchronously."""
        return self.evaluate(context)

    def children(self) -> list[Expression]:
        """Return a list of expressions that are children of this expression."""
        raise NotImplementedError(f"{self.__class__.__name__}.children")
