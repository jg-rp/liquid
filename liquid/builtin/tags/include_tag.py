"""Parse tree node and tag definition for the built in "include" tag."""
import sys

from typing import List
from typing import Optional
from typing import Dict
from typing import TextIO
from typing import Tuple

from liquid.ast import ChildNode
from liquid.ast import Node

from liquid.builtin.drops import IterableDrop
from liquid.context import Context

from liquid.expression import Expression, Literal
from liquid.expression import Identifier

from liquid.exceptions import LiquidSyntaxError
from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.parse import expect

from liquid.token import Token
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_EOF

from liquid.expressions import TokenStream as ExprTokenStream
from liquid.expressions.common import parse_string_or_identifier
from liquid.expressions.common import parse_unchained_identifier
from liquid.expressions.common import parse_identifier
from liquid.expressions.include.lex import tokenize
from liquid.expressions.filtered.parse import parse_obj


TAG_INCLUDE = sys.intern("include")


class IncludeNode(Node):
    """Parse tree node for the built-in "include" tag."""

    __slots__ = ("tok", "name", "var", "alias", "args")
    tag = TAG_INCLUDE

    def __init__(
        self,
        tok: Token,
        name: Expression,
        var: Optional[Identifier] = None,
        alias: Optional[str] = None,
        args: Optional[Dict[str, Expression]] = None,
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

        return f"{self.tag}({''.join(buf)})"

    def __repr__(self) -> str:
        return f"IncludeNode(tok={self.tok!r}, name={self.name})"  # pragma: no cover

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        name = self.name.evaluate(context)
        template = context.get_template_with_context(str(name), tag=self.tag)
        namespace: Dict[str, object] = {}

        # Add any keyword arguments to the new template context.
        for _key, _val in self.args.items():
            namespace[_key] = _val.evaluate(context)

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
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        """Same as ``render_to_output`` but uses async versions of get_template and
        render_with_context."""
        name = await self.name.evaluate_async(context)
        template = await context.get_template_with_context_async(
            str(name), tag=self.tag
        )
        namespace: Dict[str, object] = {}

        for _key, _val in self.args.items():
            namespace[_key] = await _val.evaluate_async(context)

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

    def children(self) -> List[ChildNode]:
        block_scope: List[str] = list(self.args.keys())
        _children = [
            ChildNode(
                linenum=self.tok.linenum,
                node=None,
                expression=self.name,
                block_scope=block_scope,
                load_mode="include",
                load_context={"tag": "include"},
            )
        ]
        if self.var:
            if self.alias:
                block_scope.append(self.alias)
            elif isinstance(self.name, Literal):
                block_scope.append(str(self.name.value).split(".", 1)[0])
            _children.append(
                ChildNode(
                    linenum=self.tok.linenum,
                    expression=self.var,
                )
            )
        for expr in self.args.values():
            _children.append(ChildNode(linenum=self.tok.linenum, expression=expr))
        return _children


BIND_TOKENS = frozenset((TOKEN_WITH, TOKEN_FOR))


class IncludeTag(Tag):
    """The built-in "include" tag."""

    name = TAG_INCLUDE
    block = False
    node_class = IncludeNode

    def parse(self, stream: TokenStream) -> Node:
        """Read an IncludeNode from the given stream of tokens."""
        tok = next(stream)
        expect(stream, TOKEN_EXPRESSION)
        expr_stream = ExprTokenStream(
            tokenize(
                stream.current.value,
                linenum=tok.linenum,
            )
        )

        # Need a string or identifier that resolves to a string. This is the name
        # of the template to be included.
        name = parse_string_or_identifier(expr_stream)
        next(expr_stream)

        identifier: Optional[Identifier] = None
        alias: Optional[str] = None

        # Optionally bind a variable to the included template context
        if expr_stream.current[1] in BIND_TOKENS:
            next(expr_stream)  # Eat 'with' or 'for'
            expr_stream.expect(TOKEN_IDENTIFIER)
            identifier = parse_identifier(expr_stream)
            next(expr_stream)

            # The bound variable will take the name of the template by default,
            # or an alias if an identifier follows the "as" keyword.
            if expr_stream.current[1] == TOKEN_AS:
                next(expr_stream)  # Eat 'as'
                expr_stream.expect(TOKEN_IDENTIFIER)
                alias = str(parse_unchained_identifier(expr_stream))
                next(expr_stream)

        # Zero or more keyword arguments
        args: Dict[str, Expression] = {}

        # The first keyword argument might follow immediately or after a comma.
        if expr_stream.current[1] == TOKEN_IDENTIFIER:
            key, val = _parse_argument(expr_stream)
            args[key] = val

        while expr_stream.current[1] != TOKEN_EOF:
            if expr_stream.current[1] == TOKEN_COMMA:
                next(expr_stream)  # Eat comma
                key, val = _parse_argument(expr_stream)
                args[key] = val
            else:
                typ = expr_stream.current[1]
                raise LiquidSyntaxError(
                    f"expected a comma separated list of arguments, found {typ}",
                    linenum=tok.linenum,
                )

        return self.node_class(tok, name=name, var=identifier, alias=alias, args=args)


def _parse_argument(stream: ExprTokenStream) -> Tuple[str, Expression]:
    key = str(parse_unchained_identifier(stream))
    stream.next_token()
    stream.expect(TOKEN_COLON)
    stream.next_token()  # Eat colon
    val = parse_obj(stream)
    stream.next_token()
    return key, val
