"""Common parse tree nodes."""

from abc import ABC
from abc import abstractmethod

from typing import Collection
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import TextIO

from typing_extensions import Literal

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

    def children(self) -> List["ChildNode"]:
        """Return a list of child nodes and/or expressions associated with this node."""
        raise NotImplementedError(f"{self.__class__.__name__}.children")


class ChildNode(NamedTuple):
    """An AST node and expression pair with optional scope and load data.

    :param linenum: The line number of the child's first token in the template source
        text.
    :type linenum: int
    :param expression: An :class:`liquid.expression.Expression`. If not ``None``, this
        expression is expected to be related to the given :class:`liquid.ast.Node`.
    :type expression: Optional[liquid.expression.Expression]
    :param node: A :class:`liquid.ast.Node`. Typically a ``BlockNode`` or
        ``ConditionalBlockNode``.
    :type node: Optional[liquid.ast.Node]
    :param template_scope: A list of names the parent node adds to the template "local"
        scope. For example, the built-in ``assign``, ``capture``, ``increment`` and
        ``decrement`` tags all add names to the template scope. This helps us identify,
        through static analysis, names that are assumed to be "global".
    :type template_scope: Optional[List[str]]
    :param block_scope: A list of names available to the given child node. For example,
        the ``for`` tag adds the name "forloop" for the duration of its block.
    :type block_scope: Optional[List[str]]
    :param load_mode: If not ``None``, indicates that the given expression should be
        used to load a partial template. In "render" mode, the partial will be analyzed
        in an isolated namespace, without access to the parent's template local scope.
        In "include" mode, the partial will have access to the parents template local
        scope and the parent's scope can be updated by the partial template too.
    :type load_mode: Optional[Literal["render", "include", "extends"]]
    :param load_context: Meta data a template ``Loader`` might need to find the source
        of a partial template.
    """

    linenum: int
    expression: Optional[Expression] = None
    node: Optional[Node] = None
    template_scope: Optional[List[str]] = None
    block_scope: Optional[List[str]] = None
    load_mode: Optional[Literal["render", "include", "extends"]] = None
    load_context: Optional[Dict[str, str]] = None


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

    def children(self) -> List["ChildNode"]:
        return [
            ChildNode(
                linenum=self.tok.linenum,
                node=stmt,
            )
            for stmt in self.statements
        ]


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

    def children(self) -> List["ChildNode"]:
        return [
            ChildNode(
                linenum=self.tok.linenum,
                node=self.block,
                expression=self.condition,
            )
        ]
