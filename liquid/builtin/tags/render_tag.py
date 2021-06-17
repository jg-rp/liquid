"""Parse tree node and tag definition for the built in "render" tag."""

import pathlib
import sys

from typing import Optional
from typing import Dict
from typing import Any
from typing import TextIO
from typing import Tuple

from liquid.ast import Node

from liquid.builtin.drops import IterableDrop
from liquid.builtin.tags.for_tag import ForLoop
from liquid.builtin.tags.include_tag import TAG_INCLUDE

from liquid.context import Context
from liquid.context import ReadOnlyChainMap

from liquid.exceptions import LiquidSyntaxError

from liquid.expression import Expression
from liquid.expression import Identifier

from liquid.lex import tokenize_include_expression

from liquid.parse import expect
from liquid.parse import parse_identifier
from liquid.parse import parse_expression
from liquid.parse import parse_unchained_identifier
from liquid.parse import parse_string_literal

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_STRING


TAG_RENDER = sys.intern("render")


class RenderNode(Node):
    """Parse tree node for the built-in "render" tag."""

    __slots__ = ("tok", "name", "var", "loop", "alias", "args")

    def __init__(
        self,
        tok: Token,
        name: Expression,
        var: Optional[Expression] = None,
        loop: bool = False,
        alias: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ):
        self.tok = tok
        self.name = name
        self.var = var
        self.loop = loop
        self.alias = alias
        self.args = args or {}

    def __str__(self) -> str:
        buf = [f"{self.name}"]

        if self.var:
            buf.append(f" with {self.var}")

        if self.alias:
            buf.append(f" as {self.alias}")

        if self.args:
            buf.append(", ")

        args = (f"{key}={val}" for key, val in self.args.items())
        buf.append(", ".join(args))

        return f"render({''.join(buf)})"

    def __repr__(self) -> str:
        return f"RenderNode(tok={self.tok!r}, name={self.name})"  # pragma: no cover

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        path = self.name.evaluate(context)
        assert isinstance(path, str)

        # XXX: This `render_folder` and forced ".liquid" suffix is to simulate a Shopify
        # theme structure. If it does actually belong in Python Liquid, it needs to be
        # documented.

        # TODO: Store this kind of thing on the context object but not the
        # globals/locals namespace.
        render_folder = context.get("render_folder", default=None)

        if render_folder:
            # FIXME: Don't assume ".liquid"
            path = str(pathlib.Path(str(render_folder), path).with_suffix(".liquid"))
        template = context.get_template(path)

        # Evaluate keyword arguments once. Unlike 'include', 'render' can not
        # mutate variables in the outer scope, so there's no need to re-evaluate
        # arguments for each loop (if any).
        args = {k: v.evaluate(context) for k, v in self.args.items()}

        # We're using a chain map here in case we need to push a forloop drop into
        # it. As drops are read only, the built-in collections.ChainMap will not do.
        namespace = ReadOnlyChainMap(args)

        # New context with globals and filters from the parent, plus the read only
        # namespace containing render arguments and bound variable.
        ctx = context.copy(namespace, disabled_tags=[TAG_INCLUDE])

        # Optionally bind a variable to the render namespace.
        if self.var is not None:
            val = self.var.evaluate(context)
            key = self.alias or template.name.split(".")[0]

            # If the variable is array-like, render the template once for each item.
            # `self.loop` being True indicates the render expression used "for" not
            # "with". This distinction is not made when using the 'include' tag.
            if self.loop and isinstance(val, (tuple, list, IterableDrop)):
                forloop = ForLoop(
                    name=key,
                    it=iter(val),
                    length=len(val),
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

        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        """An awaitable version of `render_to_output` that loads templates
        asynchronously."""
        path = await self.name.evaluate_async(context)
        assert isinstance(path, str)

        # XXX: This `render_folder` and forced ".liquid" suffix is to simulate a Shopify
        # theme structure. If it does actually belong in Python Liquid, it needs to be
        # documented.

        # TODO: Store this kind of thing on the context object but not the
        # globals/locals namespace.
        render_folder = context.get("render_folder", default=None)

        if render_folder:
            # FIXME: Don't assume ".liquid"
            path = str(pathlib.Path(str(render_folder), path).with_suffix(".liquid"))
        template = await context.get_template_async(path)

        # Evaluate keyword arguments once. Unlike 'include', 'render' can not
        # mutate variables in the outer scope, so there's no need to re-evaluate
        # arguments for each loop (if any).
        args = {k: await v.evaluate_async(context) for k, v in self.args.items()}

        # We're using a chain map here in case we need to push a forloop drop into
        # it. As drops are read only, the built-in collections.ChainMap will not do.
        namespace = ReadOnlyChainMap(args)

        # New context with globals and filters from the parent, plus the read only
        # namespace containing render arguments and bound variable.
        ctx = context.copy(namespace, disabled_tags=[TAG_INCLUDE])

        # Optionally bind a variable to the render namespace.
        if self.var is not None:
            val = await self.var.evaluate_async(context)
            key = self.alias or template.name.split(".")[0]

            # If the variable is array-like, render the template once for each item.
            # `self.loop` being True indicates the render expression used "for" not
            # "with". This distinction is not made when using the 'include' tag.
            if self.loop and isinstance(val, (tuple, list, IterableDrop)):
                forloop = ForLoop(
                    name=key,
                    it=iter(val),
                    length=len(val),
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

        return None


class RenderTag(Tag):
    """The built-in "render" tag."""

    name = TAG_RENDER
    block = False

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_RENDER)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_include_expression(stream.current.value))

        # Need a string. 'render' does not accept identifiers that resolve to a string.
        # This is the name of the template to be included.
        expect(expr_stream, TOKEN_STRING)
        name = parse_string_literal(expr_stream)
        expr_stream.next_token()

        alias: Optional[str] = None
        identifier: Optional[Identifier] = None
        loop: bool = False

        # Optionally bind a variable to the included template context
        if expr_stream.current.type in (TOKEN_WITH, TOKEN_FOR):
            loop = expr_stream.current.type == TOKEN_FOR
            expr_stream.next_token()  # Eat 'with' or 'for'
            expect(expr_stream, TOKEN_IDENTIFIER)
            identifier = parse_identifier(expr_stream)
            expr_stream.next_token()

            # The bound variable will take the name of the template by default,
            # or an alias if an identifier follows the "as" keyword.
            if expr_stream.current.type == TOKEN_AS:
                expr_stream.next_token()  # Eat 'as'
                expect(expr_stream, TOKEN_IDENTIFIER)
                alias = str(parse_unchained_identifier(expr_stream))
                expr_stream.next_token()

        # Zero or more keyword arguments
        args = {}

        # The first keyword argument might follow immediately or after a comma.
        if expr_stream.current.type == TOKEN_IDENTIFIER:
            key, val = parse_argument(expr_stream)
            args[key] = val

        while expr_stream.current.type != TOKEN_EOF:
            if expr_stream.current.type == TOKEN_COMMA:
                expr_stream.next_token()  # Eat comma
                key, val = parse_argument(expr_stream)
                args[key] = val
            else:
                typ = expr_stream.current.type
                raise LiquidSyntaxError(
                    f"expected a comma separated list of arguments, found {typ}",
                    linenum=tok.linenum,
                )

        return RenderNode(
            tok,
            name=name,
            var=identifier,
            loop=loop,
            alias=alias,
            args=args,
        )


def parse_argument(stream: TokenStream) -> Tuple[str, Expression]:
    """Return the next key/value pair from the stream where key and value
    are separated by a colon."""
    key = str(parse_unchained_identifier(stream))
    stream.next_token()

    expect(stream, TOKEN_COLON)
    stream.next_token()  # Eat colon

    val = parse_expression(stream)
    stream.next_token()

    return key, val
