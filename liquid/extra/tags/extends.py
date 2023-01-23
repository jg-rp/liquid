"""Template inheritance tags."""
# pylint: disable=missing-class-docstring
from __future__ import annotations
import sys

from collections import defaultdict

from typing import DefaultDict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Set
from typing import TextIO
from typing import Tuple
from typing import TYPE_CHECKING

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode as TemplateBlockNode

from liquid.context import Context

from liquid.exceptions import LiquidEnvironmentError
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import RequiredBlockError
from liquid.exceptions import StopRender
from liquid.exceptions import TemplateInheritanceError

from liquid.expression import StringLiteral

from liquid.expressions import TokenStream as ExprTokenStream
from liquid.expressions.common import parse_string_literal
from liquid.expressions.common import tokenize_common_expression

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_STRING

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid import BoundTemplate


TAG_EXTENDS = sys.intern("extends")
TAG_BLOCK = sys.intern("block")
TAG_ENDBLOCK = sys.intern("endblock")


class BlockDrop(Mapping[str, object]):
    """A `block` object with a `super` property."""

    __slots__ = ("buffer", "context", "name", "parent")

    def __init__(
        self, context: Context, buffer: TextIO, name: str, parent: Optional["BlockNode"]
    ) -> None:
        self.buffer = buffer
        self.context = context
        self.name = name
        self.parent = parent

    def __str__(self) -> str:  # pragma: no cover
        return f"Block({self.name})"

    def __getitem__(self, key: str) -> object:
        if key != "super":
            raise KeyError(key)

        if not self.parent:
            return self.context.env.undefined("super")

        # NOTE: We're not allowing chaining of references to `super` for now.
        # Just the immediate parent.
        buf = self.context.get_buffer(self.buffer)
        self.parent.block.render(self.context, buf)
        return buf.getvalue()

    def __len__(self) -> int:  # pragma: no cover
        return 1

    def __iter__(self) -> Iterator[str]:  # pragma: no cover
        return iter(["super"])


class _BlockStackItem(NamedTuple):
    block: "BlockNode"
    required: bool


class BlockNode(Node):
    __slots__ = ("tok", "name", "block", "expr", "required")

    def __init__(
        self,
        tok: Token,
        name: StringLiteral,
        block: TemplateBlockNode,
        required: bool,
    ) -> None:
        self.tok = tok
        self.expr = name
        self.name = str(name)
        self.block = block
        self.required = required

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        # We should be in a base template. Render the block at the top of the "stack".
        block_stack: Sequence[_BlockStackItem] = context.tag_namespace.get(
            "extends", {}
        ).get(self.name)

        if not block_stack:
            # This base template is being rendered directly.
            if self.required:
                raise RequiredBlockError(
                    f"block {self.name} must be overridden", linenum=self.tok.linenum
                )
            with context.extend({"block": BlockDrop(context, buffer, self.name, None)}):
                return self.block.render(context, buffer)

        block, required = block_stack[0]

        if required:
            raise RequiredBlockError(
                f"block {self.name} must be overridden", linenum=self.tok.linenum
            )

        if len(block_stack) > 1:
            parent: Optional[BlockNode] = block_stack[1].block
        else:
            parent = None

        ctx = context.copy(
            {"block": BlockDrop(context, buffer, self.name, parent)},
            carry_loop_iterations=True,
            with_locals=True,
        )
        return block.block.render(ctx, buffer)

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        # We should be in a base template. Render the block at the top of the "stack".
        block_stack: Sequence[_BlockStackItem] = context.tag_namespace.get(
            "extends", {}
        ).get(self.name)

        if not block_stack:
            # This base template is being rendered directly.
            if self.required:
                raise RequiredBlockError(
                    f"block {self.name} must be overridden", linenum=self.tok.linenum
                )
            with context.extend({"block": BlockDrop(context, buffer, self.name, None)}):
                return await self.block.render_async(context, buffer)

        block, required = block_stack[0]

        if required:
            raise RequiredBlockError(
                f"block {self.name!r} must be overridden", linenum=self.tok.linenum
            )

        if len(block_stack) > 1:
            parent: Optional[BlockNode] = block_stack[1].block
        else:
            parent = None

        ctx = context.copy(
            {"block": BlockDrop(context, buffer, self.name, parent)},
            carry_loop_iterations=True,
            with_locals=True,
        )
        return await block.block.render_async(ctx, buffer)

    def children(self) -> List[ChildNode]:
        return [
            ChildNode(linenum=self.tok.linenum, expression=self.expr),
            ChildNode(linenum=self.tok.linenum, node=self.block),
        ]


class ExtendsNode(Node):
    __slots__ = ("tok", "name")
    tag = TAG_EXTENDS

    def __init__(self, tok: Token, name: StringLiteral) -> None:
        self.tok = tok
        self.name = name

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        if not context.template:
            raise LiquidEnvironmentError(
                "the 'extends' tag requires the current render context to keep a "
                "reference to its template as Context.template",
                linenum=self.tok.linenum,
            )

        if "extends" not in context.tag_namespace:
            context.tag_namespace["extends"] = defaultdict(list)

        # Build a stack for each `{% block %}` (one stack per block name) in the
        # inheritance chain. The base template will be at the bottom of the "stack".

        stack_blocks(context, context.template)
        parent = context.get_template_with_context(
            self.name.evaluate(context), tag=self.tag
        )
        parent_template_name, _ = stack_blocks(context, parent)

        while parent_template_name:
            parent = context.get_template_with_context(
                parent_template_name, tag=self.tag
            )
            parent_template_name, _ = stack_blocks(context, parent)

        # The base template
        parent.render_with_context(context, buffer)
        context.tag_namespace["extends"].clear()
        raise StopRender()

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        if not context.template:
            raise LiquidEnvironmentError(
                "the 'extends' tag requires the current render context to keep a "
                "reference to its template as Context.template",
                linenum=self.tok.linenum,
            )

        if "extends" not in context.tag_namespace:
            context.tag_namespace["extends"] = defaultdict(list)

        stack_blocks(context, context.template)
        parent = await context.get_template_with_context_async(
            self.name.evaluate(context), tag=self.tag
        )
        parent_template_name, _ = stack_blocks(context, parent)

        while parent_template_name:
            parent = await context.get_template_with_context_async(
                parent_template_name, tag=self.tag
            )
            parent_template_name, _ = stack_blocks(context, parent)

        # The base template
        await parent.render_with_context_async(context, buffer)
        context.tag_namespace["extends"].clear()
        raise StopRender()

    def children(self) -> List[ChildNode]:
        return [
            ChildNode(
                linenum=self.tok.linenum,
                expression=self.name,
                load_mode="include",
                load_context={"tag": self.tag},
            )
        ]


class BlockTag(Tag):
    name = TAG_BLOCK
    end = TAG_ENDBLOCK

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=self.name)
        tok = next(stream)

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = ExprTokenStream(
            tokenize_common_expression(stream.current.value, linenum=tok.linenum)
        )
        block_name = self._parse_block_name(expr_stream)
        next(expr_stream)

        if expr_stream.current[2] == "required":
            required = True
            next(expr_stream)
        else:
            required = False

        expr_stream.expect(TOKEN_EOF)

        next(stream)
        block = self.parser.parse_block(stream, (self.end, TOKEN_EOF))
        expect(stream, TOKEN_TAG, value=self.end)

        if stream.peek.type == TOKEN_EXPRESSION:
            next(stream)
            expr_stream = ExprTokenStream(
                tokenize_common_expression(
                    stream.current.value, linenum=stream.current.linenum
                )
            )
            end_block_name = self._parse_block_name(expr_stream)
            next(expr_stream)
            expr_stream.expect(TOKEN_EOF)

            if end_block_name != block_name:
                raise TemplateInheritanceError(
                    f"expected endblock for {block_name}, found {end_block_name}",
                    linenum=stream.current.linenum,
                )

        return BlockNode(tok, block_name, block, required)

    def _parse_block_name(self, stream: ExprTokenStream) -> StringLiteral:
        if stream.current[1] in (TOKEN_IDENTIFIER, TOKEN_STRING):
            return StringLiteral(stream.current[2])
        raise LiquidSyntaxError(
            f"invalid identifier '{stream.current[2]}' for {self.name!r} tag",
            linenum=stream.current[0],
        )


class ExtendsTag(Tag):
    name = TAG_EXTENDS
    block = False

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=self.name)
        tok = next(stream)

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = ExprTokenStream(
            tokenize_common_expression(stream.current.value, linenum=tok.linenum)
        )
        parent_template_name = parse_string_literal(expr_stream)
        next(expr_stream)
        expr_stream.expect(TOKEN_EOF)
        return ExtendsNode(tok, parent_template_name)


def find_inheritance_nodes(
    template: BoundTemplate,
) -> Tuple[List["ExtendsNode"], List[BlockNode]]:
    extends_nodes: List["ExtendsNode"] = []
    block_nodes: List[BlockNode] = []

    for node in template.tree.statements:
        _visit_node(
            node,
            extends_nodes=extends_nodes,
            block_nodes=block_nodes,
        )

    return extends_nodes, block_nodes


def _visit_node(
    node: Node,
    extends_nodes: List["ExtendsNode"],
    block_nodes: List[BlockNode],
) -> None:
    if isinstance(node, BlockNode):
        block_nodes.append(node)

    if isinstance(node, ExtendsNode):
        extends_nodes.append(node)

    for child in node.children():
        if child.node:
            _visit_node(
                child.node,
                extends_nodes=extends_nodes,
                block_nodes=block_nodes,
            )


def stack_blocks(
    context: Context, template: BoundTemplate
) -> Tuple[Optional[str], List[BlockNode]]:
    extends, blocks = find_inheritance_nodes(template)

    if len(extends) > 1:
        raise TemplateInheritanceError(
            f"too many 'extends' tags",
            linenum=extends[1].tok.linenum,
            filename=template.path or template.name,
        )

    seen_block_names: Set[str] = set()
    for block in blocks:
        if block.name in seen_block_names:
            raise TemplateInheritanceError(
                f"duplicate block {block.name}", linenum=block.tok.linenum
            )
        seen_block_names.add(block.name)

    _store_blocks(context, blocks)

    if not extends:
        return None, blocks
    return extends[0].name.evaluate(context), blocks


def _store_blocks(context: Context, blocks: List[BlockNode]) -> None:
    block_stacks: DefaultDict[str, List[_BlockStackItem]] = context.tag_namespace[
        "extends"
    ]

    for block in blocks:
        stack = block_stacks[block.name]
        if stack and not block.required:
            required = False
        else:
            required = block.required
        stack.append(_BlockStackItem(block=block, required=required))
