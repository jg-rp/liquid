"""Filter functions that operate on strings."""
from __future__ import annotations

import base64
import binascii
import html
import re
import urllib.parse

from typing import Any
from typing import List
from typing import TYPE_CHECKING

try:
    from markupsafe import escape as markupsafe_escape
    from markupsafe import Markup
    from markupsafe import soft_str
except ImportError:
    from liquid.exceptions import escape as markupsafe_escape  # type: ignore
    from liquid.exceptions import Markup  # type: ignore

    # pylint: disable=invalid-name
    soft_str = str  # type: ignore

from liquid import is_undefined
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError

from liquid.filter import with_environment
from liquid.filter import string_filter

from liquid.utils.html import strip_tags
from liquid.utils.text import truncate_chars
from liquid.utils.text import truncate_words

if TYPE_CHECKING:
    from liquid import Environment


@string_filter
def append(val: str, arg: object) -> str:
    """Concatenate two strings."""
    if not isinstance(arg, str):
        arg = str(arg)
    return val + arg


@string_filter
def capitalize(val: str) -> str:
    """Make sure the first character of a string is upper case and the rest
    lowercase."""
    return val.capitalize()


@string_filter
def downcase(val: str) -> str:
    """Make all characters in a string lower case."""
    return val.lower()


@with_environment
@string_filter
def escape(val: str, *, environment: Environment) -> str:
    """Convert the characters &, < and > in string s to HTML-safe sequences."""
    if environment.autoescape:
        return markupsafe_escape(str(val))
    return html.escape(val)


@with_environment
@string_filter
def escape_once(val: str, *, environment: Environment) -> str:
    """Convert the characters &, < and > in string s to HTML-safe sequences."""
    if environment.autoescape:
        return Markup(val).unescape()
    return html.escape(html.unescape(val))


@string_filter
def lstrip(val: str) -> str:
    """Remove leading whitespace."""
    return val.lstrip()


RE_LINETERM = re.compile(r"\r?\n")


@with_environment
@string_filter
def newline_to_br(val: str, *, environment: Environment) -> str:
    """Convert '\r\n' or '\n' to '<br />\n'."""
    # The reference implementation was changed to replace "\r\n" as well as "\n",
    # but they don't seem to care about "\r" (Mac OS).
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("<br />\n", val))
    return RE_LINETERM.sub("<br />\n", val)


@string_filter
def prepend(val: str, arg: str) -> str:
    """Concatenate string value to argument string."""
    return soft_str(arg) + val


@string_filter
def remove(val: str, arg: str) -> str:
    """Remove all occurrences of argument string from value."""
    return val.replace(soft_str(arg), "")


@string_filter
def remove_first(val: str, arg: str) -> str:
    """Remove the first occurrences of the argument string from value."""
    return val.replace(soft_str(arg), "", 1)


@string_filter
def replace(val: str, seq: str, sub: str) -> str:
    """Replaces every occurrence of the first argument in a string with the second
    argument."""
    if is_undefined(seq):
        return sub

    return val.replace(soft_str(seq), soft_str(sub))


@string_filter
def replace_first(val: str, seq: str, sub: str) -> str:
    """Replaces the first occurrence of the first argument in a string with the second
    argument."""
    if is_undefined(seq):
        return sub

    return val.replace(soft_str(seq), soft_str(sub), 1)


@string_filter
def upcase(val: str) -> str:
    """Make all characters in a string upper case."""
    return val.upper()


@string_filter
def slice_(val: str, start: Any, length: int = 1) -> str:
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
def split(val: str, seq: str) -> List[str]:
    """Split a string into a list of string, using the argument as a delimiter."""
    if not seq:
        return list(val)

    return val.split(soft_str(seq))


@string_filter
def strip(val: str) -> str:
    """Remove leading and trailing whitespace."""
    return val.strip()


@string_filter
def rstrip(val: str) -> str:
    """Remove trailing whitespace."""
    return val.rstrip()


@with_environment
@string_filter
def strip_html(val: str, *, environment: Environment) -> str:
    """Return the given HTML with all HTML tags removed."""
    stripped = strip_tags(val)
    if environment.autoescape and isinstance(val, Markup):
        return Markup(stripped)
    return stripped


@with_environment
@string_filter
def strip_newlines(val: str, *, environment: Environment) -> str:
    """Return the given string with all newline characters removed."""
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("", val))
    return RE_LINETERM.sub("", val)


@string_filter
def truncate(val: str, num: Any, end: str = "...") -> str:
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
def truncatewords(val: str, num: Any, end: str = "...") -> str:
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
def url_encode(val: str, *, environment: Environment) -> str:
    """Percent encode a string so it is useable in a URL."""
    if environment.autoescape:
        return Markup(urllib.parse.quote_plus(val))
    return urllib.parse.quote_plus(val)


@string_filter
def url_decode(val: str) -> str:
    """Decode a string that has been URL encoded."""
    # Assuming URL decoded strings are all unsafe.
    return urllib.parse.unquote_plus(val)


@string_filter
def base64_encode(val: str) -> str:
    """Encode a string to base64."""
    return base64.b64encode(val.encode()).decode()


@string_filter
def base64_decode(val: str) -> str:
    """Decode a string from base64.

    The decoded value is assumed to be UTF-8 and will be decoded as UTF-8.
    """
    try:
        return base64.b64decode(val).decode()
    except binascii.Error as err:
        raise FilterValueError("Invalid base64-encoded string.") from err


@string_filter
def base64_url_safe_encode(val: str) -> str:
    """Encode a string to URL safe base64."""
    return base64.urlsafe_b64encode(val.encode()).decode()


@string_filter
def base64_url_safe_decode(val: str) -> str:
    """Decode a URL safe string from base64.

    The decoded value is assumed to be UTF-8 and will be decoded as UTF-8.
    """
    try:
        return base64.urlsafe_b64decode(val).decode()
    except binascii.Error as err:
        raise FilterValueError("Invalid base64-encoded string.") from err
