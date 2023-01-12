"""Tag and node definition for the built-in "cycle" tag."""
import sys

from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node

from liquid.context import Context
from liquid.exceptions import LiquidSyntaxError
from liquid.expression import Expression

from liquid.parse import expect
from liquid.stream import TokenStream
from liquid.stringify import to_liquid_string
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_COLON

from liquid.undefined import is_undefined

from liquid.expressions import Token as ExprToken
from liquid.expressions import TokenStream as ExprTokenStream
from liquid.expressions.common import parse_string_or_identifier
from liquid.expressions.filtered.lex import tokenize
from liquid.expressions.filtered.parse import parse_obj

TAG_CYCLE = sys.intern("cycle")


class CycleNode(Node):
    """Parse tree node for the built-in "cycle" tag."""

    __slots__ = ("tok", "group", "args", "key")

    def __init__(self, tok: Token, group: Optional[Expression], args: List[Expression]):
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

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        if self.group:
            _group = self.group.evaluate(context)
            if is_undefined(_group):
                group_name = "__UNDEFINED"
            else:
                group_name = str(_group)
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
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        if self.group:
            _group = await self.group.evaluate_async(context)
            if is_undefined(_group):
                group_name = "__UNDEFINED"
            else:
                group_name = str(_group)
        else:
            group_name = ""

        args = [await arg.evaluate_async(context) for arg in self.args]
        buffer.write(
            to_liquid_string(
                context.cycle(group_name, args), autoescape=context.autoescape
            )
        )
        return True

    def children(self) -> List[ChildNode]:
        _children: List[ChildNode] = []
        if self.group:
            _children.append(ChildNode(linenum=self.tok.linenum, expression=self.group))
        for arg in self.args:
            _children.append(ChildNode(linenum=self.tok.linenum, expression=arg))
        return _children


def split_at_first_colon(tokens: Iterable[ExprToken]) -> Iterator[List[ExprToken]]:
    """Split tokens on into lists, using TOKEN_COLON as the delimiter."""
    buf: List[ExprToken] = []
    for token in tokens:
        if token[1] == TOKEN_COLON:
            yield buf
            buf = []
        else:
            buf.append(token)
    yield buf


class CycleTag(Tag):
    """The built-in "cycle" tag."""

    name = TAG_CYCLE
    block = False

    def parse(self, stream: TokenStream) -> CycleNode:
        tok = next(stream)
        expect(stream, TOKEN_EXPRESSION)
        tokens = tokenize(stream.current.value, linenum=tok.linenum)
        group_name: Optional[Expression] = None

        parts = list(split_at_first_colon(tokens))
        if len(parts) == 2:
            group_name = parse_string_or_identifier(ExprTokenStream(iter(parts[0])))

        args: List[Expression] = []
        expr_stream = ExprTokenStream(iter(parts[-1]))
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
                    linenum=expr_stream.current[0],
                )

        return CycleNode(tok, group_name, args)
