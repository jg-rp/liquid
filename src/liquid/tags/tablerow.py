from __future__ import annotations

from collections.abc import Iterable
from itertools import islice
from typing import TYPE_CHECKING, Protocol, TextIO, TypeGuard

from .._markup import render_block, render_block_async
from ..drops import IterableDrop, TableRowLoop
from ..exceptions import LiquidSyntaxError
from ..expressions import Name
from ..tokens import TOKEN_COMMA, TOKEN_IN, TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..tokens import Token


class TableRowTag:
    blank = False
    tag = "tablerow"

    __slots__ = (
        "block",
        "cols",
        "expression",
        "limit",
        "name",
        "offset",
        "token",
    )

    def __init__(
        self,
        token: Token,
        name: Name,
        expression: Expression,
        block: Block,
        *,
        cols: Expression | None,
        offset: Expression | None,
        limit: Expression | None,
    ) -> None:
        self.token = token
        self.name = name
        self.expression = expression
        self.block: Block = block
        self.offset = offset
        self.limit = limit
        self.cols = cols

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        ident = parser.parse_identifier()
        parser.eat(TOKEN_IN, message="missing 'in'")
        parser.expect_expression()
        expr = parser.parse_expression()

        if parser.kind() == TOKEN_COMMA:
            parser.next()

        args = parser.parse_keyword_arguments(require_commas=False)

        cols: Expression | None = None
        offset: Expression | None = None
        limit: Expression | None = None

        for arg in args:
            if arg.name.value == "offset":
                offset = arg.expr
            elif arg.name.value == "limit":
                limit = arg.expr
            elif arg.name.value == "cols":
                cols = arg.expr
            elif arg.name.value == "range":
                pass
            else:
                raise LiquidSyntaxError(
                    f"unknown argument {arg.name.value!r}",
                    token=arg.name.token,
                    source=parser.source,
                    name=parser.template_name,
                )

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        block = parser.parse_block(("endtablerow",))
        parser.eat_empty_tag("endtablerow")

        return TableRowTag(
            token,
            ident,
            expr,
            block,
            cols=cols,
            offset=offset,
            limit=limit,
        )

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        start = _to_int(self.offset, context, 0, 0)
        limit = _to_int(self.limit, context, None, 0)
        end: int | None = None

        if limit is not None:
            end = start + limit

        it: Iterable[object]
        length: int

        target = self.expression.evaluate(context)

        if is_iterable_drop(target):
            it = target.__liquid_iter__(start, end, False)
            length = len(it)
        else:
            a = context.env.to_array(target, context, self.expression.span)
            start, end, _ = slice(start, end).indices(len(a))
            it = islice(a, start, end)
            length = max(0, end - start)

        if not length:
            # An empty iterable renders nothing.
            return

        cols = _to_int(self.cols, context, length, 0)
        tablerowloop = TableRowLoop(length, cols)

        name = self.name.value
        namespace: dict[str, object] = {"tablerowloop": tablerowloop}

        with context.loop(namespace, tablerowloop):
            buffer.write('<tr class="row1">\n')

            for item in it:
                namespace[name] = item
                buffer.write(f'<td class="col{tablerowloop["col"]}">')
                render_block(self.block, context, buffer)
                buffer.write("</td>")

                if context.interrupts.pop() == "break":
                    break

                if tablerowloop["col_last"] and not tablerowloop["last"]:
                    buffer.write(f'</tr>\n<tr class="row{tablerowloop["row"] + 1}">')

                tablerowloop.step()

            buffer.write("</tr>\n")

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        start = await _to_int_async(self.offset, context, 0, 0)
        limit = await _to_int_async(self.limit, context, None, 0)
        end: int | None = None

        if limit is not None:
            end = start + limit

        it: Iterable[object]
        length: int

        target = await self.expression.evaluate_async(context)

        if is_iterable_drop(target):
            it = target.__liquid_iter__(start, end, False)
            length = len(it)
        else:
            a = context.env.to_array(target, context, self.expression.span)
            start, end, _ = slice(start, end).indices(len(a))
            it = islice(a, start, end)
            length = max(0, end - start)

        if not length:
            # An empty iterable renders nothing.
            return

        cols = await _to_int_async(self.cols, context, length, 0)
        tablerowloop = TableRowLoop(length, cols)

        name = self.name.value
        namespace: dict[str, object] = {"tablerowloop": tablerowloop}

        with context.loop(namespace, tablerowloop):
            buffer.write('<tr class="row1">\n')

            for item in it:
                namespace[name] = item
                buffer.write(f'<td class="col{tablerowloop["col"]}">')
                await render_block_async(self.block, context, buffer)
                buffer.write("</td>")

                if context.interrupts.pop() == "break":
                    break

                if tablerowloop["col_last"] and not tablerowloop["last"]:
                    buffer.write(f'</tr>\n<tr class="row{tablerowloop["row"] + 1}">')

                tablerowloop.step()

            buffer.write("</tr>\n")

    def children(self) -> list[Markup]:
        result: list[Markup] = [
            node for node in self.block if not isinstance(node, str)
        ]

        return result

    def expressions(self) -> list[Expression]:
        result = [self.expression]

        if self.cols:
            result.append(self.cols)

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


class LiquidIterable(Protocol):
    def __liquid_iter__(
        self, start: int, end: int | None, reversed_: bool
    ) -> IterableDrop[int]: ...


def is_iterable_drop(obj: object) -> TypeGuard[LiquidIterable]:
    return hasattr(obj, "__liquid_iter__")


def _to_int[T](
    expression: Expression | None,
    context: RenderContext,
    default: T,
    null: T,
) -> int | T:
    if expression is None:
        return default

    value = expression.evaluate(context)

    if context.env.is_nil(value):
        return null

    return context.env.to_int(value, context, expression.span)


async def _to_int_async[T](
    expression: Expression | None,
    context: RenderContext,
    default: T,
    null: T,
) -> int | T:
    if expression is None:
        return default

    value = await expression.evaluate_async(context)

    if context.env.is_nil(value):
        return null

    return context.env.to_int(value, context, expression.span)
