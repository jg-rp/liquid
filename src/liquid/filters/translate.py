from __future__ import annotations

import re
from gettext import NullTranslations
from typing import TYPE_CHECKING, Any, cast

from markupsafe import Markup

from .. import expressions
from .._markup import Expression
from .._messages import MESSAGES, MessageText, TranslatableFilter, Translations

if TYPE_CHECKING:
    from .._filter import FilterContext


class BaseTranslateFilter:
    """Base class for the default translation filters.

    Parameters
    ----------
    translations_var
        The name of a render context variable that resolves to a gettext `Translations`
        class. Defaults to ``"translations"``.
    default_translations
        A fallback translations class to use if `translations_var` can not be resolves.
        Defaults to ``NullTranslations``.
    message_interpolation
        If `True` (default), perform printf-style string interpolation on the translated
        message, using keyword arguments passed to the filter function.
    """

    re_vars = re.compile(r"(?<!%)%\((\w+)\)s")

    def __init__(
        self,
        *,
        translations_var: str = "translations",
        default_translations: Translations | None = None,
        message_interpolation: bool = True,
    ) -> None:
        self.translations_var = translations_var
        self.default_translations = default_translations or NullTranslations()
        self.message_interpolation = message_interpolation

    def format_message(
        self, context: FilterContext, message_text: str, message_vars: dict[str, Any]
    ) -> str:
        """Return the message string formatted with the given message variables."""
        with context.context.extend(namespace=message_vars):
            _vars = {
                k: context.env.serialize(
                    context.resolve(k), context.context, context.span
                )
                for k in self.re_vars.findall(message_text)
            }

        # Missing variables get replaced by the current `Undefined` type and we're
        # converting all values to a string, so a KeyError or a ValueError should
        # be impossible.
        return message_text % _vars

    def _resolve_translations(
        self, context: FilterContext
    ) -> Translations | NullTranslations:
        result = context.resolve(self.translations_var)
        if context.is_nil(result):
            return self.default_translations
        return cast(Translations, result)


class Translate(BaseTranslateFilter, TranslatableFilter):
    """A Liquid filter for translating strings to other languages.

    Depending on the keyword arguments provided when the resulting filter
    is called, it could behave like gettext, ngettext, pgettext or npgettext.
    """

    def __call__(
        self,
        context: FilterContext,
        left: object,
        message_context: object = None,
        **kwargs: Any,
    ) -> str:
        """Apply the filter and return the result."""
        autoescape = context.env.autoescape
        left_ = context.to_str(left, "")

        translations = self._resolve_translations(context)

        plural = kwargs.pop("plural", None)
        n = _count(kwargs.get("count"))

        if plural is not None and n is not None:
            plural = context.to_str(plural, "")

            if message_context is not None:
                text = translations.npgettext(
                    context.to_str(message_context, ""),
                    left_,
                    plural,
                    n,
                )
            else:
                text = translations.ngettext(left_, plural, n)
        elif message_context is not None:
            text = translations.pgettext(
                context.to_str(message_context, ""),
                left_,
            )
        else:
            text = translations.gettext(left_)

        if autoescape:
            text = Markup(text)

        if self.message_interpolation:
            text = self.format_message(context, text, kwargs)

        return text

    def message(
        self,
        left: Expression,
        filter_: expressions.Filtered,
        lineno: int,
    ) -> MessageText | None:
        if not isinstance(left, expressions.StringLiteral):
            return None

        if not filter_.args:
            return MessageText(
                lineno=lineno,
                funcname="gettext",
                message=(left.value,),
            )

        if not isinstance(filter_.args[0], expressions.KeywordArgument):
            context_: Expression | None = filter_.args[0]
        else:
            context_ = None

        plural: Expression | None = None
        for arg in filter_.args:
            if (
                isinstance(arg, expressions.KeywordArgument)
                and arg.name.value == "plural"
            ):
                plural = arg.expr

        # Translate our filters into standard *gettext argument specs.

        if isinstance(plural, expressions.StringLiteral):
            if isinstance(context_, expressions.StringLiteral):
                funcname = "npgettext"
                message: MESSAGES = ((context_.value, "c"), left.value, plural.value)
            else:
                funcname = "ngettext"
                message = (left.value, plural.value)
        elif plural is not None:
            # Don't attempt to extract any messages if plural is given but not a string
            # literal.
            return None
        elif isinstance(context_, expressions.StringLiteral):
            funcname = "pgettext"
            message = ((context_.value, "c"), left.value)
        else:
            funcname = "gettext"
            message = (left.value,)

        return MessageText(
            lineno=lineno,
            funcname=funcname,
            message=message,
        )


class GetText(BaseTranslateFilter, TranslatableFilter):
    """A Liquid filter equivalent of `gettext.gettext`."""

    def __call__(
        self,
        context: FilterContext,
        left: object,
        **kwargs: Any,
    ) -> str:
        autoescape = context.env.autoescape
        left_ = context.to_str(left, "")
        translations = self._resolve_translations(context)
        text = translations.gettext(left_)

        if autoescape:
            text = Markup(text)

        if self.message_interpolation:
            text = self.format_message(context, text, kwargs)

        return text

    def message(
        self,
        left: Expression,
        filter_: expressions.Filtered,
        lineno: int,
    ) -> MessageText | None:
        if not isinstance(left, expressions.StringLiteral):
            return None

        return MessageText(
            lineno=lineno,
            funcname="gettext",
            message=(left.value,),
        )


class NGetText(BaseTranslateFilter, TranslatableFilter):
    """A Liquid filter equivalent of `gettext.ngettext`."""

    def __call__(
        self,
        context: FilterContext,
        left: object,
        plural: str,
        count: object,
        **kwargs: Any,
    ) -> str:
        """Apply the filter and return the result."""
        left_ = context.to_str(left, "")

        plural = context.to_str(plural, "")
        count = int(context.to_numeric(count, 1))

        translations = self._resolve_translations(context)
        text = translations.ngettext(left_, plural, count)

        if context.env.autoescape:
            text = Markup(text)

        if self.message_interpolation:
            text = self.format_message(context, text, kwargs)

        return text

    def message(
        self,
        left: Expression,
        filter_: expressions.Filtered,
        lineno: int,
    ) -> MessageText | None:
        if len(filter_.args) < 1:
            return None

        plural = filter_.args[0]

        if not isinstance(left, expressions.StringLiteral) or not isinstance(
            plural, expressions.StringLiteral
        ):
            return None

        return MessageText(
            lineno=lineno,
            funcname="ngettext",
            message=(left.value, plural.value),
        )


class PGetText(BaseTranslateFilter, TranslatableFilter):
    """A Liquid filter equivalent of `gettext.pgettext`."""

    def __call__(
        self,
        context: FilterContext,
        left: object,
        message_context: str,
        **kwargs: Any,
    ) -> str:
        left_ = context.to_str(left, "")
        message_context = context.to_str(message_context, "")

        translations = self._resolve_translations(context)
        text = translations.pgettext(message_context, left_)

        if context.env.autoescape:
            text = Markup(text)

        if self.message_interpolation:
            text = self.format_message(context, text, kwargs)

        return text

    def message(
        self,
        left: Expression,
        filter_: expressions.Filtered,
        lineno: int,
    ) -> MessageText | None:
        if len(filter_.args) < 1:
            return None

        ctx = filter_.args[0]

        if not isinstance(left, expressions.StringLiteral) or not isinstance(
            ctx, expressions.StringLiteral
        ):
            return None

        return MessageText(
            lineno=lineno,
            funcname="pgettext",
            message=((ctx.value, "c"), left.value),
        )


class NPGetText(BaseTranslateFilter, TranslatableFilter):
    """A Liquid filter equivalent of `gettext.npgettext`."""

    def __call__(
        self,
        context: FilterContext,
        left: object,
        message_context: str,
        plural: str,
        count: object,
        **kwargs: Any,
    ) -> str:
        left_ = context.to_str(left, "")
        message_context = context.to_str(message_context, "")
        plural = context.to_str(plural, "")
        count = int(context.to_numeric(count, default=1))

        translations = self._resolve_translations(context)
        text = translations.npgettext(
            message_context,
            left_,
            plural,
            count,
        )

        if context.env.autoescape:
            text = Markup(text)

        if self.message_interpolation:
            text = self.format_message(context, text, kwargs)

        return text

    def message(
        self,
        left: Expression,
        filter_: expressions.Filtered,
        lineno: int,
    ) -> MessageText | None:
        if len(filter_.args) < 2:
            return None

        ctx = filter_.args[0]
        plural = filter_.args[1]

        if (
            not isinstance(left, expressions.StringLiteral)
            or not isinstance(plural, expressions.StringLiteral)
            or not isinstance(ctx, expressions.StringLiteral)
        ):
            return None

        return MessageText(
            lineno=lineno,
            funcname="npgettext",
            message=((ctx.value, "c"), left.value, plural.value),
        )


def _count(val: Any) -> int | None:
    if val in (None, False, True):
        return None
    try:
        return int(val)
    except ValueError:
        return None
