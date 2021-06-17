"""Tag and node definition for the built-in "cycle" tag."""

import sys

from typing import Any
from typing import List
from typing import Optional
from typing import TextIO

from liquid.ast import Node
from liquid.context import Context
from liquid.exceptions import LiquidSyntaxError
from liquid.expression import Expression
from liquid.lex import tokenize_filtered_expression

from liquid.parse import expect
from liquid.parse import parse_expression
from liquid.parse import parse_string_or_identifier

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_COLON

TAG_CYCLE = sys.intern("cycle")


class CycleNode(Node):
    """Parse tree node for the built-in "cycle" tag."""

    __slots__ = ("tok", "group", "args", "key")

    def __init__(self, tok: Token, group: Optional[Expression], args: List[Any]):
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
            group_name = str(self.group.evaluate(context))
        else:
            group_name = ""

        args = [arg.evaluate(context) for arg in self.args]
        buffer.write(str(next(context.cycle(group_name, args))))

        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        if self.group:
            group_name = str(await self.group.evaluate_async(context))
        else:
            group_name = ""

        args = [await arg.evaluate_async(context) for arg in self.args]
        buffer.write(str(next(context.cycle(group_name, args))))

        return None


class CycleTag(Tag):
    """The built-in "cycle" tag."""

    name = TAG_CYCLE
    block = False

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_CYCLE)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_filtered_expression(stream.current.value))

        group_name: Optional[Expression] = None

        if ":" in stream.current.value:
            group_name = parse_string_or_identifier(expr_stream, linenum=tok.linenum)
            expr_stream.next_token()

            expect(expr_stream, TOKEN_COLON)
            expr_stream.next_token()

        args = []
        while expr_stream.current.type != TOKEN_EOF:
            val = parse_expression(expr_stream)
            args.append(val)
            expr_stream.next_token()

            if expr_stream.current.type == TOKEN_COMMA:
                expr_stream.next_token()  # Eat comma
            elif expr_stream.current.type == TOKEN_EOF:
                break
            else:
                raise LiquidSyntaxError(
                    f"expected a comma separated list of arguments, "
                    f"found {expr_stream.current.type}",
                    linenum=tok.linenum,
                )

        return CycleNode(tok, group_name, args)
