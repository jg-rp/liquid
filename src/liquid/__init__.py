from collections.abc import Mapping
from typing import Any

from ._context import RenderContext
from ._loader import Loader, TemplateSource
from ._template import Template
from .environment import Environment
from .loaders import DictLoader
from .tokens import TOKEN_NAMES, Token, TokenKind, span, token_value

__all__ = (
    "TOKEN_NAMES",
    "DictLoader",
    "Environment",
    "Loader",
    "RenderContext",
    "Template",
    "TemplateSource",
    "Token",
    "TokenKind",
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
