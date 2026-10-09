from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from .._markup import SCOPE_ISOLATED, Partial
from .._nothing import NOTHING
from ..drops import ForLoop
from ..exceptions import NoSuchTemplateError, TemplateNotFoundError
from ..expressions import Name, StringLiteral
from ..tokens import TOKEN_COMMA, TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup
    from .._parser import Parser
    from ..expressions import KeywordArgument
    from ..tokens import Token


class RenderTag:
    blank = False
    tag = "render"

    __slots__ = ("alias", "args", "loop", "name", "token", "variable")

    def __init__(
        self,
        token: Token,
        *,
        name: StringLiteral,
        loop: bool,
        variable: Expression | None,
        alias: Name | None,
        args: list[KeywordArgument],
    ) -> None:
        self.token = token
        self.name = name
        self.loop = loop
        self.variable = variable
        self.alias = alias
        self.args = args

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        name_expr = parser.parse_string_literal()

        loop = False
        variable: Expression | None = None
        alias: Name | None = None

        # `for`, `with` and `as` don't have their own tokens kinds.
        ident = parser.value()
        if ident in ("for", "with"):
            loop = ident == "for"
            parser.next()
            variable = parser.parse_expression()

        if parser.value() == "as":
            parser.next()
            alias = parser.parse_identifier()

        if parser.kind() == TOKEN_COMMA:
            parser.next()

        args = parser.parse_keyword_arguments(require_commas=False)

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        return RenderTag(
            token,
            name=name_expr,
            loop=loop,
            variable=variable,
            alias=alias,
            args=args,
        )

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        template_name = self.name.value

        try:
            template = context.env.get_template(
                template_name, context=context, tag="render"
            )
        except TemplateNotFoundError as err:
            # Promote TemplateNotFoundError to NoSuchTemplateError
            raise NoSuchTemplateError(
                str(err),
                token=self.name.span,
                source=context.template.source,
                name=context.template.name,
            )

        bind_key = self.alias.value if self.alias else template.name.split(".", 1)[0]
        bind_value: object

        if self.variable:
            bind_value = self.variable.evaluate(context)
        else:
            bind_value = context.resolve(template_name)
            if bind_value == NOTHING:
                bind_value = None

        scope = {arg.name.value: arg.expr.evaluate(context) for arg in self.args}

        ctx = context.copy(
            scope,
            disabled_tags=("include",),
            block_scope=False,
            template=template,
        )

        if self.loop and isinstance(bind_value, list):
            forloop = ForLoop(bind_key, len(bind_value), None)  # type: ignore
            scope["forloop"] = forloop
            for item in bind_value:  # type: ignore
                scope[bind_key] = item
                forloop.step()
                template.render_with_context(ctx, buffer)
        else:
            scope[bind_key] = bind_value
            template.render_with_context(ctx, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        template_name = self.name.value

        try:
            template = await context.env.get_template_async(
                template_name, context=context, tag="render"
            )
        except TemplateNotFoundError as err:
            # Promote TemplateNotFoundError to NoSuchTemplateError
            raise NoSuchTemplateError(
                str(err),
                token=self.name.span,
                source=context.template.source,
                name=context.template.name,
            )

        bind_key = self.alias.value if self.alias else template.name.split(".", 1)[0]
        bind_value: object

        if self.variable:
            bind_value = await self.variable.evaluate_async(context)
        else:
            bind_value = context.resolve(template_name)
            if bind_value == NOTHING:
                bind_value = None

        scope = {
            arg.name.value: await arg.expr.evaluate_async(context) for arg in self.args
        }

        ctx = context.copy(
            scope,
            disabled_tags=("include",),
            block_scope=False,
            template=template,
        )

        if self.loop and isinstance(bind_value, list):
            forloop = ForLoop(bind_key, len(bind_value), None)  # type: ignore
            scope["forloop"] = forloop
            for item in bind_value:  # type: ignore
                scope[bind_key] = item
                forloop.step()
                await template.render_with_context_async(ctx, buffer)
        else:
            scope[bind_key] = bind_value
            await template.render_with_context_async(ctx, buffer)

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        result: list[Expression] = []

        if self.variable:
            result.append(self.variable)

        result.extend(arg.expr for arg in self.args)
        return result

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        template = context.env.get_template(
            self.name.value,
            context=context,
            tag="render",
        )

        scope: list[Name] = [arg.name for arg in self.args]

        if self.variable:
            if self.alias:
                scope.append(self.alias)
            else:
                scope.append(Name(self.name.token, self.name.value))

        return [
            Partial(
                template=template,
                scope=SCOPE_ISOLATED,
                in_scope=scope,
                key=hash((self.name.value, ":".join(n.value for n in scope))),
            )
        ]

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        template = await context.env.get_template_async(
            self.name.value,
            context=context,
            tag="render",
        )

        scope: list[Name] = [arg.name for arg in self.args]

        if self.variable:
            if self.alias:
                scope.append(self.alias)
            else:
                scope.append(Name(self.name.token, self.name.value))

        return [
            Partial(
                template=template,
                scope=SCOPE_ISOLATED,
                in_scope=scope,
                key=hash((self.name.value, ":".join(n.value for n in scope))),
            )
        ]
