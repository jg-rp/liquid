"""Extra HTML filters."""
from __future__ import annotations
import html

from typing import TYPE_CHECKING

from liquid import Markup
from liquid.filter import string_filter
from liquid.filter import with_environment

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment


@string_filter
@with_environment
def stylesheet_tag(url: str, *, environment: Environment) -> str:
    """Wrap a URL in an HTML stylesheet tag."""
    tag = '<link href="{}" rel="stylesheet" type="text/css" media="all" />'
    if environment.autoescape:
        return Markup(tag).format(str(url))
    return tag.format(html.escape(url))


@string_filter
@with_environment
def script_tag(url: str, *, environment: Environment) -> str:
    """Wrap a URL in an HTML script tag."""
    tag = '<script src="{}" type="text/javascript"></script>'
    if environment.autoescape:
        return Markup(tag).format(str(url))
    return tag.format(html.escape(url))
