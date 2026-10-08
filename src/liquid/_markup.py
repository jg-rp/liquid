from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, TextIO

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._parser import Parser
    from ._template import Template
    from .expressions import Name
    from .tokens import Token

type Node = str | Markup
"""A node in a template syntax tree."""

type Block = list[Node]
"""A sequence of template syntax tree nodes."""


class Markup(Protocol):
    """The interface used for *markup nodes* in a template syntax tree.

    All tags and the output statement must implement this interface.
    """

    @property
    def blank(self) -> bool:
        """Return ``True`` if this node renders to an empty string or a string containing
        whitespace only.

        This is used to suppress control flow blocks that don't contain text or markup
        that contributes to the output.
        """
        ...

    @property
    def token(self) -> Token:
        """Return a representative token for this node.

        In the absence of a more specific token from an enclosed expression, this token
        will be used for reporting errors.
        """
        ...

    @property
    def tag(self) -> str:
        """Return the name of this tag, or the empty string if this node is not a tag."""
        ...

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        """Render this node to `buffer` using data from `context`."""
        ...

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        """Render this node to `buffer` asynchronously using data from `context`."""
        ...

    def children(self) -> list[Markup]:
        """Returns markup nodes that are direct children of this node in the syntax tree.

        This is used to traverse template syntax trees during static analysis.
        """
        ...

    async def children_async(self) -> list[Markup]:
        """Returns markup nodes that are direct children of this node in the syntax tree.

        This is used to traverse template syntax trees during static analysis.
        """
        ...

    def expressions(self) -> list[Expression]:
        """Return expression owned by this node."""
        ...

    def block_scope(self) -> list[Name]:
        """Return variable names that are in scope for the duration of this node's block.

        This is used during static analysis to isolate and report global variables.
        """
        ...

    def template_scope(self) -> list[Name]:
        """Return variable names that this tag adds to the template scope."""
        ...

    def partials(self, context: RenderContext) -> list[Partial]:
        """Return meta data about partial templates rendered from this node."""
        ...

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        """Return meta data about partial templates rendered from this node."""
        ...


class Tag(Protocol):
    """The interface used for parsing tokens into markup nodes."""

    @classmethod
    def parse(cls, token: Token, parser: Parser) -> Markup:
        """Parse tokens or text from `parser` into a markup node."""
        ...


class Expression(Protocol):
    @property
    def token(self) -> Token:
        """Return a representative token for this expression.

        It could be the expression's first token or the token for this expression's
        operator, for example.
        """
        ...

    @property
    def span(self) -> Token:
        """Return a token spanning the entire expression."""
        ...

    def evaluate(self, context: RenderContext) -> object:
        """Evaluate this expression using data from `context`."""
        ...

    async def evaluate_async(self, context: RenderContext) -> object:
        """Evaluate this expression asynchronously using data from `context`."""
        ...

    def children(self) -> list[Expression]:
        """Return this expressions direct child expressions."""
        ...


type Scope = Literal[1, 2, 3]

SCOPE_SHARED: Literal[1] = 1
SCOPE_ISOLATED: Literal[2] = 2
SCOPE_INHERITED: Literal[3] = 3


class Partial:
    def __init__(
        self,
        *,
        template: Template,
        scope: Scope,
        in_scope: list[Name],
        key: int,
    ) -> None:
        self.template = template
        self.scope = scope
        self.in_scope = in_scope
        self.key = key


def render_block(block: Block, context: RenderContext, buffer: TextIO) -> None:
    # TODO:
    raise NotImplementedError


async def render_block_async(
    block: Block, context: RenderContext, buffer: TextIO
) -> None:
    # TODO:
    raise NotImplementedError


def is_blank_block(block: Block) -> bool:
    return all(
        node.isspace() if isinstance(node, str) else node.blank for node in block
    )
