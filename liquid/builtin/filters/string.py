"""Filter functions that operate on strings."""

from __future__ import annotations

import base64
import binascii
import html
import re
import urllib.parse
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import Union

from liquid import Markup
from liquid import escape as markupsafe_escape
from liquid import soft_str
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterError
from liquid.filter import liquid_filter
from liquid.filter import string_filter
from liquid.filter import with_environment
from liquid.limits import to_int
from liquid.undefined import Undefined
from liquid.undefined import is_undefined
from liquid.utils.html import strip_tags
from liquid.utils.text import truncate_chars

if TYPE_CHECKING:
    from liquid import Environment


@string_filter
def append(val: str, arg: object) -> str:
    """Return a copy of _val_ concatenated with _arg_.

    If _arg_ is not a string, it will be converted to one before concatenation.
    """
    if not isinstance(arg, str):
        arg = str(arg)
    return val + arg


@string_filter
def capitalize(val: str) -> str:
    """Return _val_ with the first character in uppercase and the rest lowercase."""
    return val.capitalize()


@string_filter
def downcase(val: str) -> str:
    """Return a copy of _val_ with all characters converted to lowercase."""
    return val.lower()


@with_environment
@string_filter
def escape(val: str, *, environment: Environment) -> str:
    """Return _val_ with the characters &, < and > converted to HTML-safe sequences."""
    if environment.autoescape:
        return markupsafe_escape(str(val))
    return html.escape(val)


@with_environment
@string_filter
def escape_once(val: str, *, environment: Environment) -> str:
    """Return _val_ with the characters &, < and > converted to HTML-safe sequences.

    It is safe to use `escape_one` on string values that already contain HTML escape
    sequences.
    """
    if environment.autoescape:
        return Markup(val).unescape()
    return html.escape(html.unescape(val))


@string_filter
def lstrip(val: str) -> str:
    """Return a copy of _val_ with leading whitespace removed."""
    return val.lstrip()


RE_LINETERM = re.compile(r"\r?\n")


@with_environment
@string_filter
def newline_to_br(val: str, *, environment: Environment) -> str:
    """Return a copy of _val_ with LF or CRLF converted to `<br />`, plus a newline."""
    # The reference implementation was changed to replace "\r\n" as well as "\n",
    # but they don't seem to care about "\r" (Mac OS).
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("<br />\n", val))
    return RE_LINETERM.sub("<br />\n", val)


@string_filter
def prepend(val: str, arg: str) -> str:
    """Return a copy of _arg_ concatenated with _val_."""
    return soft_str(arg) + val


@string_filter
def remove(val: str, arg: str) -> str:
    """Return a copy of _val_ with all occurrences of _arg_ removed."""
    return val.replace(soft_str(arg), "")


@string_filter
def remove_first(val: str, arg: str) -> str:
    """Return a copy of _val_ with the first occurrence of _arg_ removed."""
    return val.replace(soft_str(arg), "", 1)


@string_filter
def remove_last(val: str, arg: str) -> str:
    """Return a copy of _val_ with last occurrence of _arg_ removed."""
    try:
        before, _, after = val.rpartition(soft_str(arg))
    except ValueError:
        # empty separator
        return val
    if before:
        return before + after
    return val


@string_filter
def replace(val: str, seq: str, sub: str = "") -> str:
    """Return a copy of _val_ with each occurrence of _seq_ replaced with _sub_."""
    return val.replace(soft_str(seq), soft_str(sub))


@string_filter
def replace_first(val: str, seq: str, sub: str = "") -> str:
    """Return a copy of _val_ with the first occurrence of _seq_ replaced with _sub_."""
    return val.replace(soft_str(seq), soft_str(sub), 1)


@string_filter
def replace_last(val: str, seq: str, sub: str) -> str:
    """Return a copy of _val_ with the last occurrence of _seq_ replaced with _sub_."""
    try:
        before, _, after = val.rpartition(soft_str(seq))
    except ValueError:
        # empty separator
        return val + soft_str(sub)
    if before:
        return before + soft_str(sub) + after
    return val


@string_filter
def upcase(val: str) -> str:
    """Return a copy of _val_ with all characters converted to uppercase."""
    return val.upper()


MAX_SLICE_ARG = (1 << 63) - 1
MIN_SLICE_ARG = -(1 << 63)


def _slice_arg(val: Any) -> int:
    # The reference implementation does not cast floats to int.
    if isinstance(val, float):
        raise FilterArgumentError(
            f"slice expected an integer start, found {type(val).__name__}", token=None
        )

    try:
        rv = to_int(val)
    except (ValueError, TypeError) as err:
        raise FilterArgumentError(
            f"slice expected an integer start, found {type(val).__name__}", token=None
        ) from err

    rv = min(rv, MAX_SLICE_ARG)
    return max(rv, MIN_SLICE_ARG)


@liquid_filter
def slice_(val: Any, start: Any, length: Any = 1) -> Union[str, list[object]]:
    """Return the subsequence of _val_ starting at _start_ with up to _length_ chars.

    Array-like objects return a list, strings return a substring, all other objects are
    cast to a string before returning a substring.
    """
    if not isinstance(val, (list, tuple, range, str)):
        val = str(val)

    if is_undefined(start):
        raise FilterArgumentError(
            "slice expected an integer, found Undefined", token=None
        )

    if is_undefined(length):
        length = 1

    _start = _slice_arg(start)
    _length = _slice_arg(length)
    end: Optional[int] = _start + _length

    # A negative start index and a length that exceeds the theoretical length
    # of the sequence.
    if isinstance(end, int) and _start < 0 <= end:
        end = None

    if isinstance(val, str):
        return val[_start:end]
    return list(val[_start:end])


@string_filter
def split(val: str, sep: Any) -> list[str]:
    """Split string _val_ on delimiter _sep_.

    If _sep_ is empty or _undefined_, _val_ is split into a list of single
    characters. If _val_ is empty or equal to _sep_, an empty list is returned.
    """
    if isinstance(sep, Undefined):
        sep.poke()
        return list(val)

    if sep is None or sep == "":
        return list(val)

    sep = soft_str(sep)

    if not val or val == sep:
        return []

    return val.split(None if sep == " " else sep)


@string_filter
def strip(val: str) -> str:
    """Return a copy of _val_ with leading and trailing whitespace removed."""
    return val.strip()


@string_filter
def rstrip(val: str) -> str:
    """Return a copy of _val_ with trailing whitespace removed."""
    return val.rstrip()


@with_environment
@string_filter
def strip_html(val: str, *, environment: Environment) -> str:
    """Return a copy of _val_ with all HTML tags removed."""
    stripped = strip_tags(val)
    if environment.autoescape and isinstance(val, Markup):
        return Markup(stripped)
    return stripped


@with_environment
@string_filter
def strip_newlines(val: str, *, environment: Environment) -> str:
    """Return ta copy of _val_ with all newline characters removed."""
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("", val))
    return RE_LINETERM.sub("", val)


@string_filter
def truncate(val: str, num: Any = 50, end: str = "...") -> str:
    """Return a copy of _val_ truncated to _num_ characters."""
    if is_undefined(num):
        raise FilterArgumentError(
            "truncate expected an integer, found Undefined", token=None
        )

    try:
        num = to_int(num)
    except ValueError as err:
        raise FilterArgumentError(
            f"truncate expected an integer, found {type(num).__name__}", token=None
        ) from err

    end = str(end)
    return truncate_chars(val, num, end)


# Mimic reference implementation's limit to the number of words that can be truncated.
MAX_TRUNC_WORDS = (1 << 31) - 1


@string_filter
def truncatewords(val: str, num: Any = 15, end: str = "...") -> str:
    """Return a copy of _val_ truncated to at most _num_ words."""
    if is_undefined(num):
        raise FilterArgumentError(
            "truncate expected an integer, found Undefined", token=None
        )

    try:
        num = to_int(num)
    except ValueError as err:
        raise FilterArgumentError(
            f"truncate expected an integer, found {type(num).__name__}", token=None
        ) from err

    end = str(end)

    # The reference implementation seems to force a minimum `num` of 1.
    if num <= 0:
        num = 1

    # Replaces consecutive whitespace with a single newline.
    words = val.split()

    # This too mimics the reference implementation's big integer work around.
    if num >= MAX_TRUNC_WORDS:
        return val

    if len(words) < num:
        return " ".join(words)

    return " ".join(words[:num]) + end


@with_environment
@string_filter
def url_encode(val: str, *, environment: Environment) -> str:
    """Return a percent-encoded copy of _val_ so it is useable in a URL."""
    if environment.autoescape:
        return Markup(urllib.parse.quote_plus(val))
    return urllib.parse.quote_plus(val)


@string_filter
def url_decode(val: str) -> str:
    """Return a copy of _val_ after decoding percent-encoded sequences."""
    # Assuming URL decoded strings are all unsafe.
    return urllib.parse.unquote_plus(val)


@string_filter
def base64_encode(val: str) -> str:
    """Return _val_ encoded in base64."""
    return base64.b64encode(val.encode()).decode()


@string_filter
def base64_decode(val: str) -> str:
    """Return _val_ decoded as base64.

    The decoded value is assumed to be UTF-8 and will be decoded as UTF-8.
    """
    try:
        return base64.b64decode(val).decode()
    except binascii.Error as err:
        raise FilterError("invalid base64-encoded string", token=None) from err


@string_filter
def base64_url_safe_encode(val: str) -> str:
    """Return _val_ encoded in URL-safe base64."""
    return base64.urlsafe_b64encode(val.encode()).decode()


@string_filter
def base64_url_safe_decode(val: str) -> str:
    """Return _val_ decoded as URL-safe base64.

    The decoded value is assumed to be UTF-8 and will be decoded as UTF-8.
    """
    try:
        return base64.urlsafe_b64decode(val).decode()
    except binascii.Error as err:
        raise FilterError("invalid base64-encoded string", token=None) from err
