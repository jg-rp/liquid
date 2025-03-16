"""The standard _extends_ and _block_ tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import DefaultDict
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import TextIO

from markupsafe import Markup as Markupsafe

from liquid.ast import BlockNode as TemplateBlock
from liquid.ast import Node
from liquid.ast import Partial
from liquid.ast import PartialScope
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import StringLiteral
from liquid.builtin.expressions import parse_name
from liquid.exceptions import RequiredBlockError
from liquid.exceptions import StopRender
from liquid.exceptions import TemplateInheritanceError
from liquid.exceptions import TemplateNotFoundError
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_REQUIRED
from liquid.token import TOKEN_TAG

if TYPE_CHECKING:
    from liquid import BoundTemplate
    from liquid import RenderContext
    from liquid import Token
    from liquid import TokenStream


class ExtendsNode(Node):
    """The standard _extends_ tag."""

    __slots__ = ("name",)
    tag = "extends"

    def __init__(self, token: Token, name: Identifier) -> None:
        super().__init__(token)
        self.name = name
        self.blank = False

    def __str__(self) -> str:
        return f"{{% extends {self.name} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        base_template = _build_block_stacks(context, context.template, "extends")

        base_template.render_with_context(context, buffer)
        context.tag_namespace["extends"].clear()
        raise StopRender

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        base_template = await _build_block_stacks_async(
            context, context.template, "extends"
        )

        await base_template.render_with_context_async(context, buffer)
        context.tag_namespace["extends"].clear()
        raise StopRender

    def children(
        self, static_context: RenderContext, *, include_partials: bool = True
    ) -> Iterable[Node]:
        """Return this node's children."""
        if include_partials:
            try:
                parent = static_context.env.get_template(
                    self.name, context=static_context, tag=self.tag
                )
                yield from parent.nodes
            except TemplateNotFoundError as err:
                err.token = self.name.token
                err.template_name = static_context.template.full_name()
                raise

    async def children_async(
        self, static_context: RenderContext, *, include_partials: bool = True
    ) -> Iterable[Node]:
        """Return this node's children."""
        if include_partials:
            try:
                parent = await static_context.env.get_template_async(
                    self.name, context=static_context, tag=self.tag
                )
                return parent.nodes
            except TemplateNotFoundError as err:
                err.token = self.name.token
                err.template_name = static_context.template.full_name()
                raise
        return []

    def partial_scope(self) -> Optional[Partial]:
        """Return information about a partial template loaded by this node."""
        return Partial(
            name=StringLiteral(self.name.token, self.name),
            scope=PartialScope.INHERITED,
            in_scope=[],
        )


class ExtendsTag(Tag):
    """The standard _extends_ tag."""

    name = "extends"
    block = False
    node_class = ExtendsNode

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token, eat=False)
        name = parse_name(self.env, tokens)
        tokens.expect_eos()
        return self.node_class(token=token, name=name)


class BlockNode(Node):
    """The standard _block_ tag."""

    __slots__ = ("name", "block", "required")
    tag = "block"

    def __init__(
        self,
        token: Token,
        name: str,
        block: TemplateBlock,
        *,
        required: bool,
    ) -> None:
        super().__init__(token)
        self.name = name
        self.block = block
        self.required = required
        self.blank = False

    def __str__(self) -> str:
        required = " required" if self.required else ""
        return (
            f"{{% block {self.name}{required} %}}"
            f"{self.block}"
            f"{{% endblock {self.name} %}}"
        )

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        # We should be in a base template. Render the block at the top of the "stack".
        block_stack: Sequence[_BlockStackItem] = context.tag_namespace.get(
            "extends", {}
        ).get(self.name)

        if not block_stack:
            # This base template is being rendered directly.
            if self.required:
                raise RequiredBlockError(
                    f"block {self.name!r} must be overridden", token=self.token
                )
            with context.extend(
                {
                    "block": BlockDrop(
                        token=self.token,
                        context=context,
                        buffer=buffer,
                        name=self.name,
                        parent=None,
                    )
                }
            ):
                return self.block.render(context, buffer)

        stack_item = block_stack[0]

        if stack_item.required:
            raise RequiredBlockError(
                f"block {self.name!r} must be overridden",
                token=self.token,
                template_name=stack_item.source_name,
            )

        ctx = context.copy(
            namespace={
                "block": BlockDrop(
                    token=self.token,
                    context=context,
                    buffer=buffer,
                    name=self.name,
                    parent=stack_item.parent,
                )
            },
            carry_loop_iterations=True,
            block_scope=True,
        )

        return stack_item.block.block.render(ctx, buffer)

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        # We should be in a base template. Render the block at the top of the "stack".
        block_stack: Sequence[_BlockStackItem] = context.tag_namespace.get(
            "extends", {}
        ).get(self.name)

        if not block_stack:
            # This base template is being rendered directly.
            if self.required:
                raise RequiredBlockError(
                    f"block {self.name!r} must be overridden", token=self.token
                )
            with context.extend(
                {
                    "block": BlockDrop(
                        token=self.token,
                        context=context,
                        buffer=buffer,
                        name=self.name,
                        parent=None,
                    )
                }
            ):
                return await self.block.render_async(context, buffer)

        stack_item = block_stack[0]

        if stack_item.required:
            raise RequiredBlockError(
                f"block {self.name!r} must be overridden",
                token=self.token,
                template_name=stack_item.source_name,
            )

        ctx = context.copy(
            namespace={
                "block": BlockDrop(
                    token=self.token,
                    context=context,
                    buffer=buffer,
                    name=self.name,
                    parent=stack_item.parent,
                )
            },
            carry_loop_iterations=True,
            block_scope=True,
        )
        return await stack_item.block.block.render_async(ctx, buffer)

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's expressions."""
        yield self.block

    def block_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the node's block scope."""
        yield Identifier("block", token=self.token)


class BlockTag(Tag):
    """The standard _extends_ tag."""

    name = "block"
    block = True
    node_class = BlockNode
    end_block = frozenset(["endblock"])

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token)
        block_name = parse_name(self.env, tokens)

        if tokens.current.kind == TOKEN_REQUIRED:
            required = True
            next(tokens)
        else:
            required = False

        tokens.expect_eos()

        parse_block = get_parser(self.env).parse_block
        block = parse_block(stream, self.end_block)

        stream.expect(TOKEN_TAG, "endblock")
        end_block_token = stream.current

        if stream.peek.kind == TOKEN_EXPRESSION:
            next(stream)
            tokens = stream.into_inner(tag=token, eat=False)
            if tokens.current.kind != TOKEN_EOF:
                end_block_name = parse_name(self.env, tokens)
                if end_block_name != block_name:
                    raise TemplateInheritanceError(
                        f"expected endblock for '{block_name}, "
                        f"found '{end_block_name}'",
                        token=end_block_token,
                    )
                next(tokens)
            tokens.expect_eos()

        return self.node_class(
            token=token,
            name=block_name,
            block=block,
            required=required,
        )


@dataclass
class _BlockStackItem:
    token: Token
    block: BlockNode
    required: bool
    source_name: str
    parent: Optional[_BlockStackItem] = None


class BlockDrop(Mapping[str, object]):
    """A `block` object with a `super` property."""

    __slots__ = ("token", "buffer", "context", "name", "parent")

    def __init__(
        self,
        *,
        token: Token,
        context: RenderContext,
        buffer: TextIO,
        name: str,
        parent: Optional[_BlockStackItem],
    ) -> None:
        self.token = token
        self.buffer = buffer
        self.context = context
        self.name = name
        self.parent = parent

    def __str__(self) -> str:  # pragma: no cover
        return f"BlockDrop({self.name})"

    def __getitem__(self, key: str) -> object:
        if key != "super":
            raise KeyError(key)

        if not self.parent:
            return self.context.env.undefined("super", token=self.token)

        # NOTE: We're not allowing chaining of references to `super` for now.
        # Just the immediate parent.
        buf = self.context.get_buffer(self.buffer)
        with self.context.extend(
            {
                "block": BlockDrop(
                    token=self.parent.token,
                    context=self.context,
                    buffer=buf,
                    name=self.parent.source_name,
                    parent=self.parent.parent,
                )
            }
        ):
            self.parent.block.block.render(self.context, buf)

        if self.context.autoescape:
            return Markupsafe(buf.getvalue())
        return buf.getvalue()

    def __len__(self) -> int:  # pragma: no cover
        return 1

    def __iter__(self) -> Iterator[str]:  # pragma: no cover
        return iter(["super"])


def _build_block_stacks(
    context: RenderContext,
    template: BoundTemplate,
    tag: str,
) -> BoundTemplate:
    """Build a stack for each `{% block %}` in the inheritance chain.

    Blocks defined in the base template will be at the top of the stack.

    Args:
        context: A render context to build the block stacks in.
        template: A leaf template with an `extends` tag.
        parent_name: The name of the immediate parent template as a string literal.
        tag: The name of the `extends` tag, if it is overridden.
    """
    # Guard against recursive `extends`.
    seen: set[str] = set()

    def _stack_template_blocks(template: BoundTemplate) -> Optional[BoundTemplate]:
        extends_node, _ = _stack_blocks(context, template)

        if not extends_node:
            return None

        if extends_node.name in seen:
            raise TemplateInheritanceError(
                f"circular extends {extends_node.name!r}",
                token=extends_node.token,
                template_name=template.name,
            )

        seen.add(extends_node.name)

        try:
            return context.env.get_template(extends_node.name, context=context, tag=tag)
        except TemplateNotFoundError as err:
            err.token = extends_node.name.token
            err.template_name = template.full_name()
            raise

    base = next_template = _stack_template_blocks(template)

    while next_template:
        next_template = _stack_template_blocks(next_template)
        if next_template:
            base = next_template

    assert base
    return base


async def _build_block_stacks_async(
    context: RenderContext,
    template: BoundTemplate,
    tag: str,
) -> BoundTemplate:
    """Build a stack for each `{% block %}` in the inheritance chain.

    Blocks defined in the base template will be at the top of the stack.

    Args:
        context: A render context to build the block stacks in.
        template: A leaf template with an `extends` tag.
        parent_name: The name of the immediate parent template as a string.
        tag: The name of the `extends` tag, if it is overridden.
    """
    # Guard against recursive `extends`.
    seen: set[str] = set()

    async def _stack_template_blocks(
        template: BoundTemplate,
    ) -> Optional[BoundTemplate]:
        extends_node, _ = _stack_blocks(context, template)

        if not extends_node:
            return None

        if extends_node.name in seen:
            raise TemplateInheritanceError(
                f"circular extends {extends_node.name!r}",
                token=extends_node.token,
                template_name=template.name,
            )

        seen.add(extends_node.name)

        try:
            return await context.env.get_template_async(
                extends_node.name, context=context, tag=tag
            )
        except TemplateNotFoundError as err:
            err.token = extends_node.name.token
            err.template_name = template.full_name()
            raise

    base = next_template = await _stack_template_blocks(template)

    while next_template:
        next_template = await _stack_template_blocks(next_template)
        if next_template:
            base = next_template

    assert base
    return base


def _find_inheritance_nodes(
    template: BoundTemplate, context: RenderContext
) -> tuple[list["ExtendsNode"], list[BlockNode]]:
    """Return lists of `extends` and `block` nodes from the given template."""
    extends_nodes: list["ExtendsNode"] = []
    block_nodes: list[BlockNode] = []

    def _visit_node(node: Node, context: RenderContext) -> None:
        if isinstance(node, BlockNode):
            block_nodes.append(node)

        if isinstance(node, ExtendsNode):
            extends_nodes.append(node)

        for child in node.children(context, include_partials=False):
            _visit_node(child, context=context)

    for node in template.nodes:
        _visit_node(node, context=context)

    return extends_nodes, block_nodes


def _stack_blocks(
    context: RenderContext, template: BoundTemplate
) -> tuple[Optional[ExtendsNode], list[BlockNode]]:
    """Find template inheritance nodes in `template`.

    Each node found is pushed on to the appropriate block stack.
    """
    extends, blocks = _find_inheritance_nodes(template, context)
    template_name = str(template.path or template.name)

    if len(extends) > 1:
        raise TemplateInheritanceError(
            "too many 'extends' tags",
            token=extends[1].token,
            template_name=template_name,
        )

    seen_block_names: set[str] = set()
    for block in blocks:
        if block.name in seen_block_names:
            raise TemplateInheritanceError(
                f"duplicate block {block.name}",
                token=block.token,
            )
        seen_block_names.add(block.name)

    _store_blocks(context, blocks, template_name)

    if not extends:
        return None, blocks
    # return extends[0].name.evaluate(context), blocks
    return extends[0], blocks


def _store_blocks(
    context: RenderContext, blocks: list[BlockNode], source_name: str
) -> None:
    block_stacks: DefaultDict[str, list[_BlockStackItem]] = context.tag_namespace[
        "extends"
    ]

    for block in blocks:
        stack = block_stacks[block.name]
        required = False if stack and not block.required else block.required

        stack.append(
            _BlockStackItem(
                token=block.token,
                block=block,
                required=required,
                source_name=source_name,
            )
        )

        if len(stack) > 1:
            stack[-2].parent = stack[-1]
