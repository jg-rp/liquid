"""The built-in _include_ tag."""

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
from liquid.builtin.expressions import parse_identifier
from liquid.builtin.expressions import parse_string_or_path
from liquid.exceptions import TemplateNotFoundError
from liquid.tag import Tag
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_WORD
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream

TAG_INCLUDE = sys.intern("include")


class IncludeNode(Node):
    """The built-in _include_ tag."""

    __slots__ = ("name", "var", "alias", "args")
    tag = TAG_INCLUDE

    def __init__(
        self,
        token: Token,
        name: Expression,
        var: Optional[Expression] = None,
        alias: Optional[Identifier] = None,
        args: Optional[list[KeywordArgument]] = None,
    ):
        super().__init__(token)
        self.name = name
        self.var = var
        self.alias = alias
        self.args = args or []
        self.blank = False

    def __str__(self) -> str:
        var = f" with {self.var}" if self.var else ""
        if self.alias:
            var += f" as {self.alias}"
        if self.args:
            var += ","
        args = " " + ", ".join(str(arg) for arg in self.args) if self.args else ""
        return f"{{% include {self.name}{var}{args} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        name = self.name.evaluate(context)

        try:
            template = context.env.get_template(
                str(name), context=context, tag=self.tag
            )
        except TemplateNotFoundError as err:
            err.token = self.name.token
            err.template_name = context.template.full_name()
            raise

        namespace: dict[str, object] = {
            arg.name: arg.value.evaluate(context) for arg in self.args
        }

        with context.extend(namespace, template=template):
            # Bind a variable to the included template.
            if self.var is not None:
                val = self.var.evaluate(context)
                key = self.alias or template.name.split(".")[0]

                # If the variable is array-like, render the template once for each
                # item in the array.
                #
                # The reference implementation does not seem to distinguish between
                # "for" and "with". Just checks for array-like-ness.
                if isinstance(val, (tuple, list, IterableDrop)):
                    # NOTE: What if an included template with a bound array updates
                    # a keyword argument value? Do we need to update namespace
                    # arguments after each loop?
                    #
                    # The reference implementation seems to evaluate arguments once,
                    # before the loop.
                    context.raise_for_loop_limit(len(val))
                    for itm in val:
                        namespace[key] = itm
                        template.render_with_context(context, buffer, partial=True)
                else:
                    namespace[key] = val
                    template.render_with_context(context, buffer, partial=True)
            else:
                template.render_with_context(context, buffer, partial=True)

        return True

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        name = await self.name.evaluate_async(context)

        try:
            template = await context.env.get_template_async(
                str(name), context=context, tag=self.tag
            )
        except TemplateNotFoundError as err:
            err.token = self.name.token
            err.template_name = context.template.full_name()
            raise

        namespace: dict[str, object] = {
            arg.name: await arg.value.evaluate_async(context) for arg in self.args
        }

        with context.extend(namespace, template=template):
            if self.var is not None:
                val = await self.var.evaluate_async(context)
                key = self.alias or template.name.split(".")[0]

                if isinstance(val, (tuple, list, IterableDrop)):
                    context.raise_for_loop_limit(len(val))
                    for itm in val:
                        namespace[key] = itm
                        await template.render_with_context_async(
                            context, buffer, partial=True
                        )
                else:
                    namespace[key] = val
                    await template.render_with_context_async(
                        context, buffer, partial=True
                    )
            else:
                await template.render_with_context_async(context, buffer, partial=True)

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

        return Partial(name=self.name, scope=PartialScope.SHARED, in_scope=scope)


BIND_TOKENS = frozenset((TOKEN_WITH, TOKEN_FOR))


class IncludeTag(Tag):
    """The built-in _include_ tag."""

    name = TAG_INCLUDE
    block = False
    node_class = IncludeNode

    def parse(self, stream: TokenStream) -> Node:
        """Read an IncludeNode from the given stream of tokens."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token, eat=False)

        # Need a string or identifier that resolves to a string. This is the name
        # of the template to be included.
        name = parse_string_or_path(self.env, tokens)
        var: Optional[Path] = None
        alias: Optional[Identifier] = None

        # Optionally bind a variable to the included template context
        if tokens.current.kind in BIND_TOKENS:
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
        return self.node_class(token, name, var, alias, args)
