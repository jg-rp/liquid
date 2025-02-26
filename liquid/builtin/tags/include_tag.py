"""The built-in _include_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.builtin.drops import IterableDrop
from liquid.builtin.expressions import KeywordArgument
from liquid.builtin.expressions import Path
from liquid.builtin.expressions import parse_identifier
from liquid.builtin.expressions import parse_string_or_path
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
        alias: Optional[str] = None,
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
        template = context.get_template_with_context(str(name), tag=self.tag)
        namespace: dict[str, object] = {
            arg.name: arg.value.evaluate(context) for arg in self.args
        }

        with context.extend(namespace, template=template):
            # Bind a variable to the included template.
            if self.var is not None:
                val = self.var
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

        template = await context.get_template_with_context_async(
            str(name), tag=self.tag
        )

        namespace: dict[str, object] = {
            arg.name: await arg.value.evaluate_async(context) for arg in self.args
        }

        with context.extend(namespace, template=template):
            if self.var is not None:
                val = self.var
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

    def children(self) -> list[ChildNode]:
        """Return this node's children."""
        block_scope: list[str] = [arg.name for arg in self.args]
        _children = [
            ChildNode(
                linenum=self.token.start_index,
                node=None,
                expression=self.name,
                block_scope=block_scope,
                load_mode="include",
                load_context={"tag": "include"},
            )
        ]
        if self.var:
            # TODO:
            pass
        for arg in self.args:
            _children.append(
                ChildNode(linenum=self.token.start_index, expression=arg.value)
            )
        return _children


BIND_TOKENS = frozenset((TOKEN_WITH, TOKEN_FOR))


class IncludeTag(Tag):
    """The built-in _include_ tag."""

    name = TAG_INCLUDE
    block = False
    node_class = IncludeNode

    def parse(self, stream: TokenStream) -> Node:
        """Read an IncludeNode from the given stream of tokens."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(eat=False)

        # Need a string or identifier that resolves to a string. This is the name
        # of the template to be included.
        name = parse_string_or_path(self.env, tokens)
        var: Optional[Path] = None
        alias: Optional[str] = None

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
                alias = str(parse_identifier(self.env, tokens))

        # Zero or more keyword arguments
        args = KeywordArgument.parse(self.env, tokens)
        return self.node_class(token, name, var, alias, args)
