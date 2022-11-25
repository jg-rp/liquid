# pylint: disable=missing-module-docstring
from __future__ import annotations
from typing import TYPE_CHECKING

from .tags import IfNotTag
from .tags import InlineIfAssignTag
from .tags import InlineIfAssignTagWithParens
from .tags import InlineIfEchoTag
from .tags import InlineIfEchoTagWithParens
from .tags import InlineIfStatement
from .tags import InlineIfStatementWithParens

if TYPE_CHECKING:
    from liquid import Environment

__all__ = (
    "IfNotTag",
    "InlineIfAssignTag",
    "InlineIfAssignTagWithParens",
    "InlineIfEchoTag",
    "InlineIfEchoTagWithParens",
    "InlineIfStatement",
    "InlineIfStatementWithParens",
    "register_inline_if_expressions",
    "register_inline_if_expressions_with_parens",
)


def register_inline_if_expressions(env: Environment) -> None:
    """Replace standard implementations of the output statement,
    `echo` tag and `assign` tag with ones that support inline `if`
    expressions."""
    env.add_tag(InlineIfAssignTag)
    env.add_tag(InlineIfEchoTag)
    env.add_tag(InlineIfStatement)


def register_inline_if_expressions_with_parens(env: Environment) -> None:
    """Replace standard implementations of the output statement,
    `echo` tag and `assign` tag with ones that support inline `if`
    expressions."""
    env.add_tag(InlineIfAssignTagWithParens)
    env.add_tag(InlineIfEchoTagWithParens)
    env.add_tag(InlineIfStatementWithParens)
