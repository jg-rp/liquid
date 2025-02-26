"""Base class for all template nodes."""

from abc import ABC
from abc import abstractmethod
from typing import Collection
from typing import Literal
from typing import NamedTuple
from typing import Optional
from typing import TextIO

from .context import RenderContext
from .exceptions import DisabledTagError
from .expression import Expression
from .output import NullIO
from .token import TOKEN_ILLEGAL
from .token import TOKEN_TAG
from .token import Token

IllegalToken = Token(TOKEN_ILLEGAL, "", -1, "")  # XXX


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
        # TODO: benchmark local `token`
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
        if hasattr(self, "render_to_output_async"):
            return await self.render_to_output_async(context, buffer)
        return self.render_to_output(context, buffer)

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

    def children(self) -> list["ChildNode"]:
        """Return a list of child nodes and/or expressions associated with this node."""
        raise NotImplementedError(f"{self.__class__.__name__}.children")


# TODO: rewrite
class ChildNode(NamedTuple):
    """An AST node and expression pair with optional scope and load data.

    Args:
        linenum: The line number of the child's first token in the template source text.
        expression: An `liquid.expression.Expression`. If not `None`, this expression is
            expected to be related to the given `liquid.ast.Node`.
        node: A `liquid.ast.Node`. Typically a `BlockNode` or `ConditionalBlockNode`.
        template_scope: A list of names the parent node adds to the template "local"
            scope. For example, the built-in `assign`, `capture`, `increment` and
            `decrement` tags all add names to the template scope. This helps us
            identify, through static analysis, names that are assumed to be "global".
        block_scope: A list of names available to the given child node. For example,
            the `for` tag adds the name "forloop" for the duration of its block.
        load_mode: If not `None`, indicates that the given expression should be used to
            load a partial template. In "render" mode, the partial will be analyzed in
            an isolated namespace, without access to the parent's template local scope.
            In "include" mode, the partial will have access to the parents template
            local scope and the parent's scope can be updated by the partial template
            too.
        load_context: Meta data a template `Loader` might need to find the source
            of a partial template.
    """

    linenum: int
    expression: Optional[Expression] = None
    node: Optional[Node] = None
    template_scope: Optional[list[str]] = None
    block_scope: Optional[list[str]] = None
    load_mode: Optional[Literal["render", "include", "extends"]] = None
    load_context: Optional[dict[str, str]] = None


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
        # TODO: resume rendering node if mode.lax
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

    def children(self) -> list["ChildNode"]:
        """Return this node's children."""
        return [
            ChildNode(
                linenum=self.token.start_index,
                node=stmt,
            )
            for stmt in self.nodes
        ]


class ConditionalBlockNode(Node):
    """A node containing a sequence of statements and a conditional expression."""

    __slots__ = ("condition", "block")

    def __init__(self, token: Token, condition: Expression, block: BlockNode):
        super().__init__(token)
        self.condition = condition
        self.block = block
        self.blank = block.blank

    def __str__(self) -> str:
        # TODO: WC
        return f"{{% elsif {self.condition} %}}{self.block}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        if self.condition.evaluate(context):
            return self.block.render(context, buffer)
        return 0

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        if await self.condition.evaluate_async(context):
            return await self.block.render_async(context, buffer)
        return 0

    def children(self) -> list["ChildNode"]:
        """Return this node's children."""
        return [
            ChildNode(
                linenum=self.token.start_index,
                node=self.block,
                expression=self.condition,
            )
        ]
