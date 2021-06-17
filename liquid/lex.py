"""Tokenize Liquid templates and expressions.

The template lexer generates a stream of template literals, tags, output statements and
expressions, where each expression token is an unscanned string. Lexing of expression
tokens is delegated to the "parse" method of each registered Tag.
"""

from __future__ import annotations
import re

from functools import lru_cache
from functools import partial

from typing import Iterator
from typing import Tuple
from typing import Iterable
from typing import Collection
from typing import Pattern
from typing import Callable

from liquid.exceptions import LiquidSyntaxError

from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_STATEMENT
from liquid.token import TOKEN_LITERAL
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_WITH
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_BY
from liquid.token import TOKEN_NEGATIVE
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_COLS
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_ASSIGN
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_OR
from liquid.token import operators
from liquid.token import Token


__all__ = (
    "tokenize_assignment_expression",
    "tokenize_boolean_expression",
    "tokenize_filtered_expression",
    "tokenize_loop_expression",
    "tokenize_identifier",
    "tokenize_include_expression",
    "tokenize_paginate_expression",
    "tokenize_liquid_expression",
    "get_lexer",
)

IDENTIFIER_PATTERN = r"\w[a-zA-Z0-9_\-]*"
STRING_PATTERN = r"(?P<quote>[\"'])(?P<quoted>.*?)(?P=quote)"

identifier_rules = (
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_IDENTIFIER, IDENTIFIER_PATTERN),
    (TOKEN_DOT, r"\."),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)

filtered_expression_rules = (
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_IDENTIFIER, IDENTIFIER_PATTERN),
    (TOKEN_DOT, r"\."),
    (TOKEN_COMMA, r","),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    (TOKEN_PIPE, r"\|"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)

filtered_expression_keywords = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_EMPTY,
        TOKEN_BLANK,
    ]
)

assignment_expression_rules = (
    (TOKEN_ASSIGN, r"="),
    *filtered_expression_rules,
)

boolean_expression_rules = (
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-?]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    ("NEWLINE", r"\n"),
    ("OP", r"[!=<>]{1,2}"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)

boolean_expression_keywords = frozenset(
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
    ]
)

loop_expression_rules = (
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_IDENTIFIER, IDENTIFIER_PATTERN),
    (TOKEN_RANGE, r"\.\."),
    (TOKEN_DOT, r"\."),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_LPAREN, r"\("),
    (TOKEN_RPAREN, r"\)"),
    (TOKEN_COLON, r":"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)

loop_expression_keywords = frozenset(
    [
        TOKEN_IN,
        TOKEN_OFFSET,
        TOKEN_LIMIT,
        TOKEN_REVERSED,
        TOKEN_COLS,
        TOKEN_CONTINUE,
    ]
)

include_expression_rules = (
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-?]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_COMMA, r","),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)

include_expression_keywords = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_EMPTY,
        TOKEN_BLANK,
        TOKEN_WITH,
        TOKEN_FOR,
        TOKEN_AS,
    ]
)


def compile_liquid_rules(
    tag_start_string: str = r"{%",
    tag_end_string: str = r"%}",
    statement_start_string: str = r"{{",
    statement_end_string: str = r"}}",
) -> Pattern[str]:
    """Compile rules for lexing liquid templates."""
    tag_s = re.escape(tag_start_string)
    tag_e = re.escape(tag_end_string)
    stmt_s = re.escape(statement_start_string)
    stmt_e = re.escape(statement_end_string)

    liquid_rules = [
        ("RAW", rf"{tag_s}\s*raw\s*{tag_e}(?P<raw>.*?){tag_s}\s*endraw\s*{tag_e}"),
        (TOKEN_STATEMENT, rf"{stmt_s}-?\s*(?P<stmt>.*?)\s*(?P<rss>-?){stmt_e}"),
        # The "name" group is zero or more characters so that a malformed tag (one
        # with no name) does not get treated as a literal.
        ("TAG", rf"{tag_s}-?\s*(?P<name>\w*)\s*(?P<expr>.*?)\s*(?P<rst>-?){tag_e}"),
        (TOKEN_LITERAL, rf".+?(?=(({tag_s}|{stmt_s})(?P<rstrip>-?))|$)"),
    ]

    return _compile_rules(liquid_rules)


def _compile_rules(rules: Iterable[Tuple[str, str]]) -> Pattern[str]:
    """Compile the given rules into a single regular expression."""
    pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in rules)
    return re.compile(pattern, re.DOTALL)


# NOTE: Here we're talking about the expression found in "liquid" tags only.
# Each line starts with a tag name, optionally followed by zero or more space
# or tab characters and an expression, which is terminated by a newline.
LIQUID_EXPRESSION_RE = re.compile(r"[ \t]*(?P<name>\w+)[ \t]*(?P<expr>.*)[ \t]*?(\n|$)")


def tokenize_liquid_expression(source: str) -> Iterator[Token]:
    """Tokenize a "liquid" tag expression."""
    line_count = 1

    for match in LIQUID_EXPRESSION_RE.finditer(source):

        line_num = line_count
        value = match.group()
        line_count += value.count("\n")

        yield Token(line_num, TOKEN_TAG, match.group("name"))

        if match.group("expr"):
            yield Token(line_num, TOKEN_EXPRESSION, match.group("expr"))


def _tokenize(
    source: str, rules: Pattern[str], keywords: Collection[str]
) -> Iterator[Token]:
    """Generate tokens from the given source string according to the compiled rules."""
    line_num = 1

    for match in rules.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()

        if kind == TOKEN_IDENTIFIER and value in keywords:
            kind = value

        elif kind == TOKEN_STRING:
            value = match.group("quoted")

        elif kind == "OP":
            try:
                kind = operators[value]
            except KeyError as err:
                raise LiquidSyntaxError(
                    f"unknown operator {value!r}",
                    linenum=line_num,
                ) from err

        elif kind == "NEWLINE":
            line_num += 1
            continue

        elif kind == "SKIP":
            continue

        elif kind == TOKEN_ILLEGAL:
            raise LiquidSyntaxError(f"unexpected {value!r}", linenum=line_num)

        yield Token(line_num, kind, value)


tokenize_identifier = partial(
    _tokenize,
    rules=_compile_rules(identifier_rules),
    keywords=(),
)

tokenize_loop_expression = partial(
    _tokenize,
    rules=_compile_rules(loop_expression_rules),
    keywords=loop_expression_keywords,
)

tokenize_filtered_expression = partial(
    _tokenize,
    rules=_compile_rules(filtered_expression_rules),
    keywords=filtered_expression_keywords,
)

tokenize_assignment_expression = partial(
    _tokenize,
    rules=_compile_rules(assignment_expression_rules),
    keywords=filtered_expression_keywords,
)

tokenize_boolean_expression = partial(
    _tokenize,
    rules=_compile_rules(boolean_expression_rules),
    keywords=boolean_expression_keywords,
)

tokenize_include_expression = partial(
    _tokenize,
    rules=_compile_rules(include_expression_rules),
    keywords=include_expression_keywords,
)

tokenize_paginate_expression = partial(
    _tokenize,
    rules=_compile_rules(identifier_rules),
    keywords={TOKEN_BY},
)


def _tokenize_template(source: str, rules: Pattern[str]) -> Iterator[Token]:
    line_count = 1
    lstrip = False

    for match in rules.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        line_num = line_count
        value = match.group()
        line_count += value.count("\n")

        if kind == TOKEN_STATEMENT:
            value = match.group("stmt")
            lstrip = bool(match.group("rss"))

        elif kind == "TAG":
            name = match.group("name")
            yield Token(line_num, TOKEN_TAG, name)

            kind = TOKEN_EXPRESSION
            value = match.group("expr")
            lstrip = bool(match.group("rst"))

            if not value:
                continue

        elif kind == "RAW":
            kind = TOKEN_LITERAL
            value = match.group("raw")

        elif kind == TOKEN_LITERAL:
            if lstrip:
                value = value.lstrip()
            if match.group("rstrip"):
                value = value.rstrip()

            if not value:
                continue

            if value.startswith(r"{{"):
                raise LiquidSyntaxError(
                    "expected '}}', found 'eof'", linenum=line_count
                )
            if value.startswith(r"{%"):
                raise LiquidSyntaxError(
                    "expected '%}', found 'eof'", linenum=line_count
                )

        yield Token(line_num, kind, value)


@lru_cache(maxsize=128)
def get_lexer(
    tag_start_string: str = r"{%",
    tag_end_string: str = r"%}",
    statement_start_string: str = r"{{",
    statement_end_string: str = r"}}",
) -> Callable[[str], Iterator[Token]]:
    """Return a template lexer using the given tag and statement delimiters."""
    rules = compile_liquid_rules(
        tag_start_string,
        tag_end_string,
        statement_start_string,
        statement_end_string,
    )
    return partial(_tokenize_template, rules=rules)
