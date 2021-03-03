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


from .filters.math import (
    Abs,
    AtMost,
    AtLeast,
    Ceil,
    DividedBy,
    Floor,
    Minus,
    Plus,
    Round,
    Times,
    Modulo,
)

from .filters.string import (
    Capitalize,
    Append,
    Downcase,
    Escape,
    EscapeOnce,
    LStrip,
    NewlineToBR,
    Prepend,
    Remove,
    RemoveFirst,
    Replace,
    ReplaceFirst,
    Slice,
    Split,
    Upcase,
    Strip,
    RStrip,
    StripHTML,
    StripNewlines,
    Truncate,
    TruncateWords,
    URLEncode,
    URLDecode,
)

from .filters.array import (
    Join,
    First,
    Last,
    Concat,
    Map,
    Reverse,
    Sort,
    SortNatural,
    Where,
    Uniq,
    Compact,
)

from .filters.misc import Size, Default, Date


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

    env.add_filter(Abs.name, Abs(env))
    env.add_filter(AtMost.name, AtMost(env))
    env.add_filter(AtLeast.name, AtLeast(env))
    env.add_filter(Ceil.name, Ceil(env))
    env.add_filter(DividedBy.name, DividedBy(env))
    env.add_filter(Floor.name, Floor(env))
    env.add_filter(Minus.name, Minus(env))
    env.add_filter(Plus.name, Plus(env))
    env.add_filter(Round.name, Round(env))
    env.add_filter(Times.name, Times(env))
    env.add_filter(Modulo.name, Modulo(env))

    env.add_filter(Capitalize.name, Capitalize(env))
    env.add_filter(Append.name, Append(env))
    env.add_filter(Downcase.name, Downcase(env))
    env.add_filter(Escape.name, Escape(env))
    env.add_filter(EscapeOnce.name, EscapeOnce(env))
    env.add_filter(LStrip.name, LStrip(env))
    env.add_filter(NewlineToBR.name, NewlineToBR(env))
    env.add_filter(Prepend.name, Prepend(env))
    env.add_filter(Remove.name, Remove(env))
    env.add_filter(RemoveFirst.name, RemoveFirst(env))
    env.add_filter(Replace.name, Replace(env))
    env.add_filter(ReplaceFirst.name, ReplaceFirst(env))
    env.add_filter(Slice.name, Slice(env))
    env.add_filter(Split.name, Split(env))
    env.add_filter(Upcase.name, Upcase(env))
    env.add_filter(Strip.name, Strip(env))
    env.add_filter(RStrip.name, RStrip(env))
    env.add_filter(StripHTML.name, StripHTML(env))
    env.add_filter(StripNewlines.name, StripNewlines(env))
    env.add_filter(Truncate.name, Truncate(env))
    env.add_filter(TruncateWords.name, TruncateWords(env))
    env.add_filter(URLEncode.name, URLEncode(env))
    env.add_filter(URLDecode.name, URLDecode(env))

    env.add_filter(Join.name, Join(env))
    env.add_filter(First.name, First(env))
    env.add_filter(Last.name, Last(env))
    env.add_filter(Concat.name, Concat(env))
    env.add_filter(Map.name, Map(env))
    env.add_filter(Reverse.name, Reverse(env))
    env.add_filter(Sort.name, Sort(env))
    env.add_filter(SortNatural.name, SortNatural(env))
    env.add_filter(Where.name, Where(env))
    env.add_filter(Uniq.name, Uniq(env))
    env.add_filter(Compact.name, Compact(env))

    env.add_filter(Size.name, Size(env))
    env.add_filter(Default.name, Default(env))
    env.add_filter(Date.name, Date(env))
