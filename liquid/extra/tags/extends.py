"""Template inheritance tags."""
from __future__ import annotations
import sys

from collections import defaultdict
from collections import deque

from typing import Deque
from typing import DefaultDict
from typing import Iterator
from typing import List
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import TextIO
from typing import Tuple
from typing import TYPE_CHECKING

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode as TemplateBlockNode

from liquid.context import Context

from liquid.exceptions import LiquidEnvironmentError
from liquid.exceptions import StopRender
from liquid.exceptions import TemplateInheritanceError

from liquid.expression import Expression
from liquid.expression import StringLiteral

from liquid.expressions import TokenStream as ExprTokenStream
from liquid.expressions.common import parse_string_literal
from liquid.expressions.common import parse_string_or_identifier
from liquid.expressions.common import tokenize_common_expression

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid import BoundTemplate


TAG_EXTENDS = sys.intern("extends")
TAG_BLOCK = sys.intern("block")
TAG_ENDBLOCK = sys.intern("endblock")


class BlockDrop(Mapping[str, object]):
    __slots__ = ("buffer", "context", "name", "super")

    def __init__(
        self, context: Context, buffer: TextIO, name: str, parent: Optional["BlockNode"]
    ) -> None:
        self.buffer = buffer
        self.context = context
        self.name = name
        self.parent = parent

    def __str__(self) -> str:
        return f"Block({self.name})"

    def __getitem__(self, key: str) -> object:
        if key != "super":
            raise KeyError(key)

        if not self.parent:
            return self.context.env.undefined("super")

        buf = self.context.get_buffer(self.buffer)
        self.parent.render(self.context, buf)
        return buf.getvalue()

    def __len__(self) -> int:
        return 1

    def __iter__(self) -> Iterator[str]:
        return iter(["super"])


class BlockNodeDropPair(NamedTuple):
    block: "BlockNode"
    drop: BlockDrop


class BlockNode(Node):
    __slots__ = ("tok", "name", "block", "expr")

    def __init__(self, tok: Token, name: Expression, block: TemplateBlockNode) -> None:
        self.tok = tok
        self.expr = name
        self.name = str(name)
        self.block = block

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        # We should be in a base template. Render the block at the bottom of the stack.
        block_stack: Sequence[BlockNodeDropPair] = context.tag_namespace["extends"].get(
            self.name
        )

        if not block_stack:
            # This base template is being rendered directly.
            with context.extend({"block": BlockDrop(context, buffer, self.name, None)}):
                return self.block.render(context, buffer)

        block, drop = block_stack[-1]

        with context.extend({"block": drop}):
            return block.render(context, buffer)

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        # We should be in a base template. Render the block at the bottom of the stack.
        block_stack: Sequence[BlockNodeDropPair] = context.tag_namespace["extends"].get(
            self.name
        )

        if not block_stack:
            # This base template is being rendered directly.
            with context.extend({"block": BlockDrop(context, buffer, self.name, None)}):
                return await self.block.render_async(context, buffer)

        block, drop = block_stack[-1]

        with context.extend({"block": drop}):
            return await block.render_async(context, buffer)

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
            context.tag_namespace["extends"] = defaultdict(deque)

        extends, blocks = self._find_inheritance_nodes(context.template)

        if extends:
            raise TemplateInheritanceError(
                f"too many {self.tag!r} tags", linenum=self.tok.linenum
            )

        self._store_blocks(context, buffer, blocks)

        parent = context.get_template_with_context(
            self.name.evaluate(context), tag=self.tag
        )
        parent_template_name, blocks = self._parent_template_blocks(
            context, buffer, parent
        )

        while parent_template_name:
            parent = context.get_template_with_context(
                parent_template_name, tag=self.tag
            )
            parent_template_name, blocks = self._parent_template_blocks(
                context, buffer, parent
            )
            self._store_blocks(context, buffer, blocks)

        # The base template
        parent.render_with_context(context, buffer)
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
            context.tag_namespace["extends"] = defaultdict(deque)

        extends, blocks = self._find_inheritance_nodes(context.template)

        if extends:
            raise TemplateInheritanceError(
                f"too many {self.tag!r} tags", linenum=self.tok.linenum
            )

        self._store_blocks(context, buffer, blocks)

        parent = await context.get_template_with_context_async(
            self.name.evaluate(context), tag=self.tag
        )
        parent_template_name, blocks = self._parent_template_blocks(
            context, buffer, parent
        )

        while parent_template_name:
            parent = await context.get_template_with_context_async(
                parent_template_name, tag=self.tag
            )
            parent_template_name, blocks = self._parent_template_blocks(
                context, buffer, parent
            )

        # The base template
        await parent.render_with_context_async(context, buffer)
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

    def _find_inheritance_nodes(
        self, template: BoundTemplate
    ) -> Tuple[List["ExtendsNode"], List[BlockNode]]:
        extends_nodes: List["ExtendsNode"] = []
        block_nodes: List[BlockNode] = []

        for node in template.tree.statements:
            self._visit_node(
                node,
                extends_nodes=extends_nodes,
                block_nodes=block_nodes,
            )

        return extends_nodes, block_nodes

    def _visit_node(
        self,
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
                self._visit_node(
                    node,
                    extends_nodes=extends_nodes,
                    block_nodes=block_nodes,
                )

    def _parent_template_blocks(
        self, context: Context, buffer: TextIO, parent: BoundTemplate
    ) -> Tuple[Optional[str], List[BlockNode]]:
        extends, blocks = self._find_inheritance_nodes(parent)

        if len(extends) > 1:
            raise TemplateInheritanceError(
                f"too many {self.tag!r} tags", linenum=self.tok.linenum
            )

        self._store_blocks(context, buffer, blocks)

        if not extends:
            return None, blocks
        return extends[0].name.evaluate(context), blocks

    def _store_blocks(
        self, context: Context, buffer: TextIO, blocks: List[BlockNode]
    ) -> None:
        block_stacks: DefaultDict[
            str, Deque[BlockNodeDropPair]
        ] = context.tag_namespace["extends"]

        # TODO: raise/warn on duplicate block names in the same template

        for block in blocks:
            stack = block_stacks[block.name]
            if not stack:
                drop = BlockDrop(context, buffer, block.name, None)
            else:
                drop = BlockDrop(context, buffer, block.name, stack[-1].block)
            block_stacks[block.name].append(BlockNodeDropPair(block=block, drop=drop))


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
        block_name = parse_string_or_identifier(expr_stream)
        next(expr_stream)
        expr_stream.expect(TOKEN_EOF)
        next(stream)

        block = self.parser.parse_block(stream, (self.end, TOKEN_EOF))
        expect(stream, TOKEN_TAG, value=self.end)
        return BlockNode(tok, block_name, block)


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
