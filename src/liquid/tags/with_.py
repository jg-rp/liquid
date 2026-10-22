from __future__ import annotations

from typing import TYPE_CHECKING

from .._io import StringBuffer
from .._markup import is_blank_block, render_block, render_block_async
from ..tokens import TOKEN_COMMA, TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from ..expressions import KeywordArgument, Name
    from ..tokens import Token


class WithTag:
    tag = "with"

    __slots__ = ("args", "blank", "block", "token")

    def __init__(self, token: Token, args: list[KeywordArgument], block: Block) -> None:
        self.token = token
        self.args = args
        self.block = block
        self.blank = is_blank_block(block)

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        if parser.kind() == TOKEN_COMMA:
            # Leading commas are OK.
            parser.next()

        args = parser.parse_keyword_arguments(require_commas=True)

        if parser.kind() == TOKEN_COMMA:
            # Trailing commas are OK.
            parser.next()

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        block = parser.parse_block(("endwith",))
        parser.eat_empty_tag("endwith")
        return WithTag(token, args, block)

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        scope: dict[str, object] = {}

        with context.extend(scope):
            # Later args have access to earlier args.
            for arg in self.args:
                scope[arg.name.value] = arg.expr.evaluate(context)

            render_block(self.block, context, buffer)

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        scope: dict[str, object] = {}

        with context.extend(scope):
            # Later args have access to earlier args.
            for arg in self.args:
                scope[arg.name.value] = await arg.expr.evaluate_async(context)

            await render_block_async(self.block, context, buffer)

    def children(self) -> list[Markup]:
        return [node for node in self.block if not isinstance(node, str)]

    def expressions(self) -> list[Expression]:
        return [arg.expr for arg in self.args]

    def block_scope(self) -> list[Name]:
        return [arg.name for arg in self.args]

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        return []

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        return []
