"""Tag and node definition for the built-in "case" tag."""
from __future__ import annotations
import sys

from typing import List
from typing import Optional
from typing import TextIO
from typing import TYPE_CHECKING

from liquid.expression import BooleanExpression
from liquid.expression import InfixExpression

from liquid.expressions.common import tokenize_common_expression
from liquid.expressions.common import parse_common_expression
from liquid.expressions.stream import TokenStream as ExpressionTokenStream

from liquid.token import Token
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_TAG


from liquid.parse import get_parser
from liquid.parse import expect

from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.expression import Expression

TAG_CASE = sys.intern("case")
TAG_ENDCASE = sys.intern("endcase")
TAG_WHEN = sys.intern("when")
TAG_ELSE = sys.intern("else")

ENDWHENBLOCK = frozenset((TAG_ENDCASE, TAG_WHEN, TAG_ELSE, TOKEN_EOF))
ENDCASEBLOCK = frozenset((TAG_ENDCASE,))


class CaseNode(ast.Node):
    """Parse tree node for the built-in "case" tag."""

    __slots__ = ("tok", "whens", "default", "forced_output")

    def __init__(
        self,
        tok: Token,
        whens: List[ast.ConditionalBlockNode],
        default: Optional[ast.BlockNode] = None,
    ):
        self.tok = tok
        self.whens = whens
        self.default = default

        self.forced_output = any(
            n.forced_output for n in (*self.whens, self.default) if n
        )

    def __str__(self) -> str:
        if not self.whens:
            buf = ["if (False) { }"]
        else:
            buf = [f"if {self.whens[0]}"]

        if len(self.whens) > 1:
            for when in self.whens[1:]:
                buf.append(f"elsif {when}")

        if self.default:
            buf.append(f"else {{ {self.default} }}")

        return " ".join(buf)

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        rendered: Optional[bool] = False

        for when in self.whens:
            if when.render(context, buf):
                rendered = True

        if not rendered and self.default:
            rendered = self.default.render(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        rendered: Optional[bool] = False

        for when in self.whens:
            if await when.render_async(context, buf):
                rendered = True

        if not rendered and self.default:
            rendered = await self.default.render_async(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    def children(self) -> List[ast.ChildNode]:
        _children = [
            ast.ChildNode(
                linenum=alt.tok.linenum,
                node=alt.block,
                expression=alt.condition,
            )
            for alt in self.whens
        ]
        if self.default:
            _children.append(
                ast.ChildNode(
                    linenum=self.default.tok.linenum,
                    node=self.default,
                    expression=None,
                )
            )
        return _children


class CaseTag(Tag):
    """The built-in cycle tag."""

    name = TAG_CASE
    end = TAG_ENDCASE

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> ast.Node:
        expect(stream, TOKEN_TAG, value=TAG_CASE)
        tok = stream.current
        stream.next_token()

        # Parse the case expression.
        expect(stream, TOKEN_EXPRESSION)
        case = self._parse_case_expression(stream.current.value, stream.current.linenum)
        stream.next_token()

        # Eat whitespace or junk between `case` and when/else/endcase
        while (
            stream.current.type != TOKEN_TAG
            and stream.current.value not in ENDWHENBLOCK
        ):
            stream.next_token()

        whens: List[ast.ConditionalBlockNode] = []

        while stream.current.istag(TAG_WHEN):
            when_tok = stream.current
            stream.next_token()  # Eat WHEN
            expect(stream, TOKEN_EXPRESSION)

            # One conditional block for every object in a comma or `or` separated list.
            when_exprs = [
                BooleanExpression(InfixExpression(case, "==", expr))
                for expr in self._parse_when_expression(
                    stream.current.value, stream.current.linenum
                )
            ]

            stream.next_token()
            when_block = self.parser.parse_block(stream, ENDWHENBLOCK)

            whens.extend(
                ast.ConditionalBlockNode(
                    tok=when_tok,
                    condition=expr,
                    block=when_block,
                )
                for expr in when_exprs
            )

        default: Optional[ast.BlockNode] = None

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            default = self.parser.parse_block(stream, ENDCASEBLOCK)

        expect(stream, TOKEN_TAG, value=TAG_ENDCASE)
        return CaseNode(tok, whens=whens, default=default)

    def _parse_case_expression(self, expr: str, linenum: int) -> Expression:
        stream = ExpressionTokenStream(
            tokenize_common_expression(expr, linenum=linenum)
        )
        return parse_common_expression(stream)

    def _parse_when_expression(self, expr: str, linenum: int) -> List[Expression]:
        expressions = []
        stream = ExpressionTokenStream(
            tokenize_common_expression(expr, linenum=linenum)
        )

        while True:
            expressions.append(parse_common_expression(stream))
            next(stream)
            if stream.current[1] in (TOKEN_COMMA, TOKEN_OR):
                next(stream)
            else:
                break

        return expressions
