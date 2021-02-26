"""Filter functions that operate on strings."""

import html
import re
import urllib.parse

from liquid.filter import Filter
from liquid.filter import one_maybe_two_args
from liquid.filter import expect_integer
from liquid.filter import expect_string
from liquid.filter import string_required

from liquid.exceptions import FilterArgumentError
from liquid.utils.html import strip_tags
from liquid.utils.text import truncate_chars, truncate_words

# pylint: disable=arguments-differ too-few-public-methods


class StringFilter(Filter):

    __slots__ = ()

    name = "AbstractStringFilter"
    num_args = 0
    msg = "{}: expected a string, found {}"

    def __call__(self, val, *args):
        if len(args) != self.num_args:
            raise FilterArgumentError(
                f"{self.name}: expected {self.num_args} arguments, found {len(args)}"
            )
        try:
            return self.filter(str(val), *args)
        except (AttributeError, TypeError) as err:
            raise FilterArgumentError(self.msg.format(self.name, type(val))) from err

    def filter(self, val, *args):
        raise NotImplementedError(":(")


class Capitalize(StringFilter):
    """Make sure the first character of a string is upper case."""

    __slots__ = ()

    name = "capitalize"

    def filter(self, val):
        return val.capitalize()


class Append(StringFilter):
    """Concatenate two strings."""

    __slots__ = ()

    name = "append"
    num_args = 1

    def filter(self, val: str, string: str):
        return val + str(string)


class Downcase(StringFilter):
    """Make all characters in a string lower case."""

    __slots__ = ()

    name = "downcase"

    def filter(self, val):
        return val.lower()


class Escape(StringFilter):
    """Convert the characters &, < and > in string s to HTML-safe sequences."""

    __slots__ = ()

    name = "escape"

    def filter(self, val):
        return html.escape(val)


class EscapeOnce(StringFilter):
    """Convert the characters &, < and > in string s to HTML-safe sequences."""

    __slots__ = ()

    name = "escape_once"

    def filter(self, val):
        return html.escape(html.unescape(val))


class LStrip(StringFilter):
    """Remove leading whitespace."""

    __slots__ = ()

    name = "lstrip"

    def filter(self, val):
        return val.lstrip()


class NewlineToBR(StringFilter):
    """Convert '\r\n' or '\n' to '<br />\n'."""

    __slots__ = ()

    name = "newline_to_br"
    re_lineterm = re.compile(r"\r?\n")

    def filter(self, val):
        # The reference implementation was changed to replace "\r\n" as well as "\n",
        # but they don't seem to care about "\r" (Mac OS).
        return self.re_lineterm.sub("<br />\n", val)


class Prepend(StringFilter):
    """Concatenate string value to argument string."""

    __slots__ = ()

    name = "prepend"
    num_args = 1

    def filter(self, val, string):
        return str(string) + val


class Remove(StringFilter):
    """Remove all occurrences of argument string from value."""

    __slots__ = ()

    name = "remove"
    num_args = 1

    def filter(self, val, sub):
        return val.replace(str(sub), "")


class RemoveFirst(StringFilter):
    """Remove the first occurrences of the argument string from value."""

    __slots__ = ()

    name = "remove_first"
    num_args = 1

    def filter(self, val, sub):
        return val.replace(str(sub), "", 1)


class Replace(StringFilter):
    """Replace all occurrences of argument string in value."""

    __slots__ = ()

    name = "replace"
    num_args = 2

    def filter(self, val, seq, sub):
        return val.replace(str(seq), str(sub))


class ReplaceFirst(StringFilter):
    """Replace the first occurrences of the argument string in value."""

    __slots__ = ()

    name = "replace_first"
    num_args = 2

    def filter(self, val, seq, sub):
        return val.replace(str(seq), str(sub), 1)


class Upcase(StringFilter):
    """Make all characters in a string upper case."""

    __slots__ = ()

    name = "upcase"

    def filter(self, val):
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


class Split(StringFilter):
    """Return a list of strings, using the argument value as a delimiter."""

    __slots__ = ()

    name = "split"
    num_args = 1

    def filter(self, val, seq):
        return val.split(str(seq))


class Strip(StringFilter):
    """Remove leading and trailing whitespace."""

    __slots__ = ()

    name = "strip"

    def filter(self, val):
        return val.strip()


class RStrip(StringFilter):
    """Remove trailing whitespace."""

    __slots__ = ()

    name = "rstrip"

    def filter(self, val):
        return val.rstrip()


class StripHTML(StringFilter):
    """Return the given HTML with all tags stripped."""

    __slots__ = ()

    name = "strip_html"

    def filter(self, val):
        return strip_tags(val)


class StripNewlines(StringFilter):
    """Return the given string with all newline characters removed."""

    __slots__ = ()

    name = "strip_newlines"
    re_lineterm = re.compile(r"\r?\n")

    def filter(self, val):
        return self.re_lineterm.sub("", val)


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
            end = str(end)
        else:
            end = "..."

        # The reference implementation seems to force a minimum `num` of 1.
        if num <= 0:
            num = 1

        return truncate_words(val, num, end)


class URLEncode(StringFilter):
    """Converts any URL-unsafe characters in a string into percent-encoded
    characters."""

    __slots__ = ()

    name = "url_encode"

    def filter(self, val):
        return urllib.parse.quote_plus(val)


class URLDecode(StringFilter):
    """Decodes a string that has been encoded as a URL."""

    __slots__ = ()

    name = "url_decode"

    def filter(self, val):
        return urllib.parse.unquote_plus(val)
