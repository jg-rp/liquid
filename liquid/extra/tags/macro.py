"""Node and tag definitions for `macro` and `call`."""
from __future__ import annotations

import itertools
import sys

from typing import Optional
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

from liquid.expressions import parse_call_arguments
from liquid.expressions import parse_macro_arguments
from liquid.expressions.arguments.parse import Argument

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.builtin.tags.include_tag import TAG_INCLUDE
from liquid.extra.tags.extends import TAG_BLOCK

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF


if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment


TAG_MACRO = sys.intern("macro")
TAG_ENDMACRO = sys.intern("endmacro")
TAG_CALL = sys.intern("call")


class Macro(NamedTuple):
    """A macro block and its arguments."""

    args: List[Argument]
    block: BlockNode


class BoundArgs(NamedTuple):
    """Expressions bound to `call` ready to be evaluated."""

    args: Dict[str, Expression]
    excess_args: List[Expression]
    excess_kwargs: Dict[str, Expression]


class MacroNode(Node):
    """Parse tree node representing a macro."""

    __slots__ = ("tok", "name", "args", "block")

    def __init__(
        self,
        tok: Token,
        name: str,
        args: List[Argument],
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
        _children = [
            ChildNode(
                linenum=self.tok.linenum,
                node=self.block,
                block_scope=[key for key, _ in self.args],
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
        kwargs: List[Argument],
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

    def _bind_args(self, macro: Macro) -> BoundArgs:
        args = dict(macro.args)
        macro_names = [key for key, _ in macro.args]
        macro_set = set(macro_names)

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
            if name in macro_set:
                args[name] = expr
            else:
                excess_kwargs[name] = expr

        return BoundArgs(args, excess_args, excess_kwargs)

    def _make_context(self, context: Context, macro: Macro) -> Context:
        args, excess_args, excess_kwargs = self._bind_args(macro)

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

        return context.copy(
            ReadOnlyChainMap(bound_args, excess),
            disabled_tags=[TAG_INCLUDE, TAG_BLOCK],
            carry_loop_iterations=True,
        )

    async def _make_context_async(self, context: Context, macro: Macro) -> Context:
        args, excess_args, excess_kwargs = self._bind_args(macro)

        excess: Dict[str, object] = {
            "kwargs": {
                name: await expr.evaluate_async(context)
                for name, expr in excess_kwargs.items()
            },
            "args": [await expr.evaluate_async(context) for expr in excess_args],
        }

        # NOTE: default arguments are bound late.
        bound_args: Dict[str, object] = {}
        for name, expr in args.items():
            if expr == NIL:
                bound_args[name] = context.env.undefined(name)
            else:
                assert isinstance(expr, Expression)
                assert isinstance(name, str)
                bound_args[name] = await expr.evaluate_async(context)

        return context.copy(
            ReadOnlyChainMap(bound_args, excess),
            disabled_tags=[TAG_INCLUDE, TAG_BLOCK],
            carry_loop_iterations=True,
        )

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

        ctx = await self._make_context_async(context, macro)
        await macro.block.render_async(ctx, buffer)

        return True

    def children(self) -> List[ChildNode]:
        return [
            *[
                ChildNode(linenum=self.tok.linenum, expression=expr)
                for expr in self.args
            ],
            *[
                ChildNode(linenum=self.tok.linenum, expression=val)
                for _, val in self.kwargs
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

        # Parse the expression
        expect(stream, TOKEN_EXPRESSION)
        name, args = parse_macro_arguments(stream.current.value, linenum=tok.linenum)
        stream.next_token()

        # Parse the block
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
        name, _args = parse_call_arguments(stream.current.value, linenum=tok.linenum)

        # Args can be positional (no default), or keyword (with default).
        args: List[Expression] = []
        kwargs: List[Argument] = []

        for key, val in _args:
            if key is None:
                args.append(val)
            else:
                kwargs.append((key, val))

        return CallNode(tok=tok, name=name, args=args, kwargs=kwargs)
