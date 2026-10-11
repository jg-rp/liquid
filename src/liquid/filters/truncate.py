import re

from .._filter import FilterContext

MAX_TRUNC_WORDS = 2147483647

RE_S = re.compile(r"\s+")


def truncate(
    context: FilterContext, left: object, length: object = 50, end: object = "..."
) -> str:
    left = context.to_str(left, "")
    length = context.to_int(length)

    if len(left) < length:
        return left

    end = context.to_str(end, "")
    stop = 0 if length < len(end) else length - len(end)
    return left[0:stop] + end


def truncate_words(
    context: FilterContext, left: object, word_count: object = 15, end: object = "..."
) -> str:
    left = context.to_str(left, "")
    word_count = max(context.to_int(word_count), 1)

    if word_count >= MAX_TRUNC_WORDS:
        return left

    end = context.to_str(end, "")
    words = RE_S.split(left.strip())

    if len(words) <= word_count:
        return left

    return "".join(words[:word_count]) + end
