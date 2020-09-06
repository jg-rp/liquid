"""Parse tree node and tag definition for the built in "render" tag."""

import sys
from typing import Optional, Dict, Any, Callable, TextIO

from liquid import ast
from liquid.tag import Tag
from liquid.token import (
    Token,
    TOKEN_TAG_NAME,
    TOKEN_EXPRESSION,
    TOKEN_IDENTIFIER,
    TOKEN_WITH,
    TOKEN_FOR,
    TOKEN_AS,
    TOKEN_COMMA,
    TOKEN_COLON,
    TOKEN_EOF,
    TOKEN_STRING,
)
from liquid.lex import TokenStream, get_expression_lexer
from liquid.parse import (
    expect,
    parse_identifier,
    parse_expression,
    parse_unchained_identifier,
    parse_string_literal,
)
from liquid.expression import Expression
from liquid.context import Context, ReadOnlyChainMap
from liquid.exceptions import LiquidSyntaxError
from liquid.builtin.drops import IterableDrop
from liquid.builtin.tags.for_tag import ForLoopDrop
from liquid.builtin.tags.include_tag import TAG_INCLUDE

TAG_RENDER = sys.intern("render")


class RenderNode(ast.Node):
    """Parse tree node for "render" tags."""

    __slots__ = ("tok", "name", "get_template", "var", "loop", "alias", "args")

    def __init__(
        self,
        tok: Token,
        name: Expression,
        get_template: Callable[[str, Optional[Dict[str, Any]]], Any],
        var: Optional[Expression] = None,
        loop: bool = False,
        alias: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ):
        self.tok = tok
        self.name = name
        self.get_template = get_template
        self.var = var
        self.loop = loop
        self.alias = alias
        self.args = args

    def __str__(self):
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

    def __repr__(self):
        return f"RenderNode(tok={self.tok!r}, name={self.name})"

    def render_to_output(self, context: Context, buffer: TextIO):
        template_name = self.name.evaluate(context)
        template = self.get_template(template_name, None)

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
                forloop = ForLoopDrop(key, len(val))
                namespace.push(forloop)
                for itm in val:
                    forloop.step(itm)
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


class RenderTag(Tag):

    name = TAG_RENDER

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> ast.Node:
        expect(stream, TOKEN_TAG_NAME, value=TAG_RENDER)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = get_expression_lexer(self.env).tokenize(stream.current.value)

        # Need a string. 'render' does not accept identifiers that resolve to a string.
        # This is the name of the template to be included.
        expect(expr_stream, TOKEN_STRING)
        name = parse_string_literal(expr_stream)
        expr_stream.next_token()

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
            else:
                alias = None
        else:
            identifier = None
            loop = False
            alias = None

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
            get_template=self.env.get_template,
            var=identifier,
            loop=loop,
            alias=alias,
            args=args,
        )


def parse_argument(stream: TokenStream):
    key = str(parse_unchained_identifier(stream))
    stream.next_token()

    expect(stream, TOKEN_COLON)
    stream.next_token()  # Eat colon

    val = parse_expression(stream)
    stream.next_token()

    return key, val
