from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._io import StringBuffer
    from ._markup import Expression, Markup, Partial
    from ._parser import Parser
    from .expressions import Name
    from .tokens import Token


class AbstractTag(ABC):
    """An abstract class for implementing custom tags.

    It is not necessary to inherit from `AbstractTag` when implementing custom tags, but
    it can be convenient if you're not interested in methods supporting static template
    analysis, saving you from writing several empty methods.

    Internally we use the `Markup` and `Tag` protocols, without a required base class.
    """

    @classmethod
    @abstractmethod
    def parse(cls, token: Token, parser: Parser) -> Markup:
        """Parse tokens or text from `parser` into a markup node."""

    @abstractmethod
    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        """Render this node to `buffer` using data from `context`."""

    @abstractmethod
    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        """Render this node to `buffer` asynchronously using data from `context`."""

    def children(self) -> list[Markup]:
        """Returns markup nodes that are direct children of this node in the syntax tree.

        This is used to traverse template syntax trees during static analysis.
        """
        return []

    def expressions(self) -> list[Expression]:
        """Return expression owned by this node."""
        return []

    def block_scope(self) -> list[Name]:
        """Return variable names that are in scope for the duration of this node's block.

        This is used during static analysis to isolate and report global variables.
        """
        return []

    def template_scope(self) -> list[Name]:
        """Return variable names that this tag adds to the template scope."""
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        """Return meta data about partial templates rendered from this node."""
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        """Return meta data about partial templates rendered from this node."""
        return []
