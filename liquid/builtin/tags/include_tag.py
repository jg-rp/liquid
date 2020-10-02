"""Parse tree node and tag definition for the built in "include" tag."""

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
)
from liquid.lex import TokenStream, get_expression_lexer
from liquid.parse import (
    expect,
    parse_identifier,
    parse_expression,
    parse_string_or_identifier,
    parse_unchained_identifier,
)
from liquid.expression import Expression
from liquid.context import Context
from liquid.exceptions import LiquidSyntaxError
from liquid.builtin.drops import IterableDrop

TAG_INCLUDE = sys.intern("include")


class IncludeNode(ast.Node):
    """Parse tree node for "include" block tags."""

    __slots__ = ("tok", "name", "get_template", "var", "alias", "args")

    def __init__(
        self,
        tok: Token,
        name: Expression,
        get_template: Callable[[str, Optional[Dict[str, Any]]], Any],
        var: Optional[Expression] = None,
        alias: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ):
        self.tok = tok
        self.name = name
        self.get_template = get_template
        self.var = var
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

        return f"include({''.join(buf)})"

    def __repr__(self):
        return f"IncludeNode(tok={self.tok!r}, name={self.name})"

    def render_to_output(self, context: Context, buffer: TextIO):
        name = self.name.evaluate(context)
        template = self.get_template(name, None)

        namespace = {}

        # Add any keyword arguments to the new template context.
        for key, val in self.args.items():
            namespace[key] = val.evaluate(context)

        with context.extend(namespace):
            # Bind a variable to the included template.
            if self.var is not None:
                val = self.var.evaluate(context)
                key = self.alias or template.name.split(".")[0]

                # If the variable is array-like, render the template once for each item in
                # the array.
                #
                # The reference implementation does not seem to distinguish between "for"
                # and "with". Just checks for array-like-ness.
                if isinstance(val, (tuple, list, IterableDrop)):
                    # XXX: What if an included template with a bound array updates a
                    # keyword argument value? Do we need to update namespace arguments after
                    # each loop?
                    #
                    # The reference implementation seems to evaluate arguments once, before
                    # the loop.
                    for itm in val:
                        namespace[key] = itm
                        template.render_with_context(context, buffer, partial=True)
                else:
                    namespace[key] = val
                    template.render_with_context(context, buffer, partial=True)
            else:
                template.render_with_context(context, buffer, partial=True)


class IncludeTag(Tag):

    name = TAG_INCLUDE

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> ast.Node:
        """

        {% include 'product' with collection.products[0] as special, foo: 'bar', some: other %}
        {% include 'product' with collection.products[0], foo: 'bar', some: other %}
        {% include 'product', foo: 'bar', some: other %}
        """
        expect(stream, TOKEN_TAG_NAME, value=TAG_INCLUDE)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = get_expression_lexer(self.env).tokenize(stream.current.value)

        # Need a string or identifier that resolves to a string. This is the name
        # of the template to be included.
        name = parse_string_or_identifier(expr_stream, linenum=tok.linenum)
        expr_stream.next_token()

        # Optionally bind a variable to the included template context
        if expr_stream.current.type in (TOKEN_WITH, TOKEN_FOR):
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

        return IncludeNode(
            tok,
            name=name,
            get_template=self.env.get_template,
            var=identifier,
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
