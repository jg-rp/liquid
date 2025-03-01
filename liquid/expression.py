"""The base class for all built-in expressions."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Iterable

if TYPE_CHECKING:
    from .builtin.expressions import Identifier
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

    @abstractmethod
    def children(self) -> Iterable[Expression]:
        """Return this expression's child expressions."""

    def scope(self) -> Iterable[Identifier]:
        """Return variables this expression adds the scope of any child expressions.

        Used by lambda expressions only.
        """
        return []
