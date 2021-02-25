"""Common parse tree nodes."""

from abc import ABC, abstractmethod
from io import StringIO

from typing import List
from typing import Optional
from typing import TextIO
from typing import Collection
from typing import Union
from typing import NoReturn

from liquid import __version__
from liquid import Context
from liquid import Expression

from liquid.token import Token, TOKEN_TAG

from liquid.exceptions import DisabledTagError
from liquid.exceptions import Error


class Node(ABC):
    """Base class for all nodes in a parse tree."""

    __slots__ = ()

    def token(self) -> Token:
        """The token that started this node."""
        return getattr(self, "tok", None)

    def raise_for_disabled(self, disabled_tags: Collection[str]):
        """Raise a DisabledTagError if this node's type is in the given list."""
        tok = self.token()
        if tok.type == TOKEN_TAG and tok.value in disabled_tags:
            raise DisabledTagError(
                f"{tok.value} usage is not allowed in this context",
                linenum=tok.linenum,
            )

    def render(
        self, context: Context, buffer: TextIO
    ) -> Union[Optional[bool], NoReturn]:
        """Check disabled tags before delegating to `render_to_output`."""
        if context.disabled_tags:
            self.raise_for_disabled(context.disabled_tags)
        return self.render_to_output(context, buffer)

    @abstractmethod
    def render_to_output(
        self,
        context: Context,
        buffer: TextIO,
    ) -> Union[Optional[bool], NoReturn]:
        """Render this node to the output buffer."""


class ParseTree(Node):
    """The root node of all syntax trees."""

    __slots__ = ("statements", "version")

    def __init__(self):
        self.statements = []
        self.version = __version__

    def __str__(self):  # pragma: no cover
        return "".join(str(s) for s in self.statements)

    def __repr__(self):
        return f"ParseTree({self.statements})"

    def render_to_output(self, context: Context, buffer: TextIO):
        for stmt in self.statements:
            stmt.render(context, buffer)


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

    def render_to_output(self, context: Context, buffer: TextIO):
        pass


class BlockNode(Node):
    """A parse tree node representing a sequence of statements."""

    __slots__ = ("tok", "statements")

    def __init__(self, tok: Token, statements: Optional[List[Node]] = None):
        self.tok = tok
        self.statements = statements or []

    def __str__(self):
        return "".join(str(s) for s in self.statements)

    def render_to_output(self, context: Context, buffer: TextIO):
        # This intermediate buffer is used to suppress blocks that, when rendered,
        # contain only whitespace.
        buf = StringIO()

        for stmt in self.statements:
            try:
                stmt.render(context, buf)
            except Error as err:
                # Maybe resume rendering the block after an error.
                context.error(err)
            except Exception:
                # Write what we have so far and stop rendering the block.
                val = buf.getvalue()
                if not val.isspace():
                    buffer.write(val)
                raise

        # Don't write to the output buffer if the block contains only whitespace.
        val = buf.getvalue()
        if not val.isspace():
            buffer.write(val)


class ConditionalBlockNode(Node):
    """A parse tree node representing a sequence of statements and a conditional
    expression."""

    __slots__ = ("tok", "condition", "block")

    def __init__(self, tok: Token, condition: Expression, block: BlockNode = None):
        self.tok = tok
        self.condition = condition
        self.block = block

    def __str__(self):
        return f"{self.condition} {{ {self.block} }}"

    def render_to_output(self, context: Context, buffer: TextIO):
        if self.condition.evaluate(context):
            self.block.render(context, buffer)
            return True
        return False
