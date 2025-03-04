"""The built-in _cycle_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import TextIO

from liquid.ast import Node
from liquid.builtin.expressions import PositionalArgument
from liquid.builtin.expressions import parse_primitive
from liquid.stringify import to_liquid_string
from liquid.tag import Tag
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_TAG
from liquid.token import Token
from liquid.undefined import is_undefined

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream


TAG_CYCLE = sys.intern("cycle")


class CycleNode(Node):
    """The built-in _cycle_ tag."""

    __slots__ = ("group", "args")

    group_by_args: bool = False
    """If `True`, use cycle arguments as well as group name when building cycle
    context keys."""

    def __init__(
        self, token: Token, group: Optional[Expression], args: list[Expression]
    ):
        super().__init__(token)
        self.group = group
        self.args = args
        self.blank = False

    def __str__(self) -> str:
        name = f"{self.group.token.value}: " if self.group else ""
        items = ", ".join(str(i) for i in self.args)
        return f"{{% cycle {name}{items} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        if self.group:
            _group = self.group.evaluate(context)
            group_name = "__UNDEFINED" if is_undefined(_group) else str(_group)
        else:
            group_name = ""

        args = [arg.evaluate(context) for arg in self.args]

        if self.group_by_args:
            key: object = (group_name, tuple(args))
        else:
            key = group_name if group_name else str(args)

        index = context.cycle(key, len(args))

        if index >= len(args):
            return 0

        return buffer.write(
            to_liquid_string(args[index], autoescape=context.autoescape)
        )

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        if self.group:
            _group = await self.group.evaluate_async(context)
            group_name = "__UNDEFINED" if is_undefined(_group) else str(_group)
        else:
            group_name = ""

        args = [await arg.evaluate_async(context) for arg in self.args]

        if self.group_by_args:
            key: object = (group_name, tuple(args))
        else:
            key = group_name if group_name else str(args)

        index = context.cycle(key, len(args))

        if index >= len(args):
            return 0

        return buffer.write(
            to_liquid_string(args[index], autoescape=context.autoescape)
        )

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        if self.group:
            yield self.group
        yield from self.args


class CycleTag(Tag):
    """The built-in _cycle_ tag."""

    name = TAG_CYCLE
    block = False
    node_class = CycleNode

    def parse(self, stream: TokenStream) -> CycleNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token, eat=False)

        group_name: Optional[Expression] = None
        if tokens.peek.kind == TOKEN_COLON:
            group_name = parse_primitive(self.env, tokens)
            tokens.eat(TOKEN_COLON)

        args = PositionalArgument.parse(self.env, tokens)
        return self.node_class(token, group_name, [arg.value for arg in args])
