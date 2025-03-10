"""The built-in `macro` and `call` tags."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import TextIO
from typing import Union

from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import KeywordArgument
from liquid.builtin.expressions import Parameter
from liquid.builtin.expressions import parse_arguments
from liquid.builtin.expressions import parse_name
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_TAG
from liquid.undefined import Undefined
from liquid.undefined import is_undefined

if TYPE_CHECKING:
    from liquid import Expression
    from liquid import RenderContext
    from liquid import Token
    from liquid import TokenStream
    from liquid.builtin.expressions import PositionalArgument


@dataclass
class Macro:
    """A macro's arguments and associated block."""

    args: dict[str, Parameter]
    block: BlockNode


@dataclass
class BoundArgs:
    """Expressions bound to the evaluation of a `call` tag."""

    args: dict[str, Optional[Expression]]
    excess_args: list[Expression]
    excess_kwargs: dict[str, Expression]


class MacroNode(Node):
    """The built-in _macro_ tag."""

    __slots__ = ("name", "args", "block")

    def __init__(
        self,
        token: Token,
        name: str,
        args: dict[str, Parameter],
        block: BlockNode,
    ):
        super().__init__(token)
        self.name = name
        self.args = args
        self.block = block
        self.blank = True

    def __str__(self) -> str:
        args = " " + ", ".join(str(p) for p in self.args.values()) if self.args else ""
        return f"{{% macro {self.name}{args} %}}{self.block}{{% endmacro %}}"

    def render_to_output(self, context: RenderContext, _buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        # Macro tags don't render or evaluate anything, just store their arguments list
        # and block on the render context so it can be called later by a `call` tag.
        context.tag_namespace["macros"][self.name] = Macro(
            args=self.args, block=self.block
        )
        return 0

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield from (arg.value for arg in self.args.values() if arg.value)

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.block

    def block_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the node's block scope."""
        yield from (Identifier(p.name, token=p.token) for p in self.args.values())


class MacroTag(Tag):
    """The built-in _macro_ tag."""

    name = "macro"
    node_class = MacroNode

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token)
        name = parse_name(self.env, tokens)
        args = Parameter.parse(self.env, tokens)
        block = get_parser(self.env).parse_block(stream, ("endmacro",))
        stream.expect(TOKEN_TAG, "endmacro")
        return self.node_class(token, name, args, block)


class CallNode(Node):
    """The built-in _call_ tag."""

    __slots__ = ("name", "args", "kwargs")
    disabled_tags = ["include", "block"]

    def __init__(
        self,
        token: Token,
        name: str,
        args: list[PositionalArgument],
        kwargs: list[KeywordArgument],
    ) -> None:
        super().__init__(token)
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.blank = False

    def __str__(self) -> str:
        args = " " + ", ".join(
            [*(str(arg) for arg in self.args), *(str(arg) for arg in self.kwargs)]
        )
        return f"{{% call {self.name}{args} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        macro: Union[Macro, Undefined] = context.tag_namespace["macros"].get(
            self.name, context.env.undefined(self.name, token=self.token)
        )

        if isinstance(macro, Undefined):
            return buffer.write(str(macro))

        args = self.macro_args(macro)

        namespace: dict[str, object] = {
            "args": [expr.evaluate(context) for expr in args.excess_args],
            "kwargs": {
                name: expr.evaluate(context)
                for name, expr in args.excess_kwargs.items()
            },
        }

        for name, expr in args.args.items():
            if expr is None:
                namespace[name] = context.env.undefined(name, token=self.token)
            else:
                namespace[name] = expr.evaluate(context)

        macro_context = context.copy(
            namespace=namespace,
            disabled_tags=self.disabled_tags,
            carry_loop_iterations=True,
        )

        return macro.block.render(macro_context, buffer)

    async def render_to_output_async(
        self,
        context: RenderContext,
        buffer: TextIO,
    ) -> int:
        """Render the node to the output buffer."""
        macro: Union[Macro, Undefined] = context.tag_namespace["macros"].get(
            self.name, context.env.undefined(self.name, token=self.token)
        )

        if is_undefined(macro):
            return buffer.write(str(macro))

        assert isinstance(macro, Macro)
        args = self.macro_args(macro)

        namespace: dict[str, object] = {
            "args": [await expr.evaluate_async(context) for expr in args.excess_args],
            "kwargs": {
                name: await expr.evaluate_async(context)
                for name, expr in args.excess_kwargs.items()
            },
        }

        for name, expr in args.args.items():
            if expr is None:
                namespace[name] = context.env.undefined(name, token=self.token)
            else:
                namespace[name] = await expr.evaluate_async(context)

        macro_context = context.copy(
            namespace=namespace,
            disabled_tags=self.disabled_tags,
            carry_loop_iterations=True,
        )

        return await macro.block.render_async(macro_context, buffer)

    def macro_args(self, macro: Macro) -> BoundArgs:
        """Bind this call's arguments to macro parameter names."""
        args: dict[str, Optional[Expression]] = {
            name: param.value for name, param in macro.args.items()
        }

        excess_args: list[Expression] = []
        excess_kwargs: dict[str, Expression] = {}

        # Bind positional arguments to names. If there are more positional arguments
        # than names defined in the macro, they'll be stored in `excess_args`.
        #
        # We're effectively pushing kwargs to the end if they appear before positional
        # arguments.
        for name, expr in itertools.zip_longest(macro.args, self.args, fillvalue=None):
            if name is None:
                assert expr is not None
                excess_args.append(expr.value)
                continue

            if expr is None:
                break

            args[name] = expr.value

        for arg in self.kwargs:
            if arg.name in macro.args:
                # This has the potential to override a positional argument.
                args[arg.name] = arg.value
            else:
                excess_kwargs[arg.name] = arg.value

        return BoundArgs(
            args=args, excess_args=excess_args, excess_kwargs=excess_kwargs
        )

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield from (arg.value for arg in self.args if arg.value)
        yield from (arg.value for arg in self.kwargs if arg.value)


class CallTag(Tag):
    """The built-in _call_ tag."""

    name = "call"
    node_class = CallNode
    block = False

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token, eat=False)
        name = parse_name(self.env, tokens)
        args, kwargs = parse_arguments(self.env, tokens)
        return self.node_class(token, name, args, kwargs)
