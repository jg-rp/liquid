import re

from .._filter import FilterContext

MAX_TRUNC_WORDS = 2147483647

RE_S = re.compile(r"\s+")


def truncate(
    context: FilterContext, left: object, length: object = 50, end: object = "..."
) -> str:
    left_ = context.to_str(left, "")
    length_ = context.to_int(length)

    if len(left_) <= length_:
        return left_

    end_ = context.to_str(end, "")
    stop = 0 if length_ < len(end_) else length_ - len(end_)
    return left_[0:stop] + end_


def truncate_words(
    context: FilterContext, left: object, word_count: object = 15, end: object = "..."
) -> str:
    left_ = context.to_str(left, "")
    word_count_ = max(context.to_int(word_count), 1)

    if word_count_ >= MAX_TRUNC_WORDS:
        return left_

    end_ = context.to_str(end, "")
    words = RE_S.split(left_.strip())

    if len(words) <= word_count_:
        return left_

    return " ".join(words[:word_count_]) + end_
