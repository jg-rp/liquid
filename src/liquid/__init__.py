from collections.abc import Mapping
from typing import Any

from .environment import Environment
from .loaders import DictLoader
from .tokens import TOKEN_NAMES, Token, TokenKind, span, token_value

__all__ = (
    "TOKEN_NAMES",
    "DictLoader",
    "Environment",
    "Token",
    "TokenKind",
    "span",
    "token_value",
)


DEFAULT_ENVIRONMENT = Environment()


def render(source: str, data: Mapping[str, Any]) -> str:
    return DEFAULT_ENVIRONMENT.render(source, data)
