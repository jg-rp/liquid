"""Text processing utilities."""


def truncate_chars(val: str, num: int, end: str = "...") -> str:
    """Truncates a string if it is longer than the specified number of characters.
    Truncated strings will end with `end`, an ellipsis by default."""
    val_length = len(val)
    end_length = len(end)

    if val_length < num:
        return val

    return f"{val[:num-end_length]}{end}"


# Note: truncate_words is no longer used by the truncatewords filter.


def truncate_words(val: str, num: int, end: str = "...") -> str:  # pragma: no cover
    """Truncates a string down to the number of words passed as the first parameter."""
    # Replaces consecutive whitespace with a single newline.
    words = val.split()

    if len(words) < num:
        return " ".join(words)

    return " ".join(words[:num]) + end
