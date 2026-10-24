from __future__ import annotations

import os
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    NamedTuple,
    Protocol,
    TypeGuard,
)

from babel.messages import Catalog

from . import expressions
from .tags import CommentTag, InlineCommentTag, TemplateComment

if TYPE_CHECKING:
    from ._markup import Expression, Markup
    from ._template import Template
    from .environment import Environment


DEFAULT_KEYWORDS: dict[str, Any] = {
    "t": None,
    "trans": None,
    "translate": None,
    "gettext": None,
    "ngettext": (1, 2),
    "pgettext": ((1, "c"), 2),
    "npgettext": ((1, "c"), 2, 3),
}

DEFAULT_COMMENT_TAGS = [
    "Translators:",
]


class Translations(Protocol):
    """Message catalog interface.

    An object implementing this protocol is expected to be available in a render context.

    Could be a ``GNUTranslations`` instance from the ``gettext`` module, a Babel
    ``Translations`` object, or any object implementing ``gettext``, ``ngettext``,
    ``pgettext`` and ``npgettext`` methods.
    """

    def gettext(self, message: str) -> str:
        """Lookup the message in the catalog."""
        ...

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Do plural-forms message lookup."""
        ...

    def pgettext(self, context: str, message: str) -> str:
        """Lookup the context and message in the catalog."""
        ...

    def npgettext(self, context: str, singular: str, plural: str, n: int) -> str:
        """Do plural-forms context and message lookup."""
        ...


type MESSAGES = (
    str
    | tuple[str, ...]
    | tuple[tuple[str, str], str]
    | tuple[tuple[str, str], str, str]
)

type SPEC = (
    tuple[int, ...] | tuple[tuple[int, str], int] | tuple[tuple[int, str], int, int]
)


class MessageTuple(NamedTuple):
    """The tuple expected to be returned from babel extraction methods."""

    lineno: int
    funcname: str
    message: MESSAGES
    comments: list[str]


class MessageText(NamedTuple):
    """Partial message tuple returned from translatable tags."""

    lineno: int
    funcname: str
    message: MESSAGES


class TranslatableTag(Protocol):
    def messages(self, template: Template) -> Iterable[MessageText]:
        """Generate a sequence of translation messages."""
        ...

    def children(self) -> list[Markup]: ...


def translatable_tag(node: Markup) -> TypeGuard[TranslatableTag]:
    return hasattr(node, "messages")


class TranslatableFilter(Protocol):
    def message(
        self,
        left: Expression,
        filter_: expressions.Filtered,
        lineno: int,
    ) -> MessageText | None:
        """Return a translation message."""


def translatable_filter(node: object) -> TypeGuard[TranslatableFilter]:
    return hasattr(node, "message")


def extract_from_templates(
    *templates: Template,
    keywords: dict[str, Any] | None = None,
    comment_tags: list[str] | None = None,
    strip_comment_tags: bool = False,
) -> Catalog:
    """Extract messages from one or more templates.

    This function returns a single `babel.messages.Catalog` containing messages from all
    the given templates.

    Parameters
    ----------
    templates
        Templates to extract messages from.
    keywords
        A Babel compatible mapping of translatable "function" names to argument specs.
        The included translation filters and tag transform their messages into typical
        *gettext format, regardless of their names.
    comment_tags
        A list of translator tags to search for and include in extracted messages.
    strip_comment_tags
        If `True`, remove comment tags from collected message comments.
    """
    keywords = keywords or DEFAULT_KEYWORDS
    comment_tags = comment_tags or DEFAULT_COMMENT_TAGS
    catalog = Catalog()
    for template in templates:
        for lineno, funcname, messages, comments in extract_from_template(
            template, keywords, comment_tags
        ):
            # A partial re-implementation of Babel's messages.extract function.
            # See https://github.com/python-babel/babel/blob/master/babel/messages/extract.py#L262
            spec: SPEC = keywords[funcname] or (1,)
            if not isinstance(messages, (list, tuple)):
                messages = (messages,)
            if not messages:
                continue
            if len(spec) != len(messages):
                continue

            # Assumes context is the first item in the spec
            if isinstance(spec[0], tuple):
                # context aware message
                context = messages[spec[0][0] - 1][0]
                message = [messages[i - 1] for i in spec[1:]]
            else:
                context = None
                message = [messages[i - 1] for i in spec if isinstance(i, int)]

            if not message[0]:
                # Empty message
                continue

            if strip_comment_tags:
                comments = _strip_comment_tags(comments, comment_tags)

            # Use the template's path if it has one
            template_name = template.name
            if isinstance(template.path, Path):
                template_name = str(template.path.joinpath(template_name))
            elif isinstance(template.path, str):
                template_name = os.path.join(template.path, template_name)

            catalog.add(
                message[0] if len(message) == 1 else message,  # type: ignore
                "",
                [(template_name, lineno)],
                auto_comments=comments,
                context=context,
            )

    return catalog


def extract_from_template(
    template: Template,
    keywords: list[str] | dict[str, Any] | None = None,
    comment_tags: list[str] | None = None,
) -> Iterator[MessageTuple]:
    """Extract translation messages from a Liquid template."""
    comment_tags_ = comment_tags or DEFAULT_COMMENT_TAGS
    comments_: list[tuple[int, str]] = []
    keywords_ = keywords or DEFAULT_KEYWORDS

    def visit_expression(expr: Expression, lineno: int) -> Iterator[MessageTuple]:
        if isinstance(expr, expressions.Filtered):
            for _lineno, funcname, message in _extract_from_filters(
                template.env, expr, lineno, keywords_
            ):
                if comments_ and comments_[-1][0] < lineno - 1:
                    comments_.clear()

                yield MessageTuple(
                    lineno=_lineno,
                    funcname=funcname,
                    message=message,
                    comments=[text for _, text in comments_],
                )
                comments_.clear()

        for expression in expr.children():
            yield from visit_expression(expression, lineno)

    def visit(node: Markup) -> Iterator[MessageTuple]:
        lineno, _ = template.line_col(node.token)
        if (
            isinstance(node, (CommentTag, InlineCommentTag, TemplateComment))
            and node.text
        ):
            comment_text = node.text.strip()

            for comment_tag in comment_tags_:
                if comment_text.startswith(comment_tag):
                    # Our multi-line comments are wrapped in a tag, so we're
                    # only ever going to have one comment text object to deal
                    # with.
                    comments_.clear()
                    comments_.append((lineno, comment_text))
                    break

        elif translatable_tag(node):
            for lineno, funcname, message in node.messages(template):
                if comments_ and comments_[-1][0] < lineno - 1:
                    comments_.clear()

                yield MessageTuple(
                    lineno=lineno,
                    funcname=funcname,
                    message=message,
                    comments=[text for _, text in comments_],
                )
                comments_.clear()

        for child in node.children():
            for expr in child.expressions():
                yield from visit_expression(expr, template.line_col(expr.token)[0])
            yield from visit(child)

    for node in template.nodes:
        if not isinstance(node, str):
            for expr in node.expressions():
                yield from visit_expression(expr, template.line_col(expr.token)[0])
            yield from visit(node)


def _extract_from_filters(
    environment: Environment,
    expression: expressions.Filtered,
    lineno: int,
    keywords: list[str] | dict[str, Any],
) -> Iterable[MessageText]:
    if expression.name.value in keywords:
        filter_callable = environment.filters.get(expression.name.value)
        if translatable_filter(filter_callable):
            msg = filter_callable.message(expression.left, expression, lineno)
            if msg:
                yield msg


def _strip_comment_tags(comments: list[str], tags: list[str]) -> list[str]:
    """Similar to Babel's messages.extract._strip_comment_tags."""

    def _strip(line: str) -> str:
        for tag in tags:
            if line.startswith(tag):
                return line[len(tag) :].strip()
        return line

    return [_strip(comment) for comment in comments]
