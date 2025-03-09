"""Base class for all template nodes."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from enum import Enum
from enum import auto
from typing import TYPE_CHECKING
from typing import Collection
from typing import Iterable
from typing import TextIO

from .exceptions import DisabledTagError
from .output import NullIO
from .token import TOKEN_TAG
from .token import Token

if TYPE_CHECKING:
    from .builtin.expressions import Identifier
    from .context import RenderContext
    from .expression import Expression


class Node(ABC):
    """Base class for all nodes in a parse tree."""

    __slots__ = ("token", "blank")

    def __init__(self, token: Token) -> None:
        self.token = token

        self.blank = True
        """If True, indicates that the node, when rendered, produces no output text
        or only whitespace.
        
        The output node (`{{ something }}`) and echo tag are exception. Even if they
        evaluate to an empty or blank string, they are not considered "blank".
        """

    def raise_for_disabled(self, disabled_tags: Collection[str]) -> None:
        """Raise a DisabledTagError if this node's type is in the given list."""
        if self.token.kind == TOKEN_TAG and self.token.value in disabled_tags:
            raise DisabledTagError(
                f"{self.token.value} usage is not allowed in this context",
                token=self.token,
            )

    def render(self, context: RenderContext, buffer: TextIO) -> int:
        """Check disabled tags before delegating to `render_to_output`."""
        if context.disabled_tags:
            self.raise_for_disabled(context.disabled_tags)
        return self.render_to_output(context, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> int:
        """An async version of `liquid.ast.Node.render`."""
        if context.disabled_tags:
            self.raise_for_disabled(context.disabled_tags)
        return await self.render_to_output_async(context, buffer)

    @abstractmethod
    def render_to_output(
        self,
        context: RenderContext,
        buffer: TextIO,
    ) -> int:
        """Render this node to the output buffer."""

    async def render_to_output_async(
        self,
        context: RenderContext,
        buffer: TextIO,
    ) -> int:
        """An async version of `liquid.ast.Node.render_to_output`."""
        return self.render_to_output(context, buffer)

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        return []

    async def children_async(
        self,
        static_context: RenderContext,
        *,
        include_partials: bool = True,
    ) -> Iterable[Node]:
        """An async version of `children()`."""
        return self.children(static_context, include_partials=include_partials)

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        return []

    def template_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the template local scope."""
        return []

    def block_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the node's block scope."""
        return []

    def partial_scope(self) -> Partial | None:
        """Return information about a partial template loaded by this node."""
        return None


class PartialScope(Enum):
    """The kind of scope a partial template should have when loaded."""

    SHARED = auto()
    ISOLATED = auto()
    INHERITED = auto()


class Partial:
    """Partial template meta data.

    Args:
        name: An expression resolving to the name associated with the partial template.
        scope: The kind of scope the partial template should have when loaded.
        in_scope: Names that will be added to the partial template scope.
    """

    __slots__ = ("name", "scope", "in_scope")

    def __init__(
        self, name: Expression, scope: PartialScope, in_scope: Iterable[Identifier]
    ) -> None:
        self.name = name
        self.scope = scope
        self.in_scope = in_scope


class IllegalNode(Node):
    """Parse tree node representing an illegal or unregistered tag.

    Illegal nodes are necessary when running in "warn" or "lax" mode. In
    strict mode, an exception should be raised as soon as an illegal token
    is found.
    """

    __slots__ = ()

    def __str__(self) -> str:
        return ""

    def render_to_output(self, _context: RenderContext, _buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        return 0


class BlockNode(Node):
    """A parse tree node representing a sequence of statements."""

    __slots__ = ("nodes", "blank")

    def __init__(self, token: Token, nodes: list[Node]):
        super().__init__(token)
        self.nodes = nodes
        self.blank = all(node.blank for node in nodes)

    def __str__(self) -> str:
        return "".join(str(s) for s in self.nodes)

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        if context.env.suppress_blank_control_flow_blocks and self.blank:
            buf = NullIO()
            for node in self.nodes:
                node.render(context, buf)
            return 0
        return sum(node.render(context, buffer) for node in self.nodes)

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        if context.env.suppress_blank_control_flow_blocks and self.blank:
            buf = NullIO()
            for node in self.nodes:
                await node.render_async(context, buf)
            return 0
        return sum([await node.render_async(context, buffer) for node in self.nodes])

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        return self.nodes


class ConditionalBlockNode(Node):
    """A node containing a sequence of statements and a conditional expression."""

    __slots__ = ("expression", "block")

    def __init__(self, token: Token, expression: Expression, block: BlockNode):
        super().__init__(token)
        self.expression = expression
        self.block = block
        self.blank = block.blank

    def __str__(self) -> str:
        return f"{{% elsif {self.expression} %}}{self.block}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        if self.expression.evaluate(context):
            return self.block.render(context, buffer)
        return 0

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        if await self.expression.evaluate_async(context):
            return await self.block.render_async(context, buffer)
        return 0

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.block

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.expression
