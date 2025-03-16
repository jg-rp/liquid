"""The built-in _for_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import LoopExpression
from liquid.exceptions import BreakLoop
from liquid.exceptions import ContinueLoop
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream


TAG_FOR = sys.intern("for")
TAG_ENDFOR = sys.intern("endfor")
TAG_ELSE = sys.intern("else")

TAG_BREAK = sys.intern("break")
TAG_CONTINUE = sys.intern("continue")

ENDFORBLOCK = frozenset((TAG_ENDFOR, TAG_ELSE))
ENDFORELSEBLOCK = frozenset((TAG_ENDFOR,))


class ForNode(Node):
    """The built-in _for_ tag."""

    __slots__ = ("expression", "block", "default")

    def __init__(
        self,
        token: Token,
        expression: LoopExpression,
        block: BlockNode,
        default: Optional[BlockNode] = None,
    ):
        super().__init__(token)
        self.expression = expression
        self.block = block
        self.default = default
        self.blank = block.blank and (not default or default.blank)

    def __str__(self) -> str:
        default = ""

        if self.default:
            default = f"{{% else %}}{self.default}"

        return f"{{% for {self.expression} %}}{self.block}{default}{{% endfor %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        it, length = self.expression.evaluate(context)

        if length:
            character_count = 0
            name = self.expression.identifier

            forloop = ForLoop(
                name=f"{name}-{self.expression.iterable}",
                it=it,
                length=length,
                parentloop=context.parentloop(),
            )

            namespace = {
                "forloop": forloop,
                name: None,
            }

            # Extend the context. Essentially giving priority to `ForLoopDrop`, then
            # delegating `get` and `assign` to the outer context.
            with context.loop(namespace, forloop):
                for itm in forloop:
                    namespace[name] = itm
                    try:
                        character_count += self.block.render(context, buffer)
                    except ContinueLoop:
                        continue
                    except BreakLoop:
                        break

            return character_count

        return self.default.render(context, buffer) if self.default else 0

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        it, length = await self.expression.evaluate_async(context)

        if length:
            character_count = 0
            name = self.expression.identifier

            forloop = ForLoop(
                name=f"{name}-{self.expression.iterable}",
                it=it,
                length=length,
                parentloop=context.parentloop(),
            )

            namespace = {
                "forloop": forloop,
                name: None,
            }

            # Extend the context. Essentially giving priority to `ForLoopDrop`, then
            # delegating `get` and `assign` to the outer context.
            with context.loop(namespace, forloop):
                for itm in forloop:
                    namespace[name] = itm
                    try:
                        character_count += await self.block.render_async(
                            context, buffer
                        )
                    except ContinueLoop:
                        continue
                    except BreakLoop:
                        break

            return character_count

        return await self.default.render_async(context, buffer) if self.default else 0

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.block
        if self.default:
            yield self.default

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.expression

    def block_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the node's block scope."""
        yield Identifier(self.expression.identifier, token=self.expression.token)
        yield Identifier("forloop", token=self.token)


class BreakNode(Node):
    """Parse tree node for the built-in "break" tag."""

    def __str__(self) -> str:
        return "{% break %}"

    def render_to_output(
        self,
        _: RenderContext,
        __: TextIO,
    ) -> int:
        """Render the node to the output buffer."""
        raise BreakLoop("break")


class ContinueNode(Node):
    """Parse tree node for the built-in "continue" tag."""

    def __str__(self) -> str:
        return "{% continue %}"

    def render_to_output(
        self,
        _: RenderContext,
        __: TextIO,
    ) -> int:
        """Render the node to the output buffer."""
        raise ContinueLoop("continue")


class ForTag(Tag):
    """The built-in _for_ tag."""

    name = TAG_FOR
    end = TAG_ENDFOR
    node_class = ForNode

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        expr = LoopExpression.parse(self.env, stream.into_inner(tag=token))

        parse_block = get_parser(self.env).parse_block
        block = parse_block(stream, ENDFORBLOCK)
        default: Optional[BlockNode] = None

        if stream.current.is_tag(TAG_ELSE):
            next(stream)
            default = parse_block(stream, ENDFORELSEBLOCK)

        stream.expect(TOKEN_TAG, value=TAG_ENDFOR)
        return self.node_class(token, expression=expr, block=block, default=default)


class BreakTag(Tag):
    """The built-in _break_ tag."""

    name = TAG_BREAK
    block = False

    def parse(self, stream: TokenStream) -> BreakNode:
        """Parse tokens from _stream_ into an AST node."""
        stream.expect(TOKEN_TAG, value=TAG_BREAK)
        return BreakNode(stream.current)


class ContinueTag(Tag):
    """The built-in _continue_ tag."""

    name = TAG_CONTINUE
    block = False

    def parse(self, stream: TokenStream) -> ContinueNode:
        """Parse tokens from _stream_ into an AST node."""
        stream.expect(TOKEN_TAG, value=TAG_CONTINUE)
        return ContinueNode(stream.current)


class ForLoop(Mapping[str, object]):
    """Loop helper variables."""

    __slots__ = (
        "name",
        "it",
        "length",
        "item",
        "_index",
        "parentloop",
    )

    _keys = frozenset(
        [
            "name",
            "length",
            "index",
            "index0",
            "rindex",
            "rindex0",
            "first",
            "last",
            "parentloop",
        ]
    )

    def __init__(
        self,
        name: str,
        it: Iterator[Any],
        length: int,
        parentloop: object,
    ):
        self.name = name
        self.it = it
        self.length = length

        self.item = None
        self._index = -1  # Step is called before `next(it)`
        self.parentloop = parentloop

    def __repr__(self) -> str:  # pragma: no cover
        return f"ForLoop(name='{self.name}', length={self.length})"

    def __getitem__(self, key: str) -> object:
        if key in self._keys:
            return getattr(self, key)
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._keys)

    def __next__(self) -> object:
        self.step()
        return next(self.it)

    def __iter__(self) -> Iterator[Any]:
        return self

    def __str__(self) -> str:
        return "ForLoop"

    @property
    def index(self) -> int:
        """The 1-based index of the current loop iteration."""
        return self._index + 1

    @property
    def index0(self) -> int:
        """The 0-based index of the current loop iteration."""
        return self._index

    @property
    def rindex(self) -> int:
        """The 1-based index, counting from the right, of the current loop iteration."""
        return self.length - self._index

    @property
    def rindex0(self) -> int:
        """The 0-based index, counting from the right, of the current loop iteration."""
        return self.length - self._index - 1

    @property
    def first(self) -> bool:
        """True if this is the first iteration, false otherwise."""
        return self._index == 0

    @property
    def last(self) -> bool:
        """True if this is the last iteration, false otherwise."""
        return self._index == self.length - 1

    def step(self) -> None:
        """Move the for loop helper forward to the next iteration."""
        self._index += 1
