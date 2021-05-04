"""Filter functions that operate on strings."""

import html
import re
import urllib.parse

try:
    from markupsafe import escape as markupsafe_escape
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import escape as markupsafe_escape  # type: ignore
    from liquid.exceptions import Markup  # type: ignore

from liquid import is_undefined
from liquid.exceptions import FilterArgumentError

from liquid.filter import with_environment
from liquid.filter import string_filter

from liquid.utils.html import strip_tags
from liquid.utils.text import truncate_chars
from liquid.utils.text import truncate_words


@string_filter
def append(val, arg):
    """Concatenate two strings."""
    if not isinstance(arg, str):
        arg = str(arg)
    return val + arg


@string_filter
def capitalize(val):
    """Make sure the first character of a string is upper case and the rest
    lowercase."""
    return val.capitalize()


@string_filter
def downcase(val):
    """Make all characters in a string lower case."""
    return val.lower()


@with_environment
@string_filter
def escape(val, *, environment):
    """Convert the characters &, < and > in string s to HTML-safe sequences."""
    if environment.autoescape:
        return markupsafe_escape(str(val))
    return html.escape(val)


@with_environment
@string_filter
def escape_once(val, *, environment):
    """Convert the characters &, < and > in string s to HTML-safe sequences."""
    if environment.autoescape:
        return Markup.unescape(val)
    return html.escape(html.unescape(val))


@string_filter
def lstrip(val):
    """Remove leading whitespace."""
    return val.lstrip()


RE_LINETERM = re.compile(r"\r?\n")


@with_environment
@string_filter
def newline_to_br(val, *, environment):
    """Convert '\r\n' or '\n' to '<br />\n'."""
    # The reference implementation was changed to replace "\r\n" as well as "\n",
    # but they don't seem to care about "\r" (Mac OS).
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("<br />\n", val))
    return RE_LINETERM.sub("<br />\n", val)


@string_filter
def prepend(val, arg):
    """Concatenate string value to argument string."""
    if not isinstance(arg, str):
        arg = str(arg)
    return arg + val


@string_filter
def remove(val, arg):
    """Remove all occurrences of argument string from value."""
    if not isinstance(arg, str):
        arg = str(arg)
    return val.replace(arg, "")


@string_filter
def remove_first(val, arg):
    """Remove the first occurrences of the argument string from value."""
    if not isinstance(arg, str):
        arg = str(arg)
    return val.replace(arg, "", 1)


@string_filter
def replace(val, seq, sub):
    """Replaces every occurrence of the first argument in a string with the second
    argument."""
    if not isinstance(sub, str):
        sub = str(sub)

    if is_undefined(seq):
        return sub

    if not isinstance(seq, str):
        seq = str(seq)

    return val.replace(seq, sub)


@string_filter
def replace_first(val, seq, sub):
    """Replaces the first occurrence of the first argument in a string with the second
    argument."""
    if not isinstance(sub, str):
        sub = str(sub)

    if is_undefined(seq):
        return sub

    if not isinstance(seq, str):
        seq = str(seq)

    return val.replace(seq, sub, 1)


@string_filter
def upcase(val):
    """Make all characters in a string upper case."""
    return val.upper()


@string_filter
def slice_(val, start, length=1):
    """Return a substring, starting at `start`, containing up to `length` characters."""
    if not val:
        return ""

    if is_undefined(start):
        raise FilterArgumentError("slice expected an integer, found Undefined")

    if is_undefined(length):
        length = 1

    try:
        start = int(start)
    except ValueError as err:
        raise FilterArgumentError(
            f"slice expected an integer, found {type(start).__name__}"
        ) from err

    try:
        length = int(length)
    except ValueError as err:
        raise FilterArgumentError(
            f"slice expected an integer, found {type(start).__name__}"
        ) from err

    if start > len(val) - 1:
        raise FilterArgumentError("slice string index out of range")

    return val[start : start + length]


@string_filter
def split(val, seq):
    """Split a string into a list of string, using the argument as a delimiter."""
    if not isinstance(seq, str):
        seq = str(seq)

    if not seq:
        return list(val)

    return val.split(seq)


@string_filter
def strip(val):
    """Remove leading and trailing whitespace."""
    return val.strip()


@string_filter
def rstrip(val):
    """Remove trailing whitespace."""
    return val.rstrip()


@with_environment
@string_filter
def strip_html(val, *, environment):
    """Return the given HTML with all HTML tags removed."""
    stripped = strip_tags(val)
    if environment.autoescape and isinstance(val, Markup):
        return Markup(stripped)
    return stripped


@with_environment
@string_filter
def strip_newlines(val, *, environment):
    """Return the given string with all newline characters removed."""
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("", val))
    return RE_LINETERM.sub("", val)


@string_filter
def truncate(val, num, end="..."):
    """Truncate a string if it is longer than the specified number of characters."""
    if is_undefined(num):
        raise FilterArgumentError("truncate expected an integer, found Undefined")

    try:
        num = int(num)
    except ValueError as err:
        raise FilterArgumentError(
            f"truncate expected an integer, found {type(num).__name__}"
        ) from err

    end = str(end)
    return truncate_chars(val, num, end)


@string_filter
def truncatewords(val, num, end="..."):
    """Shorten a string down to the given number of words."""
    if is_undefined(num):
        raise FilterArgumentError("truncate expected an integer, found Undefined")

    try:
        num = int(num)
    except ValueError as err:
        raise FilterArgumentError(
            f"truncate expected an integer, found {type(num).__name__}"
        ) from err

    end = str(end)

    # The reference implementation seems to force a minimum `num` of 1.
    if num <= 0:
        num = 1

    # Is truncating markup ever safe? Autoescape for now.
    return truncate_words(val, num, end)


@with_environment
@string_filter
def url_encode(val, *, environment):
    """Percent encode a string so it is useable in a URL."""
    if environment.autoescape:
        return Markup(urllib.parse.quote_plus(val))
    return urllib.parse.quote_plus(val)


@string_filter
def url_decode(val):
    """Decode a string that has been URL encoded."""
    # Assuming URL decoded strings are all unsafe.
    return urllib.parse.unquote_plus(val)
