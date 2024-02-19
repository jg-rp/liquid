from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import TextIO
from typing import Union

from liquid import ast
from liquid.builtin.tags.case_tag import ENDWHENBLOCK
from liquid.builtin.tags.case_tag import TAG_CASE
from liquid.builtin.tags.case_tag import TAG_ELSE
from liquid.builtin.tags.case_tag import TAG_ENDCASE
from liquid.builtin.tags.case_tag import TAG_WHEN
from liquid.builtin.tags.case_tag import CaseTag
from liquid.exceptions import LiquidSyntaxError
from liquid.expression import BooleanExpression
from liquid.expression import InfixExpression
from liquid.parse import expect
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import Context
    from liquid.stream import TokenStream


@dataclass
class _Block:
    tag: str
    node: Union[ast.BlockNode, ast.ConditionalBlockNode]


class LaxCaseNode(ast.Node):
    """Parse tree node for the lax "case" tag."""

    __slots__ = ("tok", "blocks", "forced_output")

    def __init__(
        self,
        tok: Token,
        blocks: List[_Block],
    ):
        self.tok = tok
        self.blocks = blocks

        self.forced_output = self.force_output or any(
            b.node.forced_output for b in self.blocks
        )

    def __str__(self) -> str:
        buf = (
            ["if (False) { }"]
            if not self.blocks or self.blocks[0].tag == TAG_ELSE
            else [f"if {self.blocks[0].node}"]
        )

        for block in self.blocks:
            if block.tag == TAG_ELSE:
                buf.append(f"else {block.node}")
            elif block.tag == TAG_WHEN:
                buf.append(f"elsif {block.node}")

        return " ".join(buf)

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        rendered: Optional[bool] = False

        for block in self.blocks:
            if block.tag == TAG_WHEN:
                rendered = block.node.render(context, buf) or rendered
            elif block.tag == TAG_ELSE and not rendered:
                block.node.render(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        rendered: Optional[bool] = False

        for block in self.blocks:
            if block.tag == TAG_WHEN:
                rendered = await block.node.render_async(context, buf) or rendered
            elif block.tag == TAG_ELSE and not rendered:
                await block.node.render_async(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    def children(self) -> List[ast.ChildNode]:
        _children = []

        for block in self.blocks:
            if isinstance(block.node, ast.BlockNode):
                _children.append(
                    ast.ChildNode(
                        linenum=block.node.tok.linenum,
                        node=block.node,
                        expression=None,
                    )
                )
            elif isinstance(block.node, ast.ConditionalBlockNode):
                _children.append(
                    ast.ChildNode(
                        linenum=block.node.tok.linenum,
                        node=block.node,
                        expression=block.node.condition,
                    )
                )

        return _children


class LaxCaseTag(CaseTag):
    """A `case` tag that is lax in its handling of extra `else` and `when` blocks."""

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

        blocks: List[_Block] = []

        while not stream.current.istag(TAG_ENDCASE):
            if stream.current.istag(TAG_ELSE):
                stream.next_token()
                blocks.append(
                    _Block(
                        tag=TAG_ELSE,
                        node=self.parser.parse_block(stream, ENDWHENBLOCK),
                    )
                )
            elif stream.current.istag(TAG_WHEN):
                when_tok = stream.next_token()
                expect(stream, TOKEN_EXPRESSION)  # XXX: empty when expressions?

                when_exprs = [
                    BooleanExpression(InfixExpression(case, "==", expr))
                    for expr in self._parse_when_expression(
                        stream.current.value, stream.current.linenum
                    )
                ]

                stream.next_token()
                when_block = self.parser.parse_block(stream, ENDWHENBLOCK)

                blocks.extend(
                    _Block(
                        tag=TAG_WHEN,
                        node=ast.ConditionalBlockNode(
                            tok=when_tok,
                            condition=expr,
                            block=when_block,
                        ),
                    )
                    for expr in when_exprs
                )

            else:
                raise LiquidSyntaxError(
                    f"unexpected tag {stream.current.value}",
                    linenum=stream.current.linenum,
                )

        expect(stream, TOKEN_TAG, value=TAG_ENDCASE)
        return LaxCaseNode(tok, blocks=blocks)
