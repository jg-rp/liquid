from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, TextIO

from ..expressions import Variable
from ..tokens import TOKEN_COLON, TOKEN_COMMA, TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import Name
    from ..tokens import Token


class CycleTag:
    blank = False
    tag = "cycle"

    __slots__ = ("group", "items", "static_key", "token")

    def __init__(
        self, token: Token, group: Expression | None, items: list[Expression]
    ) -> None:
        self.token = token
        self.group = group
        self.items = items
        self.static_key = ""

        if group is not None:
            # This mimics Shopify/liquid by giving every Variable a unique ID.
            self.static_key = str(
                [f"{i}:{id(i)}" if isinstance(i, Variable) else i for i in items]
            )

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        group: Expression | None = None
        items: list[Expression] = []

        first = parser.parse_expression()

        if parser.kind() == TOKEN_COLON:
            group = first
            parser.next()
        else:
            items.append(first)

        if parser.kind() == TOKEN_COMMA:
            parser.next()

        items.extend(parser.parse_positional_arguments())
        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        return CycleTag(token, group, items)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        cycles = context.get_register("cycle", default=register_factory)
        key = self.static_key

        if self.group:
            key = context.env.to_str(
                self.group.evaluate(context),
                context,
                self.group.span,
            )

        index = cycles[key]
        expr = self.items[index]

        buffer.write(context.env.to_str(expr.evaluate(context), context, expr.span))

        index += 1
        if index >= len(self.items):
            index = 0

        cycles[key] = index

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        cycles = context.get_register("cycle", default=register_factory)
        key = self.static_key

        if self.group:
            key = context.env.to_str(
                await self.group.evaluate_async(context),
                context,
                self.group.span,
            )

        index = cycles[key]
        expr = self.items[index]

        buffer.write(
            context.env.to_str(await expr.evaluate_async(context), context, expr.span)
        )

        index += 1
        if index >= len(self.items):
            index = 0

        cycles[key] = index

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        return [self.group, *self.items] if self.group else self.items

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
