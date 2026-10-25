from collections.abc import Iterator, Mapping
from typing import Any, TextIO

from ._base_tag import AbstractTag
from ._context import RenderContext
from ._drop import AbstractDrop, ContextHint
from ._filter import FilterContext
from ._io import StringBuffer
from ._lax_parser_mixin import LaxParserMixin
from ._lexer import Lexer
from ._lexer_extended import ExtendedLexer
from ._lexer_legacy import LegacyLexer
from ._loader import Loader, TemplateSource
from ._markup import (
    Block,
    Expression,
    Markup,
    Node,
    Partial,
    Scope,
    Tag,
    render_block,
    render_block_async,
)
from ._messages import MessageTuple, Translations, extract_from_template
from ._parser import Parser
from ._parser_extended import ExtendedParser
from ._parser_legacy import LegacyParser
from ._resource_limits import ResourceLimits
from ._static_analysis import Segments, TemplateAnalysis
from ._template import Template
from .drops import FalsyStrictUndefined, StrictUndefined, Undefined
from .environment import Environment
from .loaders import (
    CachingChoiceLoader,
    CachingDictLoader,
    CachingFileSystemLoader,
    CachingLoaderMixin,
    ChoiceLoader,
    DictLoader,
    FileSystemLoader,
    PackageLoader,
)
from .tokens import TOKEN_NAMES, Token, TokenKind, span, token_value

__all__ = (
    "TOKEN_NAMES",
    "AbstractDrop",
    "AbstractTag",
    "Block",
    "CachingChoiceLoader",
    "CachingDictLoader",
    "CachingFileSystemLoader",
    "CachingLoaderMixin",
    "ChoiceLoader",
    "ContextHint",
    "DictLoader",
    "Environment",
    "Expression",
    "ExtendedLexer",
    "ExtendedParser",
    "FalsyStrictUndefined",
    "FileSystemLoader",
    "FilterContext",
    "LaxExtendedParser",
    "LaxLegacyParser",
    "LaxParserMixin",
    "LegacyLexer",
    "LegacyParser",
    "Lexer",
    "Loader",
    "Markup",
    "Node",
    "PackageLoader",
    "Parser",
    "Partial",
    "RenderContext",
    "ResourceLimits",
    "Scope",
    "Segments",
    "StrictUndefined",
    "StringBuffer",
    "Tag",
    "Template",
    "TemplateAnalysis",
    "TemplateSource",
    "Token",
    "TokenKind",
    "Translations",
    "Undefined",
    "render_block",
    "render_block_async",
    "span",
    "token_value",
)


DEFAULT_ENVIRONMENT = Environment()


def parse(
    source: str,
    *,
    name: str = "",
    globals: Mapping[str, Any] | None = None,
) -> Template:
    """Parse template source code `source` using the default Liquid environment.

    Parameters
    ----------
    source
        Template source code.
    name
        A name for the template that will appear in error messages.
    globals
        Variables to pin to the resulting template.
    """
    return DEFAULT_ENVIRONMENT.parse(source, name=name, globals=globals)


def render(source: str, data: Mapping[str, Any] | None = None) -> str:
    """Parse and render `source` with variables from `data` using the default environment.

    Parameters
    ----------
    source
        Template source code.
    data
        Template variables.
    """
    return DEFAULT_ENVIRONMENT.render(source, data)


async def render_async(source: str, data: Mapping[str, Any] | None = None) -> str:
    """Parse and render `source` asynchronously with variables from `data` using the
    default environment.

    Parameters
    ----------
    source
        Template source code.
    data
        Template variables.
    """
    return await DEFAULT_ENVIRONMENT.render_async(source, data)


class LaxLegacyParser(LaxParserMixin, LegacyParser):
    """A legacy parser that suppresses Liquid syntax errors.

    Use ``Template.errors()`` to get a list of available ``LiquidSyntaxError`` instances.
    """


class LaxExtendedParser(LaxParserMixin, ExtendedParser):
    """An extended parser that suppresses Liquid syntax errors.

    Use ``Template.errors()`` to get a list of available ``LiquidSyntaxError`` instances.
    """


def extract_liquid(
    fileobj: TextIO,
    keywords: list[str],
    comment_tags: list[str] | None = None,
    options: Mapping[str, Any] | None = None,
) -> Iterator[MessageTuple]:
    """A babel compatible translation message extraction method for Liquid templates.

    See https://babel.pocoo.org/en/latest/messages.html

    Keywords are the names of Liquid filters or tags operating on translatable strings.
    For a filter to contribute to message extraction, it must also appear as a child of
    a `FilteredExpression` and be a `TranslatableFilter`. Similarly, tags must produce a
    node that is a `TranslatableTag`.

    Where a Liquid comment contains a prefix in `comment_tags`, the comment will be
    attached to the translatable filter or tag immediately following the comment. Python
    Liquid's non-standard shorthand comments are not supported.

    Use ``extract_from_template`` to extract messages from an existing template bound to
    an existing environment.
    """
    template = Environment(extra=True).parse(fileobj.read())
    return extract_from_template(
        template=template,
        keywords=keywords,
        comment_tags=comment_tags,
    )
