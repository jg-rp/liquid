"""The built-in _cycle_ tag."""

import sys
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.builtin.expressions import PositionalArgument
from liquid.builtin.expressions import parse_primitive
from liquid.context import RenderContext
from liquid.expression import Expression
from liquid.stream import TokenStream
from liquid.stringify import to_liquid_string
from liquid.tag import Tag
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_TAG
from liquid.token import Token
from liquid.undefined import is_undefined

TAG_CYCLE = sys.intern("cycle")


class CycleNode(Node):
    """The built-in _cycle_ tag."""

    __slots__ = ("group", "args")

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
        return buffer.write(
            to_liquid_string(
                context.cycle(group_name, args), autoescape=context.autoescape
            )
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
        return buffer.write(
            to_liquid_string(
                context.cycle(group_name, args), autoescape=context.autoescape
            )
        )

    def children(self) -> list[ChildNode]:
        """Return this node's expressions."""
        _children: list[ChildNode] = []
        if self.group:
            _children.append(
                ChildNode(linenum=self.token.start_index, expression=self.group)
            )
        for arg in self.args:
            _children.append(ChildNode(linenum=self.token.start_index, expression=arg))
        return _children


class CycleTag(Tag):
    """The built-in _cycle_ tag."""

    name = TAG_CYCLE
    block = False
    node_class = CycleNode

    def parse(self, stream: TokenStream) -> CycleNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner()

        group_name: Optional[Expression] = None
        if tokens.peek.kind == TOKEN_COLON:
            group_name = parse_primitive(self.env, tokens)
            tokens.eat(TOKEN_COLON)

        args = PositionalArgument.parse(self.env, tokens)
        return self.node_class(token, group_name, [arg.value for arg in args])
