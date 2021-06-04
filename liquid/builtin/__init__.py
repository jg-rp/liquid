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

from .filters._math import abs_
from .filters._math import at_most
from .filters._math import at_least
from .filters._math import ceil
from .filters._math import divided_by
from .filters._math import floor
from .filters._math import minus
from .filters._math import plus
from .filters._math import round_
from .filters._math import times
from .filters._math import modulo

from .filters._string import capitalize
from .filters._string import append
from .filters._string import downcase
from .filters._string import escape
from .filters._string import escape_once
from .filters._string import lstrip
from .filters._string import newline_to_br
from .filters._string import prepend
from .filters._string import remove
from .filters._string import remove_first
from .filters._string import replace
from .filters._string import replace_first
from .filters._string import slice_
from .filters._string import split
from .filters._string import upcase
from .filters._string import strip
from .filters._string import rstrip
from .filters._string import strip_html
from .filters._string import strip_newlines
from .filters._string import truncate
from .filters._string import truncatewords
from .filters._string import url_encode
from .filters._string import url_decode
from .filters._string import base64_encode
from .filters._string import base64_decode
from .filters._string import base64_url_safe_encode
from .filters._string import base64_url_safe_decode

from .filters._array import join
from .filters._array import first
from .filters._array import last
from .filters._array import concat
from .filters._array import map_
from .filters._array import reverse
from .filters._array import sort
from .filters._array import sort_natural
from .filters._array import where
from .filters._array import uniq
from .filters._array import compact

from .filters._misc import size
from .filters._misc import default
from .filters._misc import date

from .filters._extra import safe


if TYPE_CHECKING:
    from liquid import Environment


def register(env: Environment) -> None:
    env.add_tag(literal.Literal)
    env.add_tag(statement.Statement)
    env.add_tag(illegal.Illegal)
    env.add_tag(if_tag.IfTag)
    env.add_tag(comment_tag.CommentTag)
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
    env.add_filter("replace", replace)
    env.add_filter("replace_first", replace_first)
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
