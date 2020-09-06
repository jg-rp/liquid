from liquid.builtin import literal
from liquid.builtin import statement
from liquid.builtin import illegal

from liquid.builtin.tags import if_tag
from liquid.builtin.tags import comment_tag
from liquid.builtin.tags import unless_tag
from liquid.builtin.tags import case_tag
from liquid.builtin.tags import for_tag
from liquid.builtin.tags import tablerow_tag
from liquid.builtin.tags import raw_tag
from liquid.builtin.tags import capture_tag
from liquid.builtin.tags import cycle_tag
from liquid.builtin.tags import assign_tag
from liquid.builtin.tags import increment_tag
from liquid.builtin.tags import decrement_tag
from liquid.builtin.tags import echo_tag
from liquid.builtin.tags import liquid_tag
from liquid.builtin.tags import include_tag
from liquid.builtin.tags import render_tag


from liquid.builtin.filters.math import (
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

from liquid.builtin.filters.string import (
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

from liquid.builtin.filters.array import (
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

from liquid.builtin.filters.misc import Size, Default, Date


def register(env):
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
    env.add_tag(raw_tag.RawTag)
    env.add_tag(capture_tag.CaptureTag)
    env.add_tag(cycle_tag.CycleTag)
    env.add_tag(assign_tag.AssignTag)
    env.add_tag(increment_tag.IncrementTag)
    env.add_tag(decrement_tag.DecrementTag)
    env.add_tag(echo_tag.EchoTag)
    env.add_tag(liquid_tag.LiquidTag)
    env.add_tag(include_tag.IncludeTag)
    env.add_tag(render_tag.RenderTag)

    env.filters[Abs.name] = Abs(env)
    env.filters[AtMost.name] = AtMost(env)
    env.filters[AtLeast.name] = AtLeast(env)
    env.filters[Ceil.name] = Ceil(env)
    env.filters[DividedBy.name] = DividedBy(env)
    env.filters[Floor.name] = Floor(env)
    env.filters[Minus.name] = Minus(env)
    env.filters[Plus.name] = Plus(env)
    env.filters[Round.name] = Round(env)
    env.filters[Times.name] = Times(env)
    env.filters[Modulo.name] = Modulo(env)

    env.filters[Capitalize.name] = Capitalize(env)
    env.filters[Append.name] = Append(env)
    env.filters[Downcase.name] = Downcase(env)
    env.filters[Escape.name] = Escape(env)
    env.filters[EscapeOnce.name] = EscapeOnce(env)
    env.filters[LStrip.name] = LStrip(env)
    env.filters[NewlineToBR.name] = NewlineToBR(env)
    env.filters[Prepend.name] = Prepend(env)
    env.filters[Remove.name] = Remove(env)
    env.filters[RemoveFirst.name] = RemoveFirst(env)
    env.filters[Replace.name] = Replace(env)
    env.filters[ReplaceFirst.name] = ReplaceFirst(env)
    env.filters[Slice.name] = Slice(env)
    env.filters[Split.name] = Split(env)
    env.filters[Upcase.name] = Upcase(env)
    env.filters[Strip.name] = Strip(env)
    env.filters[RStrip.name] = RStrip(env)
    env.filters[StripHTML.name] = StripHTML(env)
    env.filters[StripNewlines.name] = StripNewlines(env)
    env.filters[Truncate.name] = Truncate(env)
    env.filters[TruncateWords.name] = TruncateWords(env)
    env.filters[URLEncode.name] = URLEncode(env)
    env.filters[URLDecode.name] = URLDecode(env)

    env.filters[Join.name] = Join(env)
    env.filters[First.name] = First(env)
    env.filters[Last.name] = Last(env)
    env.filters[Concat.name] = Concat(env)
    env.filters[Map.name] = Map(env)
    env.filters[Reverse.name] = Reverse(env)
    env.filters[Sort.name] = Sort(env)
    env.filters[SortNatural.name] = SortNatural(env)
    env.filters[Where.name] = Where(env)
    env.filters[Uniq.name] = Uniq(env)
    env.filters[Compact.name] = Compact(env)

    env.filters[Size.name] = Size(env)
    env.filters[Default.name] = Default(env)
    env.filters[Date.name] = Date(env)
