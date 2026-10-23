from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .. import expressions
from .._drop import AbstractDrop
from .._markup import SCOPE_INHERITED, Partial, render_block, render_block_async
from .._nothing import NOTHING
from ..exceptions import (
    LiquidArgumentError,
    LiquidSyntaxError,
    NoSuchTemplateError,
    RequiredBlockError,
    TemplateInheritanceError,
    TemplateNotFoundError,
)
from ..expressions import Name
from ..tokens import (
    TOKEN_DOUBLE_QUOTE,
    TOKEN_IDENT,
    TOKEN_SINGLE_QUOTE,
    TOKEN_TAG_END,
    TOKEN_TAG_NAME,
    TOKEN_TAG_START,
    token_value,
)

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._io import StringBuffer
    from .._markup import Block, Expression, Markup
    from .._parser import Parser
    from .._template import Template
    from ..tokens import Token


class ExtendsTag:
    blank = False
    tag = "extend"

    __slots__ = ("name", "token")

    def __init__(self, token: Token, name: Name) -> None:
        self.token = token
        self.name = name

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        name = parser.parse_name()
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return ExtendsTag(token, name)

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        stacks: defaultdict[str, list[ExtendsStackItem]] = context.get_register(
            "extends", lambda: defaultdict(list)
        )

        base_template = self._stack_blocks(context, stacks)

        with context.extend({}, template=base_template):
            base_template.render_with_context(context, buffer)

        stacks.clear()
        context.interrupts.append("stop")

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        stacks: defaultdict[str, list[ExtendsStackItem]] = context.get_register(
            "extends", lambda: defaultdict(list)
        )

        base_template = self._stack_blocks(context, stacks)

        with context.extend({}, template=base_template):
            await base_template.render_with_context_async(context, buffer)

        stacks.clear()
        context.interrupts.append("stop")

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return []

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        template = context.env.get_template(
            self.name.value, context=context, tag="extends"
        )
        return [
            Partial(
                template=template,
                scope=SCOPE_INHERITED,
                in_scope=[],
                key=hash(self.name.value),
            )
        ]

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        template = await context.env.get_template_async(
            self.name.value, context=context, tag="extends"
        )

        return [
            Partial(
                template=template,
                scope=SCOPE_INHERITED,
                in_scope=[],
                key=hash(self.name.value),
            )
        ]

    def _stack_blocks(
        self, context: RenderContext, stacks: defaultdict[str, list[ExtendsStackItem]]
    ) -> Template:
        """Build a stack for each named block by visiting templates in the inheritance chain."""
        seen_extends: set[str] = set()

        def visit(template_: Template) -> Template | None:
            extends_nodes, block_nodes = self._find_extends_nodes(context, template_)

            seen_blocks: set[str] = set()

            for block in block_nodes:
                block_name = block.name.value
                if block_name in seen_blocks:
                    raise TemplateInheritanceError(
                        f"duplicate block {block_name!r}",
                        token=block.token,
                        source=template_.source,
                        name=template_.name,
                    )

                seen_blocks.add(block_name)
                stack = stacks[block_name]
                required = len(stack) > 1 and block.required

                stack_item = ExtendsStackItem(
                    block=block,
                    required=required,
                    template=template_,
                    parent=None,
                )

                if stack:
                    stack[-1].parent = stack_item

                stack.append(stack_item)

            if not extends_nodes:
                return None

            extends_node = extends_nodes[0]
            extends_name = extends_node.name.value

            if len(extends_nodes) > 1:
                raise TemplateInheritanceError(
                    "too many 'extends' tags",
                    token=extends_node.token,
                    source=template_.source,
                    name=template_.name,
                )

            if extends_name in seen_extends:
                raise TemplateInheritanceError(
                    f"circular extends {extends_name!r}",
                    token=extends_node.token,
                    source=template_.source,
                    name=template_.name,
                )

            seen_extends.add(extends_name)

            try:
                return context.env.get_template(
                    extends_name, context=context, tag="extends"
                )
            except TemplateNotFoundError as err:
                raise NoSuchTemplateError(
                    str(err),
                    token=extends_node.name.span,
                    source=template_.source,
                    name=template_.name,
                )

        next_template = visit(context.template)
        base = next_template

        while next_template:
            next_template = visit(next_template)
            if next_template:
                base = next_template

        assert base
        return base

    def _find_extends_nodes(
        self, context: RenderContext, template: Template
    ) -> tuple[list[ExtendsTag], list[BlockTag]]:
        extends_nodes: list[ExtendsTag] = []
        block_nodes: list[BlockTag] = []

        def visit(node: Markup) -> None:
            if isinstance(node, ExtendsTag):
                extends_nodes.append(node)
            elif isinstance(node, BlockTag):
                block_nodes.append(node)

            for child in node.children():
                visit(child)

        for node in template.nodes:
            if not isinstance(node, str):
                visit(node)

        return extends_nodes, block_nodes


class BlockTag:
    blank = False
    tag = "block"

    __slots__ = ("block", "name", "required", "token")

    def __init__(self, token: Token, name: Name, block: Block, required: bool) -> None:
        self.token = token
        self.name = name
        self.block = block
        self.required = required

    @classmethod
    def parse(cls, token: Token, parser: Parser) -> Markup:
        name = parser.parse_name()
        required = cls.unpack_args(parser, parser.parse_arguments(require_commas=True))
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        block = parser.parse_block(("endblock",))

        # Consume `{% endblock %}` with optional name: `{% endblock name %}`.
        parser.eat(
            TOKEN_TAG_START, message=f"expected tag 'endblock' for {name.value!r}"
        )
        parser.skip_whitespace_control()
        token_ = parser.eat(TOKEN_TAG_NAME, message="expected 'endblock'")

        if value := token_value(token_, parser.source) != "endblock":
            raise LiquidSyntaxError(
                f"expected endblock for {name!r}, found {value!r}",
                token=token,
                source=parser.source,
                name=parser.template_name,
            )

        if parser.kind() in (TOKEN_IDENT, TOKEN_SINGLE_QUOTE, TOKEN_DOUBLE_QUOTE):
            end_name = parser.parse_name()
            if end_name.value != name.value:
                raise TemplateInheritanceError(
                    f"expected endblock for {name!r}, found {end_name.value!r}",
                    token=end_name.span,
                    source=parser.source,
                    name=parser.template_name,
                )

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END, message="expected a closing tag delimiter")

        return BlockTag(token, name, block, required)

    @classmethod
    def unpack_args(
        cls, parser: Parser, args: list[Expression | expressions.KeywordArgument]
    ) -> bool:
        required = False

        for arg in args:
            if (
                isinstance(arg, expressions.Variable)
                and isinstance(arg.root, Name)
                and arg.root.value == "required"
                and arg.selectors is None
            ):
                required = True
            else:
                raise LiquidArgumentError(
                    "unexpected argument",
                    token=arg.span,
                    source=parser.source,
                    name=parser.template_name,
                )

        return required

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        stacks: defaultdict[str, list[ExtendsStackItem]] = context.get_register(
            "extends", lambda: defaultdict(list)
        )

        stack = stacks[self.name.value]

        if not stack:
            # This is a base block being rendered directly
            if self.required:
                raise RequiredBlockError(
                    f"block {self.name.value!r} is required",
                    token=self.name.span,
                    source=context.template.source,
                    name=context.template.name,
                )

            with context.extend({"block": BlockDrop(self.name.value)}):
                render_block(self.block, context, buffer)

            return

        itm = stack[0]

        if itm.block.required:
            raise RequiredBlockError(
                f"block {self.name.value!r} is required",
                token=self.name.span,
                source=context.template.source,
                name=context.template.name,
            )

        scope: dict[str, object] = {"block": BlockDrop(self.name.value, itm.parent)}
        block_context = context.copy(scope, block_scope=True, template=itm.template)
        render_block(itm.block.block, block_context, buffer)
        context.render_score_cumulative += block_context.render_score

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        stacks: defaultdict[str, list[ExtendsStackItem]] = context.get_register(
            "extends", lambda: defaultdict(list)
        )

        stack = stacks[self.name.value]

        if not stack:
            # This is a base block being rendered directly
            if self.required:
                raise RequiredBlockError(
                    f"block {self.name.value!r} is required",
                    token=self.name.span,
                    source=context.template.source,
                    name=context.template.name,
                )

            with context.extend({"block": BlockDrop(self.name.value)}):
                await render_block_async(self.block, context, buffer)

            return

        itm = stack[0]

        if itm.block.required:
            raise RequiredBlockError(
                f"block {self.name.value!r} is required",
                token=self.name.span,
                source=context.template.source,
                name=context.template.name,
            )

        scope: dict[str, object] = {"block": BlockDrop(self.name.value, itm.parent)}
        block_context = context.copy(scope, block_scope=True, template=itm.template)
        await render_block_async(itm.block.block, block_context, buffer)
        context.render_score_cumulative += block_context.render_score

    def children(self) -> list[Markup]:
        return [node for node in self.block if not isinstance(node, str)]

    def expressions(self) -> list[Expression]:
        return []

    def block_scope(self) -> list[Name]:
        return [Name(self.token, "block")]

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []


@dataclass(slots=True, kw_only=True)
class ExtendsStackItem:
    block: BlockTag
    required: bool
    template: Template
    parent: ExtendsStackItem | None


class BlockDrop(AbstractDrop):
    __slots__ = ("name", "parent")

    def __init__(self, name: str, parent: ExtendsStackItem | None = None) -> None:
        super().__init__()
        self.name = name
        self.parent = parent

    def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
        return name == "super"

    def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
        if self.parent is None or name != "super":
            return NOTHING

        buffer = context.env.buffer_factory()

        scope: dict[str, object] = {
            "block": BlockDrop(self.parent.template.name, self.parent.parent)
        }

        with context.extend(scope, template=self.parent.template):
            render_block(self.parent.block.block, context, buffer)

        return buffer.getvalue()

    async def __liquid_hasattr_async__(self, name: str, context: RenderContext) -> bool:
        return name == "super"

    async def __liquid_getattr_async__(
        self, name: str, context: RenderContext
    ) -> object:
        if self.parent is None or name != "super":
            return NOTHING

        buffer = context.env.buffer_factory()

        scope: dict[str, object] = {
            "block": BlockDrop(self.parent.template.name, self.parent.parent)
        }

        with context.extend(scope, template=self.parent.template):
            await render_block_async(self.parent.block.block, context, buffer)

        return buffer.getvalue()

    def __str__(self) -> str:
        return f"BlockDrop({self.name})"
