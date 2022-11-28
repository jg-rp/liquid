"""Node and tag definitions for `macro` and `call`."""
from __future__ import annotations

import functools
import itertools
import sys

from typing import Optional
from typing import Tuple
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import TextIO
from typing import Union
from typing import TYPE_CHECKING

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import is_undefined
from liquid.context import Undefined
from liquid.context import Context
from liquid.context import ReadOnlyChainMap

from liquid.expression import Expression
from liquid.expression import NIL
from liquid.exceptions import LiquidSyntaxError

from liquid.lex import STRING_PATTERN
from liquid.lex import _tokenize
from liquid.lex import _compile_rules

from liquid.parse import expect
from liquid.parse import get_parser
from liquid.parse import parse_expression
from liquid.parse import parse_string_literal
from liquid.parse import parse_unchained_identifier

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.builtin.tags.include_tag import TAG_INCLUDE

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_NEGATIVE
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment


TAG_MACRO = sys.intern("macro")
TAG_ENDMACRO = sys.intern("endmacro")
TAG_CALL = sys.intern("call")


class CallKeywordArg(NamedTuple):
    """A named argument as used in a `call` expression."""

    name: str
    expr: Expression


class MacroArg(NamedTuple):
    """A macro argument with an optional default value."""

    name: str
    default: Expression = NIL


class Macro(NamedTuple):
    """A macro block and its arguments."""

    args: List[MacroArg]
    block: BlockNode


macro_expression_rules = (
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-?]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_COMMA, r","),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)

macro_expression_keywords = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_EMPTY,
        TOKEN_BLANK,
    ]
)

tokenize_macro_expression = functools.partial(
    _tokenize,
    rules=_compile_rules(macro_expression_rules),
    keywords=macro_expression_keywords,
)


class MacroNode(Node):
    """Parse tree node representing a macro."""

    __slots__ = ("tok", "name", "args", "block")

    def __init__(
        self,
        tok: Token,
        name: str,
        args: List[MacroArg],
        block: BlockNode,
    ):
        self.tok = tok
        self.name = name
        self.args = args
        self.block = block

    def __str__(self) -> str:  # pragma: no cover
        args: List[str] = []
        for arg, default in self.args:
            if default is not NIL:
                args.append(f"{arg}={default}")
            else:
                args.append(arg)
        return f"def {self.name}({', '.join(args)}) {{ {self.block} }}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"MacroNode(tok={self.tok}, name={self.name}, block='{self.block}')"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        if "macros" not in context.tag_namespace:
            context.tag_namespace["macros"] = {}

        context.tag_namespace["macros"][self.name] = Macro(self.args, self.block)
        return False

    def children(self) -> List[ChildNode]:
        # We don't currently have a good, generic way to model the `macro`/`call`
        # relationship for static analysis. When a macro is called, arguments without
        # defaults are expected to be `Undefined`.
        _children = [
            ChildNode(
                linenum=self.tok.linenum,
                node=self.block,
                block_scope=[arg.name for arg in self.args],
            )
        ]
        for _, expr in self.args:
            if expr != NIL:
                _children.append(ChildNode(linenum=self.tok.linenum, expression=expr))
        return _children


class CallNode(Node):
    """Parse tree node representing a call to a macro."""

    __slots__ = ("tok", "name", "args", "kwargs")

    def __init__(
        self,
        tok: Token,
        name: str,
        args: List[Expression],
        kwargs: List[CallKeywordArg],
    ):
        self.tok = tok
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:  # pragma: no cover
        args = [str(expr) for expr in self.args]
        for name, expr in self.kwargs:
            args.append(f"{name}: {expr}")
        return f"{self.name}({', '.join(args)})"

    def __repr__(self) -> str:  # pragma: no cover
        return f"CallNode(tok={self.tok}, name={self.name})"

    def _make_context(self, context: Context, macro: Macro) -> Context:
        args = dict(macro.args)
        macro_names = [arg.name for arg in macro.args]

        # Bind positional arguments to names. If there are more positional arguments
        # than names defined in the macro, they'll be stored in `excess_args`.
        excess_args: List[Expression] = []
        for name, expr in itertools.zip_longest(macro_names, self.args, fillvalue=NIL):
            if name == NIL:
                excess_args.append(expr)
                continue
            if expr == NIL:
                break
            assert isinstance(name, str)
            args[name] = expr

        # NOTE: This has the potential to override a positional argument with a keyword.
        # We also silently take the last keyword argument if a keyword is given more
        # than once.

        # Update default and/or missing arguments with keyword arguments.
        excess_kwargs: Dict[str, Expression] = {}
        for name, expr in self.kwargs:
            assert isinstance(name, str)
            if name in macro_names:
                args[name] = expr
            else:
                excess_kwargs[name] = expr

        excess: Dict[str, object] = {
            "kwargs": {
                name: expr.evaluate(context) for name, expr in excess_kwargs.items()
            },
            "args": [expr.evaluate(context) for expr in excess_args],
        }

        # NOTE: default arguments are bound late.
        bound_args: Dict[str, object] = {}
        for name, expr in args.items():
            if expr == NIL:
                bound_args[name] = context.env.undefined(name)
            else:
                assert isinstance(expr, Expression)
                assert isinstance(name, str)
                bound_args[name] = expr.evaluate(context)

        namespace = ReadOnlyChainMap(bound_args, excess)
        return context.copy(namespace, disabled_tags=[TAG_INCLUDE])

    def _get_macro(self, context: Context) -> Union[Macro, Undefined]:
        macro = context.tag_namespace.get("macros", {}).get(
            self.name, context.env.undefined(self.name)
        )
        assert isinstance(macro, (Macro, Undefined))
        return macro

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        macro = self._get_macro(context)

        if is_undefined(macro):
            buffer.write(str(macro))
            return False

        assert isinstance(macro, Macro)

        ctx = self._make_context(context, macro)
        macro.block.render(ctx, buffer)

        return True

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        macro = self._get_macro(context)

        if is_undefined(macro):
            buffer.write(str(macro))
            return False

        assert isinstance(macro, Macro)

        ctx = self._make_context(context, macro)
        await macro.block.render_async(ctx, buffer)

        return True

    def children(self) -> List[ChildNode]:
        return [
            *[
                ChildNode(linenum=self.tok.linenum, expression=expr)
                for expr in self.args
            ],
            *[
                ChildNode(linenum=self.tok.linenum, expression=arg.expr)
                for arg in self.kwargs
            ],
        ]


class MacroTag(Tag):
    """Macro tag definition."""

    name = TAG_MACRO
    end = TAG_ENDMACRO

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_MACRO)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_macro_expression(stream.current.value))

        # Name of the macro. Must be a string literal
        expect(expr_stream, TOKEN_STRING)
        name = parse_string_literal(expr_stream).value
        expr_stream.next_token()

        # Args can be positional (no default), or keyword (with default).
        args = []

        # The argument list might not start with a comma.
        if expr_stream.current.type == TOKEN_IDENTIFIER:
            args.append(parse_macro_argument(expr_stream))

        while expr_stream.current.type != TOKEN_EOF:
            if expr_stream.current.type == TOKEN_COMMA:
                expr_stream.next_token()  # Eat comma
                args.append(parse_macro_argument(expr_stream))
            else:
                typ = expr_stream.current.type
                raise LiquidSyntaxError(
                    f"expected a comma separated list of arguments, found {typ}",
                    linenum=tok.linenum,
                )

        stream.next_token()
        block = self.parser.parse_block(stream, (TAG_ENDMACRO, TOKEN_EOF))
        expect(stream, TOKEN_TAG, value=TAG_ENDMACRO)

        return MacroNode(tok=tok, name=name, args=args, block=block)


class CallTag(Tag):
    """Call tag definition."""

    name = TAG_CALL
    block = False

    def parse(self, stream: TokenStream) -> CallNode:
        expect(stream, TOKEN_TAG, value=TAG_CALL)
        tok = stream.current

        stream.next_token()
        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_macro_expression(stream.current.value))

        # Name of the macro. Must be a string literal
        expect(expr_stream, TOKEN_STRING)
        name = parse_string_literal(expr_stream).value
        expr_stream.next_token()

        # Args can be positional (no default), or keyword (with default).
        args = []
        kwargs = []

        if expr_stream.current.type not in (TOKEN_COMMA, TOKEN_EOF):
            arg_name, expr = parse_call_argument(expr_stream)
            if arg_name is None:
                args.append(expr)
            else:
                kwargs.append(CallKeywordArg(arg_name, expr))

        while expr_stream.current.type != TOKEN_EOF:
            if expr_stream.current.type == TOKEN_COMMA:
                expr_stream.next_token()  # Eat comma

                arg_name, expr = parse_call_argument(expr_stream)
                if arg_name is None:
                    args.append(expr)
                else:
                    kwargs.append(CallKeywordArg(arg_name, expr))
            else:
                typ = expr_stream.current.type
                raise LiquidSyntaxError(
                    f"expected a comma separated list of arguments, found {typ}",
                    linenum=tok.linenum,
                )

        return CallNode(tok=tok, name=name, args=args, kwargs=kwargs)


def parse_macro_argument(stream: TokenStream) -> MacroArg:
    """Return the next argument from the given token stream."""
    name = str(parse_unchained_identifier(stream))
    stream.next_token()

    if stream.current.type == TOKEN_COLON:
        # A keyword argument
        stream.next_token()  # Eat colon
        default = parse_expression(stream)
        stream.next_token()
    else:
        # A positional argument
        default = NIL

    return MacroArg(name, default)


def parse_call_argument(stream: TokenStream) -> Tuple[Optional[str], Expression]:
    """Return the next argument from the given token stream."""
    if stream.peek.type == TOKEN_COLON:
        # A keyword argument
        name: Optional[str] = str(parse_unchained_identifier(stream))
        stream.next_token()
        stream.next_token()  # Eat colon
    else:
        # A positional argument
        name = None

    expr = parse_expression(stream)
    stream.next_token()

    return name, expr
