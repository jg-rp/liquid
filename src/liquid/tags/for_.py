from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from itertools import islice
from typing import TYPE_CHECKING, TextIO

from .._drop import is_iterable_drop
from .._markup import is_blank_block, render_block, render_block_async
from ..drops import ForLoop, Undefined
from ..exceptions import LiquidSyntaxError
from ..expressions import KeywordArgument, Name, Variable
from ..tokens import TOKEN_COMMA, TOKEN_IN, TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..tokens import Token


class ForTag:
    tag = "for"

    __slots__ = (
        "blank",
        "block",
        "default",
        "expression",
        "limit",
        "name",
        "offset",
        "reversed",
        "token",
    )

    def __init__(
        self,
        token: Token,
        name: Name,
        expression: Expression,
        block: Block,
        *,
        offset: Expression | None,
        limit: Expression | None,
        reversed: bool,
        default: Block | None,
    ) -> None:
        self.token = token
        self.name = name
        self.expression = expression
        self.block: Block = block
        self.offset = offset
        self.limit = limit
        self.reversed = reversed
        self.default: Block | None = default

        self.blank = is_blank_block(self.block) and (
            not default or is_blank_block(default)
        )

        if self.blank:
            self.block = [node for node in self.block if not isinstance(node, str)]
            if self.default:
                self.default = [
                    node for node in self.default if not isinstance(node, str)
                ]

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        ident = parser.parse_identifier()
        parser.eat(TOKEN_IN, message="missing 'in'")
        parser.expect_expression()
        expr = parser.parse_expression()

        if parser.kind() == TOKEN_COMMA:
            parser.next()

        reversed_, offset, limit = ForTag.unpack_args(
            parser, parser.parse_arguments(require_commas=False)
        )

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        block = parser.parse_block(("else", "endfor"))
        default: Block | None = None

        if parser.tag("else"):
            parser.eat_empty_tag("else")
            default = parser.parse_block(("else", "endfor"))

        parser.eat_empty_tag("endfor")

        return ForTag(
            token,
            ident,
            expr,
            block,
            offset=offset,
            limit=limit,
            reversed=reversed_,
            default=default,
        )

    @staticmethod
    def unpack_args(
        parser: Parser, args: list[Expression | KeywordArgument]
    ) -> tuple[bool, Expression | None, Expression | None]:
        reversed_: bool = False
        offset: Expression | None = None
        limit: Expression | None = None

        for arg in args:
            if isinstance(arg, KeywordArgument):
                if arg.name.value == "offset":
                    offset = arg.expr
                elif arg.name.value == "limit":
                    limit = arg.expr
                else:
                    raise LiquidSyntaxError(
                        f"unknown argument {arg.name.value!r}",
                        token=arg.name.token,
                        source=parser.source,
                        name=parser.template_name,
                    )

            elif (
                isinstance(arg, Variable)
                and isinstance(arg.root, Name)
                and arg.root.value == "reversed"
                and not arg.selectors
            ):
                reversed_ = True

            else:
                raise LiquidSyntaxError(
                    "unexpected argument",
                    token=arg.token,
                    source=parser.source,
                    name=parser.template_name,
                )

        return reversed_, offset, limit

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        target = self.expression.evaluate(context)

        offsets = context.get_register("loop_offset", default=register_factory)
        offset_key = f"{self.name.value}-{self.expression}"

        offset = self.offset.evaluate(context) if self.offset else None
        start: int = 0

        if isinstance(offset, Undefined) and offset.path == "continue":
            start = offsets[offset_key]
        elif offset is not None:
            start = context.env.to_int(offset, context, self.expression.span)

        limit = self.limit.evaluate(context) if self.limit else None
        end: int | None = None

        if limit is not None:
            end = start + context.env.to_int(limit, context, self.expression.span)

        it: Iterable[object]
        length: int

        if is_iterable_drop(target):
            it = target.__liquid_iter__(start, end, self.reversed)
            length = len(it)

        else:
            a = context.env.to_array(target, context, self.expression.span)
            start, end, _ = slice(start, end).indices(len(a))
            length = max(0, end - start)

            if self.reversed:
                it = reverse_slice(a, start, end or len(a))
            else:
                it = islice(a, start, end)

        if not length:
            if self.default:
                render_block(self.default, context, buffer)
            return

        name = self.name.value
        parent_loop = context.parent_loop()

        forloop = ForLoop(f"{name}-{self.expression}", length, parent_loop)
        namespace: dict[str, object] = {"forloop": forloop}

        with context.loop(namespace, forloop):
            for obj in it:
                namespace[name] = obj
                forloop.step()
                render_block(self.block, context, buffer)

                if context.interrupts:
                    interrupt = context.interrupts.pop()
                    if interrupt == "break":
                        break
                    elif interrupt == "continue":
                        continue
                    else:
                        context.interrupts.append(interrupt)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        target = await self.expression.evaluate_async(context)

        offsets = context.get_register("loop_offset", default=register_factory)
        offset_key = f"{self.name.value}-{self.expression}"

        offset = await self.offset.evaluate_async(context) if self.offset else None
        start: int = 0

        if isinstance(offset, Undefined) and offset.path == "continue":
            start = offsets[offset_key]
        elif offset is not None:
            start = context.env.to_int(offset, context, self.expression.span)

        limit = await self.limit.evaluate_async(context) if self.limit else None
        end: int | None = None

        if limit is not None:
            end = start + context.env.to_int(limit, context, self.expression.span)

        it: Iterable[object]
        length: int

        # TODO: __liquid_aiter__
        if is_iterable_drop(target):
            it = target.__liquid_iter__(start, end, self.reversed)
            length = len(it)

        else:
            a = context.env.to_array(target, context, self.expression.span)
            start, end, _ = slice(start, end).indices(len(a))
            length = max(0, end - start)

            if self.reversed:
                it = reverse_slice(a, start, end or len(a))
            else:
                it = islice(a, start, end)

        if not length:
            if self.default:
                await render_block_async(self.default, context, buffer)
            return

        name = self.name.value
        parent_loop = context.parent_loop()

        forloop = ForLoop(f"{name}-{self.expression}", length, parent_loop)
        namespace: dict[str, object] = {"forloop": forloop}

        with context.loop(namespace, forloop):
            for obj in it:
                namespace[name] = obj
                forloop.step()
                await render_block_async(self.block, context, buffer)

                if context.interrupts:
                    interrupt = context.interrupts.pop()
                    if interrupt == "break":
                        break
                    elif interrupt == "continue":
                        continue
                    else:
                        context.interrupts.append(interrupt)

    def children(self) -> list[Markup]:
        result: list[Markup] = [
            node for node in self.block if not isinstance(node, str)
        ]

        if self.default:
            for node in self.default:
                if not isinstance(node, str):
                    result.append(node)

        return result

    def expressions(self) -> list[Expression]:
        result = [self.expression]

        if self.offset:
            result.append(self.offset)

        if self.limit:
            result.append(self.limit)

        return result

    def block_scope(self) -> list[Name]:
        return [self.name]

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []


class BreakTag:
    blank = True
    tag = "break"

    __slots__ = ("token",)

    def __init__(self, token: Token) -> None:
        self.token = token

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return BreakTag(token)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        context.interrupts.append("break")

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        context.interrupts.append("break")

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return []

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []


class ContinueTag:
    blank = True
    tag = "continue"

    __slots__ = ("token",)

    def __init__(self, token: Token) -> None:
        self.token = token

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)
        return BreakTag(token)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        context.interrupts.append("continue")

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        context.interrupts.append("continue")

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return []

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []


def register_factory() -> defaultdict[str, int]:
    return defaultdict(int)


def reverse_slice[T](seq: Sequence[T], start: int, end: int) -> Iterable[T]:
    for i in range(end - 1, start - 1, -1):
        yield seq[i]
