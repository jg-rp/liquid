"""Filter functions that operate on strings."""

import html
from urllib.parse import quote_plus, unquote_plus

from liquid.filter import Filter
from liquid.filter import (
    one_maybe_two_args,
    expect_integer,
    expect_string,
    string_required,
    no_args,
    one_string_arg_required,
    two_string_args_required,
)

from liquid.exceptions import FilterArgumentError
from liquid.utils.html import strip_tags
from liquid.utils.text import truncate_chars, truncate_words

# XXX: Should we be casting int and float arguments to strings?


class Capitalize(Filter):
    """Make sure the first character of a string is upper case."""

    __slots__ = ()

    name = "capitalize"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.capitalize()


class Append(Filter):
    """Concatenate two strings."""

    __slots__ = ()

    name = "append"

    @string_required
    @one_string_arg_required
    def __call__(self, val, *args, **kwargs):
        return "".join((val, args[0]))


class Downcase(Filter):
    """Make all characters in a string lower case."""

    __slots__ = ()

    name = "downcase"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.lower()


class Escape(Filter):
    """Convert the characters &, < and > in string s to HTML-safe sequences."""

    __slots__ = ()

    name = "escape"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return html.escape(val)


class EscapeOnce(Filter):
    """Convert the characters &, < and > in string s to HTML-safe sequences."""

    __slots__ = ()

    name = "escape_once"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return html.escape(html.unescape(val))


class LStrip(Filter):
    """Remove leading whitespace."""

    __slots__ = ()

    name = "lstrip"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.lstrip()


class NewlineToBR(Filter):
    """Convert '\n' to '<br />'."""

    __slots__ = ()

    name = "newline_to_br"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.replace("\n", "<br />")


class Prepend(Filter):
    """Concatenate string value to argument string."""

    __slots__ = ()

    name = "prepend"

    @string_required
    @one_string_arg_required
    def __call__(self, val, *args, **kwargs):
        return "".join((args[0], val))


class Remove(Filter):
    """Remove all occurences of argument string from value."""

    __slots__ = ()

    name = "remove"

    @string_required
    @one_string_arg_required
    def __call__(self, val, *args, **kwargs):
        return val.replace(args[0], "")


class RemoveFirst(Filter):
    """Remove the first occurence of the argument string from value."""

    __slots__ = ()

    name = "remove_first"

    @string_required
    @one_string_arg_required
    def __call__(self, val, *args, **kwargs):
        return val.replace(args[0], "", 1)


class Replace(Filter):
    """Replace all occurences of argument string in value."""

    __slots__ = ()

    name = "replace"

    @string_required
    @two_string_args_required
    def __call__(self, val, *args, **kwargs):
        return val.replace(args[0], args[1])


class ReplaceFirst(Filter):
    """Replace the first occurence of the argument string in value."""

    __slots__ = ()

    name = "replace_first"

    @string_required
    @two_string_args_required
    def __call__(self, val, *args, **kwargs):
        return val.replace(args[0], args[1], 1)


class Upcase(Filter):
    """Make all characters in a string upper case."""

    __slots__ = ()

    name = "upcase"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.upper()


class Slice(Filter):
    """Return a substring of `val`."""

    __slots__ = ()

    name = "slice"

    @string_required
    def __call__(self, val, *args, **kwargs):
        start, length = one_maybe_two_args(self.name, args, kwargs)
        expect_integer(self.name, start)

        if length is not None:
            expect_integer(self.name, length)
        else:
            length = 1

        max_index = len(val) - 1
        if start > max_index:
            raise FilterArgumentError(f"{self.name}: string index out of range")

        return val[start : start + length]


class Split(Filter):
    """Return a list of strings, using the argument value as a delimiter."""

    __slots__ = ()

    name = "split"

    @string_required
    @one_string_arg_required
    def __call__(self, val, *args, **kwargs):
        return val.split(args[0])


class Strip(Filter):
    """Remove leading and trailing whitespace."""

    __slots__ = ()

    name = "strip"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.strip()


class RStrip(Filter):
    """Remove trailing whitespace."""

    __slots__ = ()

    name = "rstrip"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.rstrip()


class StripHTML(Filter):
    """Return the given HTML with all tags stripped."""

    __slots__ = ()

    name = "strip_html"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return strip_tags(val)


class StripNewlines(Filter):
    """Return the given string with all newline characters removed."""

    __slots__ = ()

    name = "strip_newlines"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return val.replace("\n", "")


class Truncate(Filter):
    """Truncates a string if it is longer than the specified number of characters."""

    __slots__ = ()

    name = "truncate"

    @string_required
    def __call__(self, val, *args, **kwargs):
        num, end = one_maybe_two_args(self.name, args, kwargs)
        expect_integer(self.name, num)

        if end is not None:
            expect_string(self.name, end)
        else:
            end = "..."

        return truncate_chars(val, num, end)


class TruncateWords(Filter):
    """Shortens a string down to the number of words passed as an argument."""

    __slots__ = ()

    name = "truncatewords"

    @string_required
    def __call__(self, val, *args, **kwargs):
        num, end = one_maybe_two_args(self.name, args, kwargs)
        expect_integer(self.name, num)

        if end is not None:
            expect_string(self.name, end)
        else:
            end = "..."

        return truncate_words(val, num, end)


class URLEncode(Filter):
    """Converts any URL-unsafe characters in a string into percent-encoded characters."""

    __slots__ = ()

    name = "url_encode"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return quote_plus(val)


class URLDecode(Filter):
    """Decodes a string that has been encoded as a URL."""

    __slots__ = ()

    name = "url_decode"

    @no_args
    @string_required
    def __call__(self, val, *args, **kwargs):
        return unquote_plus(val)
