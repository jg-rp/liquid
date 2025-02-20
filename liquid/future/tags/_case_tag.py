from __future__ import annotations

from typing import TYPE_CHECKING
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
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.stream import TokenStream


class LaxCaseNode(ast.Node):
    """Parse tree node for the lax "case" tag."""

    __slots__ = ("tok", "blocks", "forced_output")

    def __init__(
        self,
        tok: Token,
        blocks: list[Union[ast.BlockNode, ast.ConditionalBlockNode]],
    ):
        self.tok = tok
        self.blocks = blocks

        self.forced_output = self.force_output or any(
            b.forced_output for b in self.blocks
        )

    def __str__(self) -> str:
        buf = (
            ["if (False) { }"]
            if not self.blocks or isinstance(self.blocks[0], ast.BlockNode)
            else [f"if {self.blocks[0]}"]
        )

        for block in self.blocks:
            if isinstance(block, ast.BlockNode):
                buf.append(f"else {block}")
            if isinstance(block, ast.ConditionalBlockNode):
                buf.append(f"elsif {block}")

        return " ".join(buf)

    def render_to_output(
        self, context: RenderContext, buffer: TextIO
    ) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        rendered: Optional[bool] = False

        for block in self.blocks:
            # Always render truthy `when` blocks, no matter the order.
            if isinstance(block, ast.ConditionalBlockNode):
                rendered = block.render(context, buf) or rendered
            # Only render `else` blocks if all preceding `when` blocks are falsy.
            # Multiple `else` blocks are OK.
            elif isinstance(block, ast.BlockNode) and not rendered:
                block.render(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> Optional[bool]:
        buf = context.get_buffer(buffer)
        rendered: Optional[bool] = False

        for block in self.blocks:
            if isinstance(block, ast.ConditionalBlockNode):
                rendered = await block.render_async(context, buf) or rendered
            elif isinstance(block, ast.BlockNode) and not rendered:
                await block.render_async(context, buf)

        val = buf.getvalue()
        if self.forced_output or not val.isspace():
            buffer.write(val)

        return rendered

    def children(self) -> list[ast.ChildNode]:
        _children = []

        for block in self.blocks:
            if isinstance(block, ast.BlockNode):
                _children.append(
                    ast.ChildNode(
                        linenum=block.tok.linenum,
                        node=block,
                        expression=None,
                    )
                )
            elif isinstance(block, ast.ConditionalBlockNode):
                _children.append(
                    ast.ChildNode(
                        linenum=block.tok.linenum,
                        node=block,
                        expression=block.condition,
                    )
                )

        return _children


class LaxCaseTag(CaseTag):
    """A `case` tag that is lax in its handling of extra `else` and `when` blocks."""

    def parse(self, stream: TokenStream) -> ast.Node:
        stream.expect(TOKEN_TAG, value=TAG_CASE)
        tok = stream.current
        stream.next_token()

        # Parse the case expression.
        stream.expect(TOKEN_EXPRESSION)
        case = self._parse_case_expression(stream.current.value, stream.current.linenum)
        stream.next_token()

        # Eat whitespace or junk between `case` and when/else/endcase
        while (
            stream.current.type != TOKEN_TAG
            and stream.current.value not in ENDWHENBLOCK
        ):
            stream.next_token()

        # Collect all `when` and `else` tags regardless of te order n which they appear.
        blocks: list[Union[ast.BlockNode, ast.ConditionalBlockNode]] = []

        while not stream.current.istag(TAG_ENDCASE):
            if stream.current.istag(TAG_ELSE):
                stream.next_token()
                blocks.append(self.parser.parse_block(stream, ENDWHENBLOCK))
            elif stream.current.istag(TAG_WHEN):
                when_tok = stream.next_token()
                stream.expect(TOKEN_EXPRESSION)

                # Transform each comma or "or" separated when expression into a block
                # node of its own, just as if each expression had its own `when` tag.
                when_exprs = [
                    BooleanExpression(InfixExpression(case, "==", expr))
                    for expr in self._parse_when_expression(
                        stream.current.value, stream.current.linenum
                    )
                ]

                stream.next_token()
                when_block = self.parser.parse_block(stream, ENDWHENBLOCK)

                # Reuse the same block.
                blocks.extend(
                    ast.ConditionalBlockNode(
                        tok=when_tok,
                        condition=expr,
                        block=when_block,
                    )
                    for expr in when_exprs
                )

            else:
                raise LiquidSyntaxError(
                    f"unexpected tag {stream.current.value}",
                    linenum=stream.current.linenum,
                )

        stream.expect(TOKEN_TAG, value=TAG_ENDCASE)
        return LaxCaseNode(tok, blocks=blocks)
