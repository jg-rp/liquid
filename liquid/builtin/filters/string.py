# type: ignore
"""Legacy, class-based implementations of filters that operate on strings."""

import html
import re
import urllib.parse

try:
    from markupsafe import escape as markupsafe_escape
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import escape as markupsafe_escape
    from liquid.exceptions import Markup

from liquid import is_undefined

from liquid.filter import Filter
from liquid.filter import one_maybe_two_args
from liquid.filter import expect_integer
from liquid.filter import expect_string

from liquid.exceptions import FilterArgumentError
from liquid.utils.html import strip_tags

from liquid.utils.text import truncate_chars
from liquid.utils.text import truncate_words

# pylint: disable=too-few-public-methods arguments-differ


class StringFilter(Filter):
    """A `Filter` subclass that ensures a filter's left value is a string and checks
    the number of arguments against `num_args` before delegating to its `filter`
    method."""

    __slots__ = ()

    name = "AbstractStringFilter"
    num_args = 0
    msg = "{}: expected a string, found {}"

    def __call__(self, val, *args, **kwargs):
        if len(args) != self.num_args:
            raise FilterArgumentError(
                f"{self.name}: expected {self.num_args} arguments, found {len(args)}"
            )

        if not isinstance(val, str):
            val = str(val)

        try:
            return self.filter(val, *args, **kwargs)
        except (AttributeError, TypeError) as err:
            raise FilterArgumentError(
                self.msg.format(self.name, type(val).__name__)
            ) from err

    def filter(self, val, *args, **kwargs):
        """Subclasses of :class:`StringFilter` should implement `filter`."""
        raise NotImplementedError(":(")


class Capitalize(StringFilter):
    """Make sure the first character of a string is upper case."""

    __slots__ = ()

    name = "capitalize"

    def filter(self, val, *args, **kwargs):
        return val.capitalize()


class Append(StringFilter):
    """Concatenate two strings."""

    __slots__ = ()

    name = "append"
    num_args = 1

    def filter(self, val: str, string: str):
        if not isinstance(string, str):
            string = str(string)
        return val + string


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
        if self.env.autoescape:
            return markupsafe_escape(str(val))
        return html.escape(val)


class EscapeOnce(StringFilter):
    """Convert the characters &, < and > in string s to HTML-safe sequences."""

    __slots__ = ()

    name = "escape_once"

    def filter(self, val):
        if self.env.autoescape:
            return Markup.unescape(val)
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
        if self.env.autoescape:
            val = markupsafe_escape(val)
            return Markup(self.re_lineterm.sub("<br />\n", val))
        return self.re_lineterm.sub("<br />\n", val)


class Prepend(StringFilter):
    """Concatenate string value to argument string."""

    __slots__ = ()

    name = "prepend"
    num_args = 1

    def filter(self, val, string):
        if not isinstance(string, str):
            string = str(string)
        return string + val


class Remove(StringFilter):
    """Remove all occurrences of argument string from value."""

    __slots__ = ()

    name = "remove"
    num_args = 1

    def filter(self, val, sub):
        if not isinstance(sub, str):
            sub = str(sub)
        return val.replace(sub, "")


class RemoveFirst(StringFilter):
    """Remove the first occurrences of the argument string from value."""

    __slots__ = ()

    name = "remove_first"
    num_args = 1

    def filter(self, val, sub):
        if not isinstance(sub, str):
            sub = str(sub)
        return val.replace(sub, "", 1)


class Replace(StringFilter):
    """Replace all occurrences of argument string in value."""

    __slots__ = ()

    name = "replace"
    num_args = 2

    def filter(self, val, seq, sub):
        if not isinstance(sub, str):
            sub = str(sub)

        if is_undefined(seq):
            return sub

        if not isinstance(seq, str):
            seq = str(seq)

        return val.replace(seq, sub)


class ReplaceFirst(StringFilter):
    """Replace the first occurrences of the argument string in value."""

    __slots__ = ()

    name = "replace_first"
    num_args = 2

    def filter(self, val, seq, sub):
        if not isinstance(sub, str):
            sub = str(sub)

        if is_undefined(seq):
            return sub

        if not isinstance(seq, str):
            seq = str(seq)

        return val.replace(seq, sub, 1)


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

    def __call__(self, val, *args, **kwargs):
        if is_undefined(val):
            return ""

        if not isinstance(val, str):
            val = str(val)

        start, length = one_maybe_two_args(self.name, args, kwargs)
        expect_integer(self.name, start)

        if length is not None:
            if is_undefined(length):
                length = 1
            else:
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
        if not isinstance(seq, str):
            seq = str(seq)

        if not seq:
            return list(val)

        return val.split(seq)


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
        stripped = strip_tags(val)
        if self.env.autoescape and isinstance(val, Markup):
            return Markup(stripped)
        return stripped


class StripNewlines(StringFilter):
    """Return the given string with all newline characters removed."""

    __slots__ = ()

    name = "strip_newlines"
    re_lineterm = re.compile(r"\r?\n")

    def filter(self, val):
        if self.env.autoescape:
            val = markupsafe_escape(val)
            return Markup(self.re_lineterm.sub("", val))
        return self.re_lineterm.sub("", val)


class Truncate(Filter):
    """Truncates a string if it is longer than the specified number of characters."""

    __slots__ = ()

    name = "truncate"

    def __call__(self, val, *args, **kwargs):
        if is_undefined(val):
            return ""

        val = str(val)
        num, end = one_maybe_two_args(self.name, args, kwargs)
        expect_integer(self.name, num)

        if end is not None:
            if is_undefined(end):
                end = ""
            else:
                expect_string(self.name, end)
        else:
            end = "..."

        # XXX: Is truncating markup ever safe? Autoescape for now.
        return truncate_chars(val, num, end)


class TruncateWords(Filter):
    """Shortens a string down to the number of words passed as an argument."""

    __slots__ = ()

    name = "truncatewords"

    def __call__(self, val, *args, **kwargs):
        if is_undefined(val):
            return ""

        val = str(val)
        num, end = one_maybe_two_args(self.name, args, kwargs)
        expect_integer(self.name, num)

        if end is not None:
            if is_undefined(end):
                end = ""
            else:
                end = str(end)
        else:
            end = "..."

        # The reference implementation seems to force a minimum `num` of 1.
        if num <= 0:
            num = 1

        # XXX: Is truncating markup ever safe? Autoescape for now.
        return truncate_words(val, num, end)


class URLEncode(StringFilter):
    """Converts any URL-unsafe characters in a string into percent-encoded
    characters."""

    __slots__ = ()

    name = "url_encode"

    def filter(self, val):
        if self.env.autoescape:
            return Markup(urllib.parse.quote_plus(val))
        return urllib.parse.quote_plus(val)


class URLDecode(StringFilter):
    """Decodes a string that has been encoded as a URL."""

    __slots__ = ()

    name = "url_decode"

    def filter(self, val):
        # XXX: Assuming URL decoded strings are all unsafe.
        return urllib.parse.unquote_plus(val)
