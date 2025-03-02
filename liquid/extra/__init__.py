from __future__ import annotations  # noqa: D104

from typing import TYPE_CHECKING

from .filters import JSON
from .filters import index
from .filters import script_tag
from .filters import sort_numeric
from .filters import stylesheet_tag
from .tags import BlockTag
from .tags import CallTag
from .tags import ExtendsTag
from .tags import MacroTag
from .tags import WithTag

if TYPE_CHECKING:
    from liquid import Environment

__all__ = (
    "add_filters",
    "add_macro_tags",
    "add_tags_and_filters",
    "BlockTag",
    "CallTag",
    "ExtendsTag",
    "IfNotTag",
    "index",
    "JSON",
    "MacroTag",
    "script_tag",
    "sort_numeric",
    "stylesheet_tag",
    "WithTag",
)

# TODO:


def add_filters(env: Environment) -> None:
    """Register all extra filters with an environment with their default options."""
    env.add_filter("index", index)
    env.add_filter("json", JSON())
    env.add_filter("script_tag", script_tag)
    env.add_filter("sort_numeric", sort_numeric)
    env.add_filter("stylesheet_tag", stylesheet_tag)


def add_tags_and_filters(env: Environment) -> None:  # pragma: no cover
    """Register all extra tags and filters with an environment."""
    add_filters(env)
