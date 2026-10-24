from __future__ import annotations

import html

import markupsafe

from .._filter import FilterContext


def stylesheet_tag(context: FilterContext, left: object) -> str:
    tag = '<link href="{}" rel="stylesheet" type="text/css" media="all" />'
    if context.env.autoescape:
        return markupsafe.Markup(tag).format(str(left))
    return tag.format(html.escape(context.to_str(left, "")))


def script_tag(context: FilterContext, left: object) -> str:
    tag = '<script src="{}" type="text/javascript"></script>'
    if context.env.autoescape:
        return markupsafe.Markup(tag).format(str(left))
    return tag.format(html.escape(context.to_str(left, "")))
