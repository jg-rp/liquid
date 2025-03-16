from __future__ import annotations  # noqa: D104

from typing import TYPE_CHECKING

from .filters import JSON
from .filters import BaseTranslateFilter
from .filters import Currency
from .filters import DateTime
from .filters import GetText
from .filters import NGetText
from .filters import NPGetText
from .filters import Number
from .filters import PGetText
from .filters import Translate
from .filters import Unit
from .filters import index
from .filters import script_tag
from .filters import sort_numeric
from .filters import stylesheet_tag
from .tags import BlockTag
from .tags import CallTag
from .tags import ExtendsTag
from .tags import MacroTag
from .tags import TranslateTag
from .tags import WithTag

if TYPE_CHECKING:
    from liquid import Environment

__all__ = (
    "add_filters",
    "add_tags_and_filters",
    "add_tags",
    "BaseTranslateFilter",
    "BlockTag",
    "CallTag",
    "Currency",
    "DateTime",
    "ExtendsTag",
    "GetText",
    "IfNotTag",
    "index",
    "JSON",
    "MacroTag",
    "NGetText",
    "NPGetText",
    "Number",
    "PGetText",
    "script_tag",
    "sort_numeric",
    "stylesheet_tag",
    "Translate",
    "Unit",
    "WithTag",
)


def add_tags(env: Environment) -> None:
    """Register all extra tags with the given environment."""
    env.add_tag(ExtendsTag)
    env.add_tag(BlockTag)
    env.add_tag(MacroTag)
    env.add_tag(CallTag)
    env.add_tag(WithTag)
    env.add_tag(TranslateTag)


def add_filters(env: Environment) -> None:
    """Register all extra filters with an environment with their default options."""
    env.add_filter("index", index)
    env.add_filter("json", JSON())
    env.add_filter("script_tag", script_tag)
    env.add_filter("sort_numeric", sort_numeric)
    env.add_filter("stylesheet_tag", stylesheet_tag)

    env.filters[GetText.name] = GetText(autoescape_message=env.autoescape)
    env.filters[NGetText.name] = NGetText(autoescape_message=env.autoescape)
    env.filters[NPGetText.name] = NPGetText(autoescape_message=env.autoescape)
    env.filters[PGetText.name] = PGetText(autoescape_message=env.autoescape)
    env.filters[Translate.name] = Translate(autoescape_message=env.autoescape)
    env.filters["currency"] = Currency()
    env.filters["money"] = Currency()
    env.filters["money_with_currency"] = Currency(default_format="¤#,##0.00 ¤¤")
    env.filters["money_without_currency"] = Currency(default_format="#,##0.00")
    env.filters["money_without_trailing_zeros"] = Currency(
        default_format="¤#,###",
        currency_digits=False,
    )
    env.filters["datetime"] = DateTime()
    env.filters["decimal"] = Number()
    env.filters["unit"] = Unit()


def add_tags_and_filters(env: Environment) -> None:  # pragma: no cover
    """Register all extra tags and filters with an environment."""
    add_tags(env)
    add_filters(env)
