"""The built-in _render_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import TextIO

from liquid.ast import Node
from liquid.ast import Partial
from liquid.ast import PartialScope
from liquid.builtin.drops import IterableDrop
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import KeywordArgument
from liquid.builtin.expressions import Literal
from liquid.builtin.expressions import Path
from liquid.builtin.expressions import StringLiteral
from liquid.builtin.expressions import parse_identifier
from liquid.builtin.expressions import parse_primitive
from liquid.builtin.tags.for_tag import ForLoop
from liquid.builtin.tags.include_tag import TAG_INCLUDE
from liquid.exceptions import TemplateNotFoundError
from liquid.tag import Tag
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_WORD
from liquid.token import Token
from liquid.utils import ReadOnlyChainMap

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream


TAG_RENDER = sys.intern("render")


class RenderNode(Node):
    """The built-in _render_ tag."""

    __slots__ = ("name", "var", "loop", "alias", "args")
    tag = TAG_RENDER

    def __init__(
        self,
        token: Token,
        name: StringLiteral,
        var: Optional[Expression] = None,
        loop: bool = False,
        alias: Optional[Identifier] = None,
        args: Optional[list[KeywordArgument]] = None,
    ):
        super().__init__(token)
        self.name = name
        self.var = var
        self.loop = loop
        self.alias = alias
        self.args = args or []
        self.blank = False

    def __str__(self) -> str:
        var = ""
        if self.var:
            var = f" for {self.var}" if self.loop else f" with {self.var}"
        if self.alias:
            var += f" as {self.alias}"
        if self.args:
            var += ","
        args = " " + ", ".join(str(arg) for arg in self.args) if self.args else ""
        return f"{{% render {self.name}{var}{args} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        try:
            template = context.env.get_template(
                self.name.value, context=context, tag=self.tag
            )
        except TemplateNotFoundError as err:
            err.token = self.name.token
            err.template_name = context.template.full_name()
            raise

        # Evaluate keyword arguments once. Unlike 'include', 'render' can not
        # mutate variables in the outer scope, so there's no need to re-evaluate
        # arguments for each loop (if any).
        args = {arg.name: arg.value.evaluate(context) for arg in self.args}

        # We're using a chain map here in case we need to push a forloop drop into
        # it. As drops are read only, the built-in collections.ChainMap will not do.
        namespace = ReadOnlyChainMap(args)

        # New context with globals and filters from the parent, plus the read only
        # namespace containing render arguments and bound variable.
        ctx = context.copy(
            namespace,
            disabled_tags=[TAG_INCLUDE],
            carry_loop_iterations=True,
            template=template,
        )

        # Optionally bind a variable to the render namespace.
        if self.var is not None:
            val = self.var.evaluate(context)
            key = self.alias or template.name.split(".")[0]

            # If the variable is array-like, render the template once for each item.
            # `self.loop` being True indicates the render expression used "for" not
            # "with". This distinction is not made when using the 'include' tag.
            if self.loop and isinstance(val, (tuple, list, IterableDrop)):
                ctx.raise_for_loop_limit(len(val))
                forloop = ForLoop(
                    name=key,
                    it=iter(val),
                    length=len(val),
                    parentloop=context.env.undefined("parentloop", token=self.token),
                )

                args["forloop"] = forloop
                args[key] = None

                for itm in forloop:
                    args[key] = itm
                    template.render_with_context(
                        ctx, buffer, partial=True, block_scope=True
                    )
            else:
                # The bound variable is not array-like, shove it into the namespace
                # via args.
                args[key] = val
                template.render_with_context(
                    ctx, buffer, partial=True, block_scope=True
                )
        else:
            template.render_with_context(ctx, buffer, partial=True, block_scope=True)

        return True

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        try:
            template = await context.env.get_template_async(
                self.name.value, context=context, tag=self.tag
            )
        except TemplateNotFoundError as err:
            err.token = self.name.token
            err.template_name = context.template.full_name()
            raise

        # Evaluate keyword arguments once. Unlike 'include', 'render' can not
        # mutate variables in the outer scope, so there's no need to re-evaluate
        # arguments for each loop (if any).
        args = {arg.name: await arg.value.evaluate_async(context) for arg in self.args}

        # We're using a chain map here in case we need to push a forloop drop into
        # it. As drops are read only, the built-in collections.ChainMap will not do.
        namespace = ReadOnlyChainMap(args)

        # New context with globals and filters from the parent, plus the read only
        # namespace containing render arguments and bound variable.
        ctx = context.copy(
            namespace,
            disabled_tags=[TAG_INCLUDE],
            carry_loop_iterations=True,
            template=template,
        )

        # Optionally bind a variable to the render namespace.
        if self.var is not None:
            val = await self.var.evaluate_async(context)
            key = self.alias or template.name.split(".")[0]

            # If the variable is array-like, render the template once for each item.
            # `self.loop` being True indicates the render expression used "for" not
            # "with". This distinction is not made when using the 'include' tag.
            if self.loop and isinstance(val, (tuple, list, IterableDrop)):
                ctx.raise_for_loop_limit(len(val))
                forloop = ForLoop(
                    name=key,
                    it=iter(val),
                    length=len(val),
                    parentloop=context.env.undefined("parentloop", token=self.token),
                )

                args["forloop"] = forloop
                args[key] = None

                for itm in forloop:
                    args[key] = itm
                    await template.render_with_context_async(
                        ctx, buffer, partial=True, block_scope=True
                    )
            else:
                # The bound variable is not array-like, shove it into the namespace
                # via args.
                args[key] = val
                await template.render_with_context_async(
                    ctx, buffer, partial=True, block_scope=True
                )
        else:
            await template.render_with_context_async(
                ctx, buffer, partial=True, block_scope=True
            )

        return True

    def children(
        self, static_context: RenderContext, *, include_partials: bool = True
    ) -> Iterable[Node]:
        """Return this node's children."""
        if include_partials:
            name = self.name.evaluate(static_context)
            try:
                template = static_context.env.get_template(
                    str(name), context=static_context, tag=self.tag
                )
                yield from template.nodes
            except TemplateNotFoundError as err:
                err.token = self.name.token
                err.template_name = static_context.template.full_name()
                raise

    async def children_async(
        self, static_context: RenderContext, *, include_partials: bool = True
    ) -> Iterable[Node]:
        """Return this node's children."""
        if include_partials:
            name = await self.name.evaluate_async(static_context)
            try:
                template = await static_context.env.get_template_async(
                    str(name), context=static_context, tag=self.tag
                )
                return template.nodes
            except TemplateNotFoundError as err:
                err.token = self.name.token
                err.template_name = static_context.template.full_name()
                raise
        return []

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.name
        if self.var:
            yield self.var
        yield from (arg.value for arg in self.args)

    def partial_scope(self) -> Partial | None:
        """Return information about a partial template loaded by this node."""
        scope: list[Identifier] = [
            Identifier(arg.name, token=arg.token) for arg in self.args
        ]

        if self.var:
            if self.alias:
                scope.append(self.alias)
            elif isinstance(self.name, Literal):
                scope.append(
                    Identifier(
                        str(self.name.value).split(".", 1)[0], token=self.name.token
                    )
                )

        return Partial(name=self.name, scope=PartialScope.ISOLATED, in_scope=scope)


BIND_TAGS = frozenset((TOKEN_WITH, TOKEN_FOR))


class RenderTag(Tag):
    """The built-in _render_ tag."""

    name = TAG_RENDER
    block = False
    node_class = RenderNode

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token, eat=False)

        # Need a string. 'render' does not accept identifiers that resolve to a string.
        # This is the name of the template to be included.
        tokens.expect(TOKEN_STRING)
        name = parse_primitive(self.env, tokens)
        assert isinstance(name, StringLiteral)

        alias: Optional[Identifier] = None
        var: Optional[Path] = None
        loop: bool = False

        # Optionally bind a variable to the included template context
        if tokens.current.kind in BIND_TAGS:
            loop = tokens.current.kind == TOKEN_FOR
            next(tokens)  # Eat 'with' or 'for'
            tokens.expect(TOKEN_WORD)
            var = Path.parse(self.env, tokens)

            # The bound variable will take the name of the template by default,
            # or an alias if an identifier follows the "as" keyword.
            if tokens.current.kind == TOKEN_AS:
                next(tokens)  # Eat 'as'
                tokens.expect(TOKEN_WORD)
                alias = parse_identifier(self.env, tokens)

        # Zero or more keyword arguments
        args = KeywordArgument.parse(self.env, tokens)
        return self.node_class(token, name, var, loop, alias, args)
