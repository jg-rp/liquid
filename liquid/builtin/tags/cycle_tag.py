"""Tag and node definition for the built-in "cycle" tag."""

import sys
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.context import RenderContext
from liquid.exceptions import LiquidSyntaxError
from liquid.expression import Expression
from liquid.stream import TokenStream
from liquid.stringify import to_liquid_string
from liquid.tag import Tag
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import Token
from liquid.undefined import is_undefined

# ruff: noqa: D102

TAG_CYCLE = sys.intern("cycle")


class CycleNode(Node):
    """Parse tree node for the built-in "cycle" tag."""

    __slots__ = ("tok", "group", "args", "key")

    def __init__(self, tok: Token, group: Optional[Expression], args: list[Expression]):
        self.tok = tok
        self.group = group
        self.args = args

    def __str__(self) -> str:
        buf = ["cycle ("]
        if self.group:
            buf.append(f"{self.group}: ")

        buf.append(", ".join([str(arg) for arg in self.args]))
        buf.append(")")
        return "".join(buf)

    def render_to_output(
        self, context: RenderContext, buffer: TextIO
    ) -> Optional[bool]:
        if self.group:
            _group = self.group.evaluate(context)
            group_name = "__UNDEFINED" if is_undefined(_group) else str(_group)
        else:
            group_name = ""

        args = [arg.evaluate(context) for arg in self.args]
        buffer.write(
            to_liquid_string(
                context.cycle(group_name, args), autoescape=context.autoescape
            )
        )
        return True

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> Optional[bool]:
        if self.group:
            _group = await self.group.evaluate_async(context)
            group_name = "__UNDEFINED" if is_undefined(_group) else str(_group)
        else:
            group_name = ""

        args = [await arg.evaluate_async(context) for arg in self.args]
        buffer.write(
            to_liquid_string(
                context.cycle(group_name, args), autoescape=context.autoescape
            )
        )
        return True

    def children(self) -> list[ChildNode]:
        _children: list[ChildNode] = []
        if self.group:
            _children.append(
                ChildNode(linenum=self.tok.start_index, expression=self.group)
            )
        for arg in self.args:
            _children.append(ChildNode(linenum=self.tok.start_index, expression=arg))
        return _children


class CycleTag(Tag):
    """The built-in "cycle" tag."""

    name = TAG_CYCLE
    block = False
    node_class = CycleNode

    def parse(self, stream: TokenStream) -> CycleNode:
        tok = next(stream)
        stream.expect(TOKEN_EXPRESSION)
        tokens = tokenize(stream.current.value, linenum=tok.start_index)
        group_name: Optional[Expression] = None

        parts = list(split_at_first_colon(tokens))
        if len(parts) == 2:  # noqa: PLR2004
            group_name = parse_string_or_identifier(TokenStream(iter(parts[0])))

        args: list[Expression] = []
        expr_stream = TokenStream(iter(parts[-1]))
        while True:
            args.append(parse_obj(expr_stream))
            next(expr_stream)

            typ = expr_stream.current[1]
            if typ == TOKEN_COMMA:
                next(expr_stream)
            elif typ == TOKEN_EOF:
                break
            else:
                raise LiquidSyntaxError(
                    f"expected a comma separated list of arguments, found {typ}",
                    token=expr_stream.current,
                )

        return self.node_class(tok, group_name, args)
