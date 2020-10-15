"""Tag and node definition for the built-in "case" tag."""
import sys
from typing import Optional, List, TextIO

from liquid.token import Token, TOKEN_EOF, TOKEN_EXPRESSION, TOKEN_TAG
from liquid.parse import get_parser, expect, parse_boolean_expression
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.lex import tokenize_boolean_expression

TAG_CASE = sys.intern("case")
TAG_ENDCASE = sys.intern("endcase")
TAG_WHEN = sys.intern("when")
TAG_ELSE = sys.intern("else")

ENDWHENBLOCK = (TAG_ENDCASE, TAG_WHEN, TAG_ELSE, TOKEN_EOF)
ENDCASEBLOCK = (TAG_ENDCASE,)


class CaseNode(ast.Node):
    """Parse tree node for the built-in "case" tag."""

    __slots__ = ("tok", "whens", "default")

    def __init__(
        self,
        tok: Token,
        whens: List[ast.ConditionalBlockNode],
        default: Optional[ast.BlockNode] = None,
    ):
        self.tok = tok
        self.whens = whens
        self.default = default

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

    def render_to_output(self, context: Context, buffer: TextIO):
        rendered = False

        for when in self.whens:
            if when.render(context, buffer):
                rendered = True
                break

        if not rendered and self.default:
            self.default.render(context, buffer)


class CaseTag(Tag):
    """The built-in cycle tag."""

    name = TAG_CASE
    end = TAG_ENDCASE

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG, value=TAG_CASE)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        case = stream.current.value
        stream.next_token()

        # Eat whitespace or junk between `case` and when/else/endcase
        while (
            stream.current.type != TOKEN_TAG
            and stream.current.value not in ENDWHENBLOCK
        ):
            stream.next_token()

        whens = []

        while stream.current.istag(TAG_WHEN):
            stream.next_token()  # Eat WHEN
            expect(stream, TOKEN_EXPRESSION)

            expr_iter = tokenize_boolean_expression(f"{case} == {stream.current.value}")
            expr = parse_boolean_expression(TokenStream(expr_iter))

            when = ast.ConditionalBlockNode(
                stream.current,
                condition=expr,
            )

            stream.next_token()
            when.block = parser.parse_block(stream, ENDWHENBLOCK)
            whens.append(when)

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            default = parser.parse_block(stream, ENDCASEBLOCK)
        else:
            default = None

        expect(stream, TOKEN_TAG, value=TAG_ENDCASE)
        return CaseNode(tok, whens=whens, default=default)
