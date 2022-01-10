"""Common parse tree nodes."""

from abc import ABC
from abc import abstractmethod

from typing import Collection
from typing import List
from typing import Optional
from typing import TextIO

from liquid.context import Context
from liquid.expression import Expression

from liquid.token import Token, TOKEN_TAG, TOKEN_ILLEGAL

from liquid.exceptions import DisabledTagError
from liquid.exceptions import Error

IllegalToken = Token(-1, TOKEN_ILLEGAL, "")


class Node(ABC):
    """Base class for all nodes in a parse tree."""

    __slots__ = ()

    # Indicates that nodes that do automatic whitespace suppression should output this
    # node regardless of its contents.
    force_output = False

    def token(self) -> Token:
        """The token that started this node."""
        token: Token = getattr(self, "tok", IllegalToken)
        return token

    def raise_for_disabled(self, disabled_tags: Collection[str]) -> None:
        """Raise a DisabledTagError if this node's type is in the given list."""
        tok = self.token()
        if tok.type == TOKEN_TAG and tok.value in disabled_tags:
            raise DisabledTagError(
                f"{tok.value} usage is not allowed in this context",
                linenum=tok.linenum,
            )

    def render(self, context: Context, buffer: TextIO) -> Optional[bool]:
        """Check disabled tags before delegating to `render_to_output`."""
        if context.disabled_tags:
            self.raise_for_disabled(context.disabled_tags)
        return self.render_to_output(context, buffer)

    async def render_async(self, context: Context, buffer: TextIO) -> Optional[bool]:
        """An async version of :meth:`liquid.ast.Node.render`."""
        if context.disabled_tags:
            self.raise_for_disabled(context.disabled_tags)
        if hasattr(self, "render_to_output_async"):
            # pylint: disable=no-member
            return await self.render_to_output_async(context, buffer)
        return self.render_to_output(context, buffer)

    @abstractmethod
    def render_to_output(
        self,
        context: Context,
        buffer: TextIO,
    ) -> Optional[bool]:
        """Render this node to the output buffer."""

    async def render_to_output_async(
        self,
        context: Context,
        buffer: TextIO,
    ) -> Optional[bool]:
        """An async version of :meth:`liquid.ast.Node.render_to_output`."""
        return self.render_to_output(context, buffer)


class ParseTree(Node):
    """The root node of all syntax trees."""

    __slots__ = ("statements", "version")

    def __init__(self) -> None:
        self.statements: List[Node] = []

    def __str__(self) -> str:  # pragma: no cover
        return "".join(str(s) for s in self.statements)

    def __repr__(self) -> str:
        return f"ParseTree({self.statements})"

    # pylint: disable=useless-return
    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        for stmt in self.statements:
            stmt.render(context, buffer)
        return None


class IllegalNode(Node):
    """Parse tree node representing an illegal or unregistered tag.

    Illegal nodes are necessary when running in "warn" or "lax" mode. In
    strict mode, an exception should be raised as soon as an illegal token
    is found.
    """

    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:  # pragma: no cover
        return f"IllegalNode(tok={self.tok})"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        pass


class BlockNode(Node):
    """A parse tree node representing a sequence of statements."""

    __slots__ = ("tok", "statements", "forced_output")

    def __init__(self, tok: Token, statements: Optional[List[Node]] = None):
        self.tok = tok
        self.statements = statements or []
        self.forced_output = False

    def __str__(self) -> str:
        return "".join(str(s) for s in self.statements)

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        for stmt in self.statements:
            try:
                stmt.render(context, buffer)
            except Error as err:
                # Maybe resume rendering the block after an error.
                context.error(err)
        return True

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        for stmt in self.statements:
            try:
                await stmt.render_async(context, buffer)
            except Error as err:
                # Maybe resume rendering the block after an error.
                context.error(err)
        return True


class ConditionalBlockNode(Node):
    """A parse tree node representing a sequence of statements and a conditional
    expression."""

    __slots__ = ("tok", "condition", "block", "forced_output")

    def __init__(self, tok: Token, condition: Expression, block: BlockNode):
        self.tok = tok
        self.condition = condition
        self.block = block
        self.forced_output = block.forced_output

    def __str__(self) -> str:
        return f"{self.condition} {{ {self.block} }}"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        if self.condition.evaluate(context):
            self.block.render(context, buffer)
            return True
        return False

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        if await self.condition.evaluate_async(context):
            await self.block.render_async(context, buffer)
            return True
        return False
