from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from gettext import NullTranslations
from typing import TYPE_CHECKING, cast

import markupsafe

from .. import expressions
from .._io import StringBuffer
from .._messages import MESSAGES, MessageText, Translations
from ..exceptions import TranslationSyntaxError
from ..expressions import Name
from ..tokens import TOKEN_COMMA, TOKEN_TAG_END
from .output import OutputStatement

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._markup import Block, Expression, Markup, Partial
    from .._parser import Parser
    from .._template import Template
    from ..expressions import KeywordArgument
    from ..tokens import Token

RE_VARS = re.compile(r"(?<!%)%\((\w+)\)s")
RE_WHITESPACE = re.compile(r"\s*\n\s*")


class TranslateTag:
    blank = False
    tag = "translate"

    default_translations = NullTranslations()
    translations_var = "translations"
    message_count_var = "count"
    message_context_var = "context"

    __slots__ = ("args", "plural_block", "singular_block", "token")

    def __init__(
        self,
        token: Token,
        args: list[KeywordArgument],
        singular_block: MessageBlock,
        plural_block: MessageBlock | None,
    ) -> None:
        self.token = token
        self.args = args
        self.singular_block = singular_block
        self.plural_block = plural_block

    @classmethod
    def parse(cls, token: Token, parser: Parser) -> Markup:
        if parser.kind() == TOKEN_COMMA:
            # Leading commas are OK.
            parser.next()

        args = parser.parse_keyword_arguments(require_commas=True)

        if parser.kind() == TOKEN_COMMA:
            # Trailing commas are OK.
            parser.next()

        parser.carry_whitespace_control()
        parser.eat(TOKEN_TAG_END)

        singular_block = cls.message_block(
            parser, parser.parse_block(("endtranslate", "plural"))
        )
        plural_block: MessageBlock | None = None

        if parser.tag("plural"):
            parser.eat_empty_tag("plural")
            plural_block = cls.message_block(
                parser, parser.parse_block(("endtranslate",))
            )

        parser.eat_empty_tag("endtranslate")
        return TranslateTag(token, args, singular_block, plural_block)

    @classmethod
    def message_block(cls, parser: Parser, block: Block) -> MessageBlock:
        message_text: list[str] = []
        message_vars: list[str] = []

        for node in block:
            if isinstance(node, str):
                message_text.append(node.replace("%", "%%"))

            elif isinstance(node, OutputStatement) and isinstance(
                node.expression, expressions.Variable
            ):
                expr = node.expression

                if not isinstance(expr.root, Name) or expr.selectors:
                    raise TranslationSyntaxError(
                        "expected a translation variable, found a path",
                        token=expr.span,
                        source=parser.source,
                        name=parser.template_name,
                    )

                message_text.append(f"%({expr.root.value})s")
                message_vars.append(expr.root.value)

            else:
                raise TranslationSyntaxError(
                    "unexpected markup in translation text",
                    token=node.token,
                    source=parser.source,
                    name=parser.template_name,
                )

        msg = "".join(message_text)
        return MessageBlock(block, RE_WHITESPACE.sub(" ", msg.strip()), message_vars)

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        translations = self.resolve_translations(context)
        scope: dict[str, object] = {}

        with context.extend(scope):
            for arg in self.args:
                scope[arg.name.value] = arg.expr.evaluate(context)

            count = self.resolve_count(context, scope)
            message_context = self.resolve_message_context(context, scope)

            message_text = self.gettext(
                translations,
                count=count,
                message_context=message_context,
            )

            return buffer.write(self._format_message(context, message_text))

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        translations = self.resolve_translations(context)
        scope: dict[str, object] = {}

        with context.extend(scope):
            for arg in self.args:
                scope[arg.name.value] = await arg.expr.evaluate_async(context)

            count = self.resolve_count(context, scope)
            message_context = self.resolve_message_context(context, scope)

            message_text = self.gettext(
                translations,
                count=count,
                message_context=message_context,
            )

            return buffer.write(self._format_message(context, message_text))

    def resolve_translations(
        self, context: RenderContext
    ) -> Translations | NullTranslations:
        """Return a translations object from the current render context."""
        t = context.resolve(self.translations_var)

        if context.env.is_nil(t):
            return self.default_translations

        return cast(Translations, t)

    def resolve_count(
        self,
        context: RenderContext,
        block_scope: dict[str, object],
    ) -> int | None:
        """Return a message count."""
        return int(
            context.env.to_numeric(
                block_scope.get(self.message_count_var, 1), context, 1
            )
        )

    def resolve_message_context(
        self,
        context: RenderContext,
        block_scope: dict[str, object],
    ) -> str | None:
        """Return the message context string."""
        message_context = block_scope.pop(self.message_context_var, None)

        if message_context:
            return (
                str(message_context)
                if not isinstance(message_context, str)
                else message_context
            )  # Just in case we get a Markupsafe object.

        return None

    def gettext(
        self,
        translations: Translations | NullTranslations,
        count: int | None,
        message_context: str | None,
    ) -> str:
        """Get translated text from the given translations object."""
        if self.plural_block and count:
            if message_context:
                return translations.npgettext(
                    message_context,
                    self.singular_block.text,
                    self.plural_block.text,
                    count,
                )

            return translations.ngettext(
                self.singular_block.text,
                self.plural_block.text,
                count,
            )

        if message_context:
            return translations.pgettext(message_context, self.singular_block.text)

        return translations.gettext(self.singular_block.text)

    def children(self) -> list[Markup]:
        result = [
            node for node in self.singular_block.block if not isinstance(node, str)
        ]

        if self.plural_block:
            result.extend(
                node for node in self.plural_block.block if not isinstance(node, str)
            )

        return result

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

    def messages(self, template: Template) -> Iterable[MessageText]:
        if not self.singular_block.block:
            return ()

        message_context: Expression | None = None
        for arg in self.args:
            if arg.name.value == self.message_context_var:
                message_context = arg.expr

        if self.plural_block:
            if message_context and isinstance(
                message_context, expressions.StringLiteral
            ):
                funcname = "npgettext"
                message: MESSAGES = (
                    (message_context.value, "c"),
                    self.singular_block.text,
                    self.plural_block.text,
                )
            else:
                funcname = "ngettext"
                message = (
                    self.singular_block.text,
                    self.plural_block.text,
                )
        elif message_context and isinstance(message_context, expressions.StringLiteral):
            funcname = "pgettext"
            message = (
                (message_context.value, "c"),
                self.singular_block.text,
            )
        else:
            funcname = "gettext"
            message = (self.singular_block.text,)

        return (
            MessageText(
                lineno=template.line_col(self.token)[0],
                funcname=funcname,
                message=message,
            ),
        )

    def _format_message(
        self,
        context: RenderContext,
        message_text: str,
    ) -> str:
        """Return the message string formatted with the given message variables."""
        if context.env.autoescape:
            message_text = markupsafe.Markup(message_text)

        _vars = {
            k: context.env.to_str(context.resolve(k), context, self.token)
            for k in RE_VARS.findall(message_text)
        }

        return message_text % _vars


@dataclass(slots=True)
class MessageBlock:
    block: Block
    text: str
    args: list[str]
