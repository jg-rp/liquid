from __future__ import annotations

from dataclasses import dataclass
from itertools import zip_longest
from typing import TYPE_CHECKING, Any

from .._io import StringBuffer
from .._markup import (
    SCOPE_ISOLATED,
    Partial,
    render_block,
    render_block_async,
)
from ..expressions import KeywordArgument, Name, Parameter
from ..tokens import TOKEN_COMMA, TOKEN_TAG_END, span

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup
    from .._parser import Parser
    from ..tokens import Token


@dataclass
class Macro:
    params: list[Parameter]
    block: Block


class MacroTag:
    tag = "macro"
    blank = True

    __slots__ = ("block", "name", "params", "token")

    def __init__(
        self, token: Token, name: Name, params: list[Parameter], block: Block
    ) -> None:
        self.token = token
        self.name = name
        self.params = params
        self.block = block

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        name = parser.parse_name()

        if parser.kind() == TOKEN_COMMA:
            # Leading commas are OK.
            parser.next()

        args = parser.parse_parameters(require_commas=True)

        if parser.kind() == TOKEN_COMMA:
            # Trailing commas are OK.
            parser.next()

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        block = parser.parse_block(("endmacro",))
        parser.eat_empty_tag("endmacro")
        return MacroTag(token, name, args, block)

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        macros: dict[str, Macro] = context.get_register("macros", register_callback)
        macros[self.name.value] = Macro(self.params, self.block)

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        macros: dict[str, Macro] = context.get_register("macros", register_callback)
        macros[self.name.value] = Macro(self.params, self.block)

    def children(self) -> list[Markup]:
        # We're treating macro blocks as partial templates so as to hook into the
        # isolated scope behavior found in rendered partial templates.
        return []

    def expressions(self) -> list[Expression]:
        return [param.expr for param in self.params if param.expr]

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        # Pretend this is a partial template so we get an isolated scope.
        return [
            Partial(
                template=context.template,
                scope=SCOPE_ISOLATED,
                in_scope=[param.name for param in self.params],
                key=hash(self.name.value),
            )
        ]

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return self.partials(context)


class CallTag:
    tag = "call"
    blank = False

    __slots__ = ("args", "name", "token")

    def __init__(
        self, token: Token, name: Name, args: list[Expression | KeywordArgument]
    ) -> None:
        self.token = token
        self.name = name
        self.args = args

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        name = parser.parse_name()

        if parser.kind() == TOKEN_COMMA:
            # Leading commas are OK.
            parser.next()

        args = parser.parse_arguments(require_commas=True)

        if parser.kind() == TOKEN_COMMA:
            # Trailing commas are OK.
            parser.next()

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        return CallTag(token, name, args)

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        macros: dict[str, Macro] = context.get_register("macros", register_callback)
        macro = macros.get(self.name.value)

        if not macro:
            buffer.write(
                str(
                    context.env.undefined(
                        self.name.value,
                        self.name.span,
                        context.template.source,
                        context.template.name,
                    )
                )
            )
            return

        args, excess_args, excess_kwargs = self._args(macro)
        scope: dict[str, Any] = {"args": [], "kwargs": {}}

        for arg in excess_args:
            scope["args"].append(arg.evaluate(context))

        for k, v in excess_kwargs.items():
            scope["kwargs"][k] = v.evaluate(context)

        for name, expr in args.items():
            if expr:
                scope[name] = expr.evaluate(context)
            else:
                scope[name] = context.env.undefined(
                    name,
                    span=span(self.token, self.args[-1].span)
                    if self.args
                    else self.token,
                    source=context.template.source,
                    template_name=context.template.name,
                )

        ctx = context.copy(scope, disabled_tags=("include", "block"))
        return render_block(macro.block, ctx, buffer)

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        macros: dict[str, Macro] = context.get_register("macros", register_callback)
        macro = macros.get(self.name.value)

        if not macro:
            buffer.write(
                str(
                    context.env.undefined(
                        self.name.value,
                        self.name.span,
                        context.template.source,
                        context.template.name,
                    )
                )
            )
            return

        args, excess_args, excess_kwargs = self._args(macro)
        scope: dict[str, Any] = {"args": [], "kwargs": {}}

        for arg in excess_args:
            scope["args"].append(await arg.evaluate_async(context))

        for k, v in excess_kwargs.items():
            scope["kwargs"][k] = await v.evaluate_async(context)

        for name, expr in args.items():
            if expr:
                scope[name] = await expr.evaluate_async(context)
            else:
                scope[name] = context.env.undefined(
                    name,
                    span=span(self.token, self.args[-1].span)
                    if self.args
                    else self.token,
                    source=context.template.source,
                    template_name=context.template.name,
                )

        ctx = context.copy(scope, disabled_tags=("include", "block"))
        return await render_block_async(macro.block, ctx, buffer)

    def _args(
        self, macro: Macro
    ) -> tuple[dict[str, Expression | None], list[Expression], dict[str, Expression]]:
        args: dict[str, Expression | None] = {
            p.name.value: p.expr for p in macro.params
        }

        excess_args: list[Expression] = []
        excess_kwargs: dict[str, Expression] = {}

        positional_args = (
            arg for arg in self.args if not isinstance(arg, KeywordArgument)
        )

        for param, expr in zip_longest(macro.params, positional_args, fillvalue=None):
            if param is None:
                assert expr is not None
                excess_args.append(expr)
                continue

            if expr is None:
                break

            args[param.name.value] = expr

        for arg in self.args:
            if not isinstance(arg, KeywordArgument):
                continue

            if arg.name.value in args:
                # Potentially override a positional argument.
                args[arg.name.value] = arg.expr
            else:
                excess_kwargs[arg.name.value] = arg.expr

        return args, excess_args, excess_kwargs

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return [
            arg.expr if isinstance(arg, KeywordArgument) else arg for arg in self.args
        ]

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return self.partials(context)


def register_callback() -> dict[str, Macro]:
    return {}
