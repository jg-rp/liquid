# pylint: disable=missing-module-docstring
from __future__ import annotations

from typing import TYPE_CHECKING

from . import literal
from . import statement
from . import illegal

from .tags import if_tag
from .tags import comment_tag
from .tags import unless_tag
from .tags import case_tag
from .tags import for_tag
from .tags import tablerow_tag
from .tags import capture_tag
from .tags import cycle_tag
from .tags import assign_tag
from .tags import increment_tag
from .tags import decrement_tag
from .tags import echo_tag
from .tags import liquid_tag
from .tags import include_tag
from .tags import render_tag
from .tags import ifchanged_tag
from .tags import inline_comment_tag

from .filters.math import abs_
from .filters.math import at_most
from .filters.math import at_least
from .filters.math import ceil
from .filters.math import divided_by
from .filters.math import floor
from .filters.math import minus
from .filters.math import plus
from .filters.math import round_
from .filters.math import times
from .filters.math import modulo

from .filters.string import capitalize
from .filters.string import append
from .filters.string import downcase
from .filters.string import escape
from .filters.string import escape_once
from .filters.string import lstrip
from .filters.string import newline_to_br
from .filters.string import prepend
from .filters.string import remove
from .filters.string import remove_first
from .filters.string import remove_last
from .filters.string import replace
from .filters.string import replace_first
from .filters.string import replace_last
from .filters.string import slice_
from .filters.string import split
from .filters.string import upcase
from .filters.string import strip
from .filters.string import rstrip
from .filters.string import strip_html
from .filters.string import strip_newlines
from .filters.string import truncate
from .filters.string import truncatewords
from .filters.string import url_encode
from .filters.string import url_decode
from .filters.string import base64_encode
from .filters.string import base64_decode
from .filters.string import base64_url_safe_encode
from .filters.string import base64_url_safe_decode

from .filters.array import join
from .filters.array import first
from .filters.array import last
from .filters.array import concat
from .filters.array import map_
from .filters.array import reverse
from .filters.array import sort
from .filters.array import sort_natural
from .filters.array import where
from .filters.array import uniq
from .filters.array import compact

from .filters.misc import size
from .filters.misc import default
from .filters.misc import date

from .filters.extra import safe


if TYPE_CHECKING:
    from liquid import Environment


# pylint: disable=too-many-statements
def register(env: Environment) -> None:
    """Register all built-in tags and filters with an environment."""
    env.add_tag(literal.Literal)
    env.add_tag(statement.Statement)
    env.add_tag(illegal.Illegal)
    env.add_tag(if_tag.IfTag)
    env.add_tag(comment_tag.CommentTextTag)
    env.add_tag(unless_tag.UnlessTag)
    env.add_tag(case_tag.CaseTag)
    env.add_tag(for_tag.ForTag)
    env.add_tag(for_tag.BreakTag)
    env.add_tag(for_tag.ContinueTag)
    env.add_tag(tablerow_tag.TablerowTag)
    env.add_tag(capture_tag.CaptureTag)
    env.add_tag(cycle_tag.CycleTag)
    env.add_tag(assign_tag.AssignTag)
    env.add_tag(increment_tag.IncrementTag)
    env.add_tag(decrement_tag.DecrementTag)
    env.add_tag(echo_tag.EchoTag)
    env.add_tag(liquid_tag.LiquidTag)
    env.add_tag(include_tag.IncludeTag)
    env.add_tag(render_tag.RenderTag)
    env.add_tag(ifchanged_tag.IfChangedTag)
    env.add_tag(inline_comment_tag.InlineCommentTag)

    env.add_filter("abs", abs_)
    env.add_filter("at_most", at_most)
    env.add_filter("at_least", at_least)
    env.add_filter("ceil", ceil)
    env.add_filter("divided_by", divided_by)
    env.add_filter("floor", floor)
    env.add_filter("minus", minus)
    env.add_filter("plus", plus)
    env.add_filter("round", round_)
    env.add_filter("times", times)
    env.add_filter("modulo", modulo)

    env.add_filter("capitalize", capitalize)
    env.add_filter("append", append)
    env.add_filter("downcase", downcase)
    env.add_filter("escape", escape)
    env.add_filter("escape_once", escape_once)
    env.add_filter("lstrip", lstrip)
    env.add_filter("newline_to_br", newline_to_br)
    env.add_filter("prepend", prepend)
    env.add_filter("remove", remove)
    env.add_filter("remove_first", remove_first)
    env.add_filter("remove_last", remove_last)
    env.add_filter("replace", replace)
    env.add_filter("replace_first", replace_first)
    env.add_filter("replace_last", replace_last)
    env.add_filter("slice", slice_)
    env.add_filter("split", split)
    env.add_filter("upcase", upcase)
    env.add_filter("strip", strip)
    env.add_filter("rstrip", rstrip)
    env.add_filter("strip_html", strip_html)
    env.add_filter("strip_newlines", strip_newlines)
    env.add_filter("truncate", truncate)
    env.add_filter("truncatewords", truncatewords)
    env.add_filter("url_encode", url_encode)
    env.add_filter("url_decode", url_decode)
    env.add_filter("base64_encode", base64_encode)
    env.add_filter("base64_decode", base64_decode)
    env.add_filter("base64_url_safe_encode", base64_url_safe_encode)
    env.add_filter("base64_url_safe_decode", base64_url_safe_decode)

    env.add_filter("join", join)
    env.add_filter("first", first)
    env.add_filter("last", last)
    env.add_filter("concat", concat)
    env.add_filter("map", map_)
    env.add_filter("reverse", reverse)
    env.add_filter("sort", sort)
    env.add_filter("sort_natural", sort_natural)
    env.add_filter("where", where)
    env.add_filter("uniq", uniq)
    env.add_filter("compact", compact)

    env.add_filter("size", size)
    env.add_filter("default", default)
    env.add_filter("date", date)

    env.add_filter("safe", safe)
