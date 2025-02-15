"""Tokenize liquid filtered expressions with optional inline conditions."""

import re
from typing import Iterator

from liquid.exceptions import LiquidSyntaxError
from liquid.expressions.common import GROUP_IDENTINDEX
from liquid.expressions.common import GROUP_IDENTQUOTED
from liquid.expressions.common import GROUP_QUOTED
from liquid.expressions.common import IDENTIFIER_PATTERN
from liquid.expressions.common import IDENTINDEX_PATTERN
from liquid.expressions.common import IDENTSTRING_PATTERN
from liquid.expressions.common import STRING_PATTERN
from liquid.expressions.common import Token
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_DPIPE
from liquid.token import TOKEN_ELSE
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_IDENTSTRING
from liquid.token import TOKEN_IF
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_NEWLINE
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_SKIP
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import operators

token_rules = (
    (TOKEN_IDENTINDEX, IDENTINDEX_PATTERN),
    (TOKEN_IDENTSTRING, IDENTSTRING_PATTERN),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_RANGE, r"\.\."),
    (TOKEN_FLOAT, r"-?\d+\.(?!\.)\d*"),
    (TOKEN_INTEGER, r"-?\d+\b"),
    (TOKEN_DOT, r"\."),
    (TOKEN_IDENTIFIER, IDENTIFIER_PATTERN),
    (TOKEN_LPAREN, r"\("),
    (TOKEN_RPAREN, r"\)"),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COMMA, r","),
    (TOKEN_COLON, r":"),
    (TOKEN_DPIPE, r"\|\|"),
    (TOKEN_PIPE, r"\|"),
    ("OP", r"[!=<>]{1,2}"),
    (TOKEN_NEWLINE, r"\n"),
    (TOKEN_SKIP, r"[ \t\r]+"),
    (TOKEN_ILLEGAL, r"."),
)

keywords = frozenset(
    [
        TOKEN_AND,
        TOKEN_BLANK,
        TOKEN_CONTAINS,
        TOKEN_ELSE,
        TOKEN_EMPTY,
        TOKEN_FALSE,
        TOKEN_IF,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_OR,
        TOKEN_TRUE,
    ]
)

# Rules including non-standard handling of parentheses.
paren_token_rules = (
    (TOKEN_RANGE_LITERAL, r"\((?=.+?\.\.)"),
    *token_rules,
)

# Keywords including the logical `not` operator.
not_keywords = frozenset(
    [
        TOKEN_NOT,
        *keywords,
    ]
)

OUTPUT_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_rules),
    re.DOTALL,
)

PAREN_TOKENS_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in paren_token_rules),
    re.DOTALL,
)


def tokenize(source: str, linenum: int = 1) -> Iterator[Token]:
    """Yield tokens from a conditional expression."""
    _keywords = keywords
    for match in OUTPUT_RE.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()
        newlines = value.count("\n")

        if kind == TOKEN_IDENTIFIER and value in _keywords:
            kind = value
        elif kind == TOKEN_IDENTINDEX:
            value = match.group(GROUP_IDENTINDEX)
        elif kind == TOKEN_IDENTSTRING:
            kind = TOKEN_IDENTIFIER
            value = match.group(GROUP_IDENTQUOTED)
        elif kind == TOKEN_STRING:
            value = match.group(GROUP_QUOTED)
        elif kind == "OP":
            try:
                kind = operators[value]
            except KeyError as err:
                raise LiquidSyntaxError(
                    f"unknown operator {value!r}",
                    linenum=linenum,
                ) from err
        elif kind == TOKEN_NEWLINE:
            linenum += 1
            continue
        elif kind == TOKEN_SKIP:
            continue
        elif kind == TOKEN_ILLEGAL:
            raise LiquidSyntaxError(f"unexpected {value!r}", linenum=linenum)

        linenum += newlines
        yield Token(linenum, kind, value)


def tokenize_with_parens(source: str, linenum: int = 1) -> Iterator[Token]:
    """Yield tokens from a conditional expression.

    This tokenizer includes extra tokens intended to distinguish the start of a range
    expression from the start of a logical group.
    """
    _keywords = not_keywords
    for match in PAREN_TOKENS_RE.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()
        newlines = value.count("\n")

        if kind == TOKEN_IDENTIFIER and value in _keywords:
            kind = value
        elif kind == TOKEN_RANGE_LITERAL:
            # Yield a TOKEN_RANGE_LITERAL, then yield a TOKEN_LPAREN
            # via the `yield` at the end of this loop.
            yield Token(linenum + newlines, kind, kind)
            kind = TOKEN_LPAREN
        elif kind == TOKEN_IDENTINDEX:
            value = match.group(GROUP_IDENTINDEX)
        elif kind == TOKEN_IDENTSTRING:
            kind = TOKEN_IDENTIFIER
            value = match.group(GROUP_IDENTQUOTED)
        elif kind == TOKEN_STRING:
            value = match.group(GROUP_QUOTED)
        elif kind == "OP":
            try:
                kind = operators[value]
            except KeyError as err:
                raise LiquidSyntaxError(
                    f"unknown operator {value!r}",
                    linenum=linenum,
                ) from err
        elif kind == TOKEN_NEWLINE:
            linenum += 1
            continue
        elif kind == TOKEN_SKIP:
            continue
        elif kind == TOKEN_ILLEGAL:
            raise LiquidSyntaxError(f"unexpected {value!r}", linenum=linenum)

        linenum += newlines
        yield Token(linenum, kind, value)
