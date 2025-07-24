"""Filters that don't exist in the reference implementation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from liquid import Markup
from liquid.filter import string_filter
from liquid.filter import with_environment

if TYPE_CHECKING:
    from liquid import Environment


@with_environment
@string_filter
def safe(val: str, *, environment: Environment) -> str:
    """Return a copy of _val_ that will not be automatically HTML escaped on output."""
    if environment.autoescape:
        return Markup(val)
    return val


# `escapejs` is inspired by https://github.com/salesforce/secure-filters and Django's
# escapejs, https://github.com/django/django/blob/485f483d49144a2ea5401442bc3b937a370b3ca6/django/utils/html.py#L63

_ESCAPE_MAP = {
    "\\": "\\u005C",
    "'": "\\u0027",
    '"': "\\u0022",
    ">": "\\u003E",
    "<": "\\u003C",
    "&": "\\u0026",
    "=": "\\u003D",
    "-": "\\u002D",
    ";": "\\u003B",
    "`": "\\u0060",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}

_ESCAPE_MAP.update({chr(c): f"\\u{c:04X}" for c in range(32)})
_ESCAPE_RE = re.compile("[" + re.escape("".join(_ESCAPE_MAP.keys())) + "]")


@string_filter
def escapejs(val: str) -> str:
    """Escape characters for safe use in JavaScript string literals.

    This filter escapes a string for embedding inside **JavaScript string
    literals**, using either single or double quotes (e.g. `'...'` or `"..."`).
    It replaces control characters and potentially dangerous symbols with
    their corresponding Unicode escape sequences.

    **Important:** This filter does **not** make strings safe for use in
    JavaScript template literals (backtick strings), or in raw JavaScript
    expressions. Use it only when placing data inside quoted JS strings
    within inline `<script>` blocks or event handlers.

    **Recommended alternatives:**
        - Pass data using HTML `data-*` attributes and read them in JS via
          `element.dataset`.
        - For structured data, prefer a JSON-serialization approach using the
          JSON filter.

    Escaped characters include:
        - ASCII control characters (U+0000 to U+001F)
        - Characters like quotes, angle brackets, ampersands, equals signs
        - Line/paragraph separators (U+2028, U+2029)

    Args:
        val: The input string to escape.

    Returns:
        A JavaScript-safe string, with problematic characters escaped as Unicode.
    """
    return _ESCAPE_RE.sub(lambda m: _ESCAPE_MAP[m.group()], val)
