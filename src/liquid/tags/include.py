from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from .._markup import SCOPE_SHARED, Partial
from .._nothing import NOTHING
from ..exceptions import NoSuchTemplateError, TemplateNotFoundError
from ..expressions import Name, StringLiteral
from ..tokens import TOKEN_COMMA, TOKEN_TAG_END

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Expression, Markup
    from .._parser import Parser
    from ..expressions import KeywordArgument
    from ..tokens import Token


class IncludeTag:
    blank = False
    tag = "include"

    __slots__ = ("alias", "args", "name", "token", "variable")

    def __init__(
        self,
        token: Token,
        name: Expression,
        variable: Expression | None,
        alias: Name | None,
        args: list[KeywordArgument],
    ) -> None:
        self.token = token
        self.name = name
        self.variable = variable
        self.alias = alias
        self.args = args

    @staticmethod
    def parse(token: Token, parser: Parser) -> Markup:
        name_expr = parser.parse_expression()

        variable: Expression | None = None
        alias: Name | None = None

        # `for`, `with` and `as` don't have their own tokens kinds.
        ident = parser.value()
        if ident in ("for", "with"):
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
        return IncludeTag(token, name_expr, variable, alias, args)

    def render(self, context: RenderContext, buffer: TextIO) -> None:
        template_name = context.env.to_str(
            self.name.evaluate(context), context, self.name.span
        )

        try:
            template = context.env.get_template(
                template_name, context=context, tag="include"
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

        with context.extend(scope, template=template):
            if isinstance(bind_value, list):
                for item in bind_value:  # type: ignore
                    scope[bind_key] = item
                    template.render_with_context(context, buffer)
            else:
                scope[bind_key] = bind_value
                template.render_with_context(context, buffer)

    async def render_async(self, context: RenderContext, buffer: TextIO) -> None:
        template_name = context.env.to_str(
            await self.name.evaluate_async(context), context, self.name.span
        )

        try:
            template = await context.env.get_template_async(
                template_name, context=context, tag="include"
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

        with context.extend(scope, template=template):
            if isinstance(bind_value, list):
                for item in bind_value:  # type: ignore
                    scope[bind_key] = item
                    await template.render_with_context_async(context, buffer)
            else:
                scope[bind_key] = bind_value
                await template.render_with_context_async(context, buffer)

    def children(self) -> list[Markup]:
        return []

    def expressions(self) -> list[Expression]:
        result: list[Expression] = [self.name]

        if self.variable:
            result.append(self.variable)

        result.extend(arg.expr for arg in self.args)
        return result

    def block_scope(self) -> list[Name]:
        return []

    def template_scope(self) -> list[Name]:
        return []

    def partials(self, context: RenderContext) -> list[Partial]:
        name = self.name.evaluate(context)

        template = context.env.get_template(
            context.env.to_str(name, context, self.name.span),
            context=context,
            tag="include",
        )

        scope: list[Name] = [arg.name for arg in self.args]

        if self.variable:
            if self.alias:
                scope.append(self.alias)
            elif isinstance(self.name, StringLiteral):
                scope.append(Name(self.name.token, self.name.value))

        return [
            Partial(
                template=template,
                scope=SCOPE_SHARED,
                in_scope=scope,
                key=hash((str(self.name), ":".join(n.value for n in scope))),
            )
        ]

    async def partials_async(self, context: RenderContext) -> list[Partial]:
        name = await self.name.evaluate_async(context)

        template = await context.env.get_template_async(
            context.env.to_str(name, context, self.name.span),
            context=context,
            tag="include",
        )

        scope: list[Name] = [arg.name for arg in self.args]

        if self.variable:
            if self.alias:
                scope.append(self.alias)
            elif isinstance(self.name, StringLiteral):
                scope.append(Name(self.name.token, self.name.value))

        return [
            Partial(
                template=template,
                scope=SCOPE_SHARED,
                in_scope=scope,
                key=hash((str(self.name), ":".join(n.value for n in scope))),
            )
        ]
