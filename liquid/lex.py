"""Tokenize Liquid templates and expressions."""

import re

from abc import ABC, abstractmethod
from functools import lru_cache, partial
from typing import Iterator, Tuple, Iterable, Collection

from liquid.exceptions import LiquidSyntaxError
from liquid.token import Token, operators

from liquid.token import (
    TOKEN_EOF,
    TOKEN_WHITESPACE_CONTROL,
    TOKEN_STRING,
    TOKEN_FLOAT,
    TOKEN_DOT,
    TOKEN_INTEGER,
    TOKEN_RANGE,
    TOKEN_IDENTIFIER,
    TOKEN_ILLEGAL,
    TOKEN_LITERAL,
    TOKEN_EXPRESSION,
    TOKEN_TAG_NAME,
    TOKEN_STATEMENT,
    TOKEN_NEWLINE,
    TOKEN_LBRACKET,
    TOKEN_RBRACKET,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_COLON,
    TOKEN_TRUE,
    TOKEN_FALSE,
    TOKEN_NIL,
    TOKEN_EMPTY,
    TOKEN_PIPE,
    TOKEN_NEGATIVE,
    TOKEN_COMMA,
    TOKEN_AND,
    TOKEN_OR,
    TOKEN_CONTAINS,
    TOKEN_WITH,
    TOKEN_FOR,
    TOKEN_AS,
    TOKEN_IN,
    TOKEN_OFFSET,
    TOKEN_LIMIT,
    TOKEN_REVERSED,
    TOKEN_COLS,
    TOKEN_BY,
    TOKEN_ASSIGN,
)


from liquid.pointer import Pointer
from liquid.stream import TokenStream


RE_WHITESPACE = re.compile(r"\s+")
RE_LINESPACE = re.compile(" \t")
RE_ENDOFLINE = re.compile("\n")
RE_ENDRAW = re.compile(r"{%-?\s*endraw\s*-?%}")


LIQUID_SPEC = [
    (TOKEN_STATEMENT, r"{{(?P<lstrip>-?)\s*(?P<stmt>.*?)\s*(?P<rstrip>-?)}}"),
    (
        TOKEN_STATEMENT,
        r"{%(?P<lstrip>-?)\s*(?P<name>\w+)\s*(?P<expr>.*?)\s*(?P<rstrip>-?)%}",
    ),
    (TOKEN_LITERAL, r".+?"),
]

IDENTIFIER_SPEC = [
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_STRING, r"(?P<quote>[\"'])(?P<quoted>.*?)(?P=quote)"),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_NEWLINE, r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
]

FILTERED_EXPRESSION_SPEC = [
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, r"(?P<quote>[\"'])(?P<quoted>.*?)(?P=quote)"),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_COMMA, r","),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    (TOKEN_PIPE, r"\|"),
    (TOKEN_NEWLINE, r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
]

FILTERED_EXPRESSION_KEYWORDS = {
    TOKEN_TRUE,
    TOKEN_FALSE,
    TOKEN_NIL,
    TOKEN_EMPTY,
}

ASSIGNMENT_EXPRESSION_SPEC = [
    (TOKEN_ASSIGN, r"="),
    *FILTERED_EXPRESSION_SPEC,
]

BOOLEAN_EXPRESSION_SPEC = [
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, r"(?P<quote>[\"'])(?P<quoted>.*?)(?P=quote)"),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-?]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    (TOKEN_NEWLINE, r"\n"),
    ("OP", r"[!=<>]{1,2}"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
]

BOOLEAN_EXPRESSION_KEYWORDS = {
    TOKEN_TRUE,
    TOKEN_FALSE,
    TOKEN_NIL,
    TOKEN_EMPTY,
    TOKEN_AND,
    TOKEN_OR,
    TOKEN_CONTAINS,
}

LOOP_EXPRESSION_SPEC = [
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-]*"),
    (TOKEN_RANGE, r"\.\."),
    (TOKEN_DOT, r"\."),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_LPAREN, r"\("),
    (TOKEN_RPAREN, r"\)"),
    (TOKEN_COLON, r":"),
    (TOKEN_NEWLINE, r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
]

LOOP_EXPRESSION_KEYWORDS = {
    TOKEN_IN,
    TOKEN_OFFSET,
    TOKEN_LIMIT,
    TOKEN_REVERSED,
    TOKEN_COLS,
}

INCLUDE_EXPRESSION_SPEC = [
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, r"(?P<quote>[\"'])(?P<quoted>.*?)(?P=quote)"),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-?]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_COMMA, r","),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    (TOKEN_NEWLINE, r"\n"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
]

INCLUDE_EXPRESSION_KEYWORDS = {
    TOKEN_TRUE,
    TOKEN_FALSE,
    TOKEN_NIL,
    TOKEN_EMPTY,
    TOKEN_WITH,
    TOKEN_FOR,
    TOKEN_AS,
}


def compile(spec: Iterable[Tuple[str, str]]):
    """"""
    pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in spec)
    return re.compile(pattern, re.DOTALL)


def tokenize(source: str, spec: re.Pattern, keywords: Collection[str]) -> Iterator:
    line_num = 1

    for match in spec.finditer(source):
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
        elif kind == TOKEN_NEWLINE:
            line_num += 1
            continue
        elif kind == "SKIP":
            continue
        elif kind == TOKEN_ILLEGAL:
            raise LiquidSyntaxError(f"unexpected {value!r}", linenum=line_num)
        yield Token(line_num, kind, value)


tokenize_identifier = partial(
    tokenize,
    spec=compile(IDENTIFIER_SPEC),
    keywords=(),
)

tokenize_loop_expression = partial(
    tokenize,
    spec=compile(LOOP_EXPRESSION_SPEC),
    keywords=LOOP_EXPRESSION_KEYWORDS,
)


tokenize_filtered_expression = partial(
    tokenize,
    spec=compile(FILTERED_EXPRESSION_SPEC),
    keywords=FILTERED_EXPRESSION_KEYWORDS,
)

tokenize_assignment_expression = partial(
    tokenize,
    spec=compile(ASSIGNMENT_EXPRESSION_SPEC),
    keywords=FILTERED_EXPRESSION_KEYWORDS,
)

tokenize_boolean_expression = partial(
    tokenize,
    spec=compile(BOOLEAN_EXPRESSION_SPEC),
    keywords=BOOLEAN_EXPRESSION_KEYWORDS,
)

tokenize_include_expression = partial(
    tokenize,
    spec=compile(INCLUDE_EXPRESSION_SPEC),
    keywords=INCLUDE_EXPRESSION_KEYWORDS,
)

tokenize_paginate_expression = partial(
    tokenize,
    spec=compile(IDENTIFIER_SPEC),
    keywords={TOKEN_BY},
)


LIQUID_SPEC = [
    ("RAW", r"{%\s*raw\s*%}(?P<raw>.*?){%\s*endraw\s*%}"),
    (TOKEN_STATEMENT, r"{{-?\s*(?P<stmt>.*?)\s*(?P<rss>-?)}}"),
    # The "name" group is zero or more characters so that a malformed tag (one
    # with not name) does not get treated as a literal.
    ("TAG", r"{%-?\s*(?P<name>\w*)\s*(?P<expr>.*?)\s*(?P<rst>-?)%}"),
    (TOKEN_LITERAL, r".+?(?=({[{%](?P<rstrip>-?))|$)"),
]


RE_LIQUID_SPEC = compile(LIQUID_SPEC)


def tokenize_liquid(source: str) -> Iterator:
    line_count = 1
    lstrip = False

    for match in RE_LIQUID_SPEC.finditer(source):
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
            yield Token(line_num, TOKEN_TAG_NAME, name)

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

            if value.startswith(r"{{") or value.startswith(r"{%"):
                raise LiquidSyntaxError("unbalanced tokens")

        yield Token(line_num, kind, value)


class Lexer(ABC):
    """Base lexer."""

    def __init__(self, env):
        self.env = env

    def tokenize(self, source: str) -> TokenStream:
        """Build a stream of tokens from a source string."""
        return TokenStream(self.tokeniter(source))

    @abstractmethod
    def tokeniter(self, source: str, linenum: int = 0) -> Iterator[Token]:
        """Return a generator over tokens in the source string."""


class LiquidLexer:
    """Tokenize "liquid" tag expressions.

    See https://shopify.dev/docs/themes/liquid/reference/tags/theme-tags#liquid
    """

    def __init__(self, env):
        # FIXME: Whitepace control.
        self.tag_name_end_re = re.compile(fr"\s|{re.escape(env.tag_end_string)}")

    def tokenize(self, source):
        return TokenStream(self.tokeniter(source))

    def tokeniter(self, source: str, linenum: int = 1) -> Iterator[Token]:
        ptr = Pointer(source, linenum=linenum)
        while ptr.ch != TOKEN_EOF:
            yield from self._tokenize(ptr)

    def _tokenize(self, ptr) -> Iterator[Token]:
        linenum = ptr.linecount

        # Each line starts with a tag name
        name = self.read_tag_name(ptr)
        yield Token(linenum, TOKEN_TAG_NAME, name)

        # With zero or more space or tab characters
        ptr.eat(RE_LINESPACE)

        # Optionally followed by an expression
        expr = self._read_line_expression(ptr).strip()
        if expr:
            yield Token(linenum, TOKEN_EXPRESSION, expr)

    def _read_line_expression(self, ptr) -> str:
        """Return all characters up to the next newline"""
        idx = ptr.idx
        ptr.jump_to_pattern(RE_ENDOFLINE, or_eof=False)
        return ptr.source[idx : ptr.idx]

    def read_tag_name(self, ptr: Pointer) -> str:
        """Return all characters up to the next whitespace."""
        ptr.eat(RE_WHITESPACE)
        idx = ptr.idx
        ptr.jump_to_pattern(self.tag_name_end_re)
        tag_name = ptr.source[idx : ptr.idx]
        return tag_name


@lru_cache
def get_liquid_lexer(env):
    """Return a "liquid" tag lexer for the given environment."""
    return LiquidLexer(env)
