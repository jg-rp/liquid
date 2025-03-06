"""Tokenize a liquid expression."""

import re
import sys
from typing import Iterator

from liquid.exceptions import LiquidSyntaxError
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COLS
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_DPIPE
from liquid.token import TOKEN_ELSE
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_IDENTSTRING
from liquid.token import TOKEN_IF
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_REQUIRED
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_SKIP
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_WORD
from liquid.token import Token
from liquid.token import operators

GROUP_QUOTE = sys.intern("quote")
GROUP_QUOTED = sys.intern("quoted")
GROUP_IDENTINDEX = sys.intern("path_index")
GROUP_IDENTQUOTE = sys.intern("identquote")
GROUP_IDENTQUOTED = sys.intern("identquoted")

# The reference implementation will accept identifiers that start with an integer or
# hyphen when in lax mode, but will raise a syntax error in strict mode. For historic
# reasons we'll stick the following pattern until at least version 2 of Python Liquid.
IDENTIFIER_PATTERN = r"\w[\w\-]*\??"

# Trailing ? is not allowed in assignment names
ASSIGN_IDENTIFIER_PATTERN = r"\w[\w\-]*"

# ["ident"] or ['ident']
IDENTSTRING_PATTERN = (
    rf"\[\s*(?P<{GROUP_IDENTQUOTE}>[\"'])"
    rf"(?P<{GROUP_IDENTQUOTED}>.*?)"
    rf"(?P={GROUP_IDENTQUOTE})\s*]"
)

# [0] or [-1]
IDENTINDEX_PATTERN = rf"\[\s*(?P<{GROUP_IDENTINDEX}>\-?\d+)\s*]"

# 'something' or "something"
STRING_PATTERN = rf"(?P<{GROUP_QUOTE}>[\"'])(?P<{GROUP_QUOTED}>.*?)(?P={GROUP_QUOTE})"

# Rules for the standard boolean expression.
# Does not support grouping with parentheses.
_rules = (
    (TOKEN_RANGE_LITERAL, r"\((?=.+?\.\.)"),
    (TOKEN_IDENTINDEX, IDENTINDEX_PATTERN),
    (TOKEN_IDENTSTRING, IDENTSTRING_PATTERN),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_RANGE, r"\.\."),
    (TOKEN_FLOAT, r"-?\d+\.(?!\.)\d*"),
    (TOKEN_INTEGER, r"-?\d+\b"),
    (TOKEN_DOT, r"\."),
    (TOKEN_WORD, IDENTIFIER_PATTERN),
    (TOKEN_LPAREN, r"\("),
    (TOKEN_RPAREN, r"\)"),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    (TOKEN_COMMA, r","),
    (TOKEN_DPIPE, r"\|\|"),
    (TOKEN_PIPE, r"\|"),
    ("OP", r"[!=<>]{1,2}"),
    (TOKEN_SKIP, r"[ \n\t\r]+"),
    (TOKEN_ILLEGAL, r"."),
)

# Keywords for the standard boolean expression.
# Excludes `not`.
_keywords = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_EMPTY,
        TOKEN_BLANK,
        TOKEN_AND,
        TOKEN_OR,
        TOKEN_CONTAINS,
        TOKEN_NOT,
        TOKEN_IN,
        TOKEN_OFFSET,
        TOKEN_LIMIT,
        TOKEN_REVERSED,
        TOKEN_COLS,
        TOKEN_CONTINUE,
        TOKEN_WITH,
        TOKEN_FOR,
        TOKEN_AS,
        TOKEN_IF,
        TOKEN_ELSE,
        TOKEN_REQUIRED,
    ]
)

_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in _rules),
    re.DOTALL,
)


def tokenize(source: str, parent_token: Token) -> Iterator[Token]:
    """Tokenize a liquid expression."""
    for match in _RE.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()

        if kind == TOKEN_WORD and value in _keywords:
            kind = value
        elif kind == TOKEN_IDENTINDEX:
            value = match.group(GROUP_IDENTINDEX)
        elif kind == TOKEN_IDENTSTRING:
            value = match.group(GROUP_IDENTQUOTED)
        elif kind == TOKEN_STRING:
            value = match.group(GROUP_QUOTED)
        elif kind == "OP":
            try:
                kind = operators[value]
            except KeyError as err:
                raise LiquidSyntaxError(
                    f"unknown operator {value!r}",
                    token=Token(
                        kind,
                        value,
                        start_index=parent_token.start_index + match.start(),
                        source=parent_token.source,
                    ),
                ) from err
        elif kind == TOKEN_SKIP:
            continue
        elif kind == TOKEN_ILLEGAL:
            raise LiquidSyntaxError(
                f"unexpected {value!r}",
                token=Token(
                    kind,
                    value,
                    start_index=parent_token.start_index + match.start(),
                    source=parent_token.source,
                ),
            )

        yield Token(
            kind,
            value,
            start_index=parent_token.start_index + match.start(),
            source=parent_token.source,
        )
