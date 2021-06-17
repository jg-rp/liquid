"""Parse tree node and tag definition for the built in "include" tag."""
import sys

from typing import Optional
from typing import Dict
from typing import Any
from typing import TextIO
from typing import Tuple

from liquid.ast import Node
from liquid.builtin.drops import IterableDrop
from liquid.context import Context

from liquid.expression import Expression
from liquid.expression import Identifier

from liquid.exceptions import LiquidSyntaxError
from liquid.lex import tokenize_include_expression
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import expect
from liquid.parse import parse_identifier
from liquid.parse import parse_expression
from liquid.parse import parse_string_or_identifier
from liquid.parse import parse_unchained_identifier

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


TAG_INCLUDE = sys.intern("include")


class IncludeNode(Node):
    """Parse tree node for the built-in "include" tag."""

    __slots__ = ("tok", "name", "var", "alias", "args")

    def __init__(
        self,
        tok: Token,
        name: Expression,
        var: Optional[Identifier] = None,
        alias: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ):
        self.tok = tok
        self.name = name
        self.var = var
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

        return f"include({''.join(buf)})"

    def __repr__(self) -> str:
        return f"IncludeNode(tok={self.tok!r}, name={self.name})"  # pragma: no cover

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        name = self.name.evaluate(context)
        template = context.get_template(str(name))

        namespace: Dict[str, object] = {}

        # Add any keyword arguments to the new template context.
        for key, val in self.args.items():
            namespace[key] = val.evaluate(context)

        with context.extend(namespace):
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
                    for itm in val:
                        namespace[key] = itm
                        template.render_with_context(context, buffer, partial=True)
                else:
                    namespace[key] = val
                    template.render_with_context(context, buffer, partial=True)
            else:
                template.render_with_context(context, buffer, partial=True)

        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        """Same as ``render_to_output`` but uses async versions of get_template and
        render_with_context."""
        name = await self.name.evaluate_async(context)
        template = await context.get_template_async(str(name))
        namespace: Dict[str, object] = {}

        for key, val in self.args.items():
            namespace[key] = await val.evaluate_async(context)

        with context.extend(namespace):
            if self.var is not None:
                val = await self.var.evaluate_async(context)
                key = self.alias or template.name.split(".")[0]

                if isinstance(val, (tuple, list, IterableDrop)):
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

        return None


class IncludeTag(Tag):
    """The built-in "include" tag."""

    name = TAG_INCLUDE
    block = False

    def parse(self, stream: TokenStream) -> IncludeNode:
        """Read an IncludeNode from the given stream of tokens."""
        expect(stream, TOKEN_TAG, value=self.name)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_include_expression(stream.current.value))

        # Need a string or identifier that resolves to a string. This is the name
        # of the template to be included.
        name = parse_string_or_identifier(expr_stream, linenum=tok.linenum)
        expr_stream.next_token()

        identifier: Optional[Identifier] = None
        alias: Optional[str] = None

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

        # Zero or more keyword arguments
        args = {}

        # The first keyword argument might follow immediately or after a comma.
        if expr_stream.current.type == TOKEN_IDENTIFIER:
            key, val = _parse_argument(expr_stream)
            args[key] = val

        while expr_stream.current.type != TOKEN_EOF:
            if expr_stream.current.type == TOKEN_COMMA:
                expr_stream.next_token()  # Eat comma
                key, val = _parse_argument(expr_stream)
                args[key] = val
            else:
                typ = expr_stream.current.type
                raise LiquidSyntaxError(
                    f"expected a comma separated list of arguments, found {typ}",
                    linenum=tok.linenum,
                )

        return IncludeNode(tok, name=name, var=identifier, alias=alias, args=args)


def _parse_argument(stream: TokenStream) -> Tuple[str, Expression]:
    key = str(parse_unchained_identifier(stream))
    stream.next_token()

    expect(stream, TOKEN_COLON)
    stream.next_token()  # Eat colon

    val = parse_expression(stream)
    stream.next_token()

    return key, val
