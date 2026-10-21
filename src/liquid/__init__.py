from collections.abc import Mapping
from typing import Any

from ._base_tag import AbstractTag
from ._context import RenderContext
from ._drop import ContextHint, Drop
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
from ._parser import Parser
from ._parser_extended import ExtendedParser
from ._parser_legacy import LegacyParser
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
    "AbstractTag",
    "Block",
    "CachingChoiceLoader",
    "CachingDictLoader",
    "CachingFileSystemLoader",
    "CachingLoaderMixin",
    "ChoiceLoader",
    "ContextHint",
    "DictLoader",
    "Drop",
    "Environment",
    "Expression",
    "ExtendedLexer",
    "ExtendedParser",
    "FalsyStrictUndefined",
    "FileSystemLoader",
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
    "Undefined",
    "render_block",
    "render_block_async",
    "span",
    "token_value",
)


DEFAULT_ENVIRONMENT = Environment()


def render(source: str, data: Mapping[str, Any]) -> str:
    return DEFAULT_ENVIRONMENT.render(source, data)


def parse(
    source: str,
    *,
    name: str = "",
    globals: Mapping[str, Any] | None = None,
) -> Template:
    return DEFAULT_ENVIRONMENT.parse(source, name=name, globals=globals)


class LaxLegacyParser(LaxParserMixin, LegacyParser):
    pass


class LaxExtendedParser(LaxParserMixin, ExtendedParser):
    pass
