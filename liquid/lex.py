"""Tokenize Liquid templates and expressions."""

import re
import sys

from abc import ABC, abstractmethod
from enum import IntEnum
from functools import lru_cache
from typing import Iterator, Tuple, NamedTuple

from liquid.exceptions import LiquidSyntaxError
from liquid.token import Token, keywords, operators, reverse_operators
from liquid.token import (
    WHITESPACE,
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
)


from liquid.pointer import Pointer
from liquid.stream import TokenStream

ENDIDENTIFIER = frozenset(".[:)],") | WHITESPACE

RE_DIGITS = re.compile(r"\d+")
RE_ENDIDENTIFIER = re.compile("|".join(re.escape(c) for c in ENDIDENTIFIER))
RE_WHITESPACE = re.compile(r"\s+")
RE_LINESPACE = re.compile(" \t")
RE_ENDOFLINE = re.compile("\n")
RE_QUOTE = re.compile("\"|'")
RE_ENDRAW = re.compile(r"{%-?\s*endraw\s*-?%}")


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


class TemplateLexer(Lexer):
    """Liquid template lexer.

    Tokenize template strings. Output statements and tag expression do not
    get tokenized here. Each tag's parse method is responsible for lexing and
    parings their own expression.
    """

    def __init__(self, env):
        super().__init__(env)
        self.tag_start_re = re.compile(fr"{re.escape(env.tag_start_string)}-?")
        self.tag_end_re = re.compile(fr"-?{re.escape(env.tag_end_string)}")

        self.statement_start_re = re.compile(
            f"{re.escape(env.statement_start_string)}-?"
        )
        self.statement_end_re = re.compile(fr"-?{re.escape(env.statement_end_string)}")

        self.literal_end_re = re.compile(
            fr"({re.escape(env.tag_start_string)}|{re.escape(env.statement_start_string)})-?"
        )

        self.tag_or_statement_end_re = re.compile(
            fr"-?({re.escape(env.tag_end_string)}|{re.escape(env.statement_end_string)})"
        )

        # FIXME: Whitepace control.
        self.tag_name_end_re = re.compile(fr"\s|{re.escape(env.tag_end_string)}")

    def tokeniter(self, source: str, linenum: int = 1) -> Iterator[Token]:
        ptr = Pointer(source, linenum)
        while ptr.ch != TOKEN_EOF:
            yield from self._tokeniter(ptr)

        yield Token(ptr.linenum, TOKEN_EOF, "")

    def _tokeniter(self, ptr: Pointer) -> Iterator[Token]:
        # Remember the starting line number, just in case a tag/statement
        # covers multiple lines.
        # FIXME: Line numbers can change between eats and reads
        linenum = ptr.linecount
        ptr.linenum = linenum

        if ptr.at_pattern(self.statement_start_re):
            # The start of an output statement.

            # Eat the start statement sequence (traditionally "{{") and any
            # whitespace control character. Preceding tokens will have read
            # ahead to inspect whitepsace control and right-stripped
            # accordingly.
            ptr.eat(self.statement_start_re)

            # Read the statement expression. That's everything up to the next
            # end statement sequence, including filters and filter arguments.
            # Expression lexing is left up to the `Statement` pseudo tag in its
            # `parse` method.
            expr = self.read_statement(ptr).strip()

            # Eat the end statement sequence (traditionally "}}") and check to
            # see if someone forgot to end their output statement.`eat_end`
            # will strip upcoming whitespace if the control character is set.
            if (end := self.eat_end(ptr)) != self.env.statement_end_string:
                raise LiquidSyntaxError(
                    f"expected '{self.env.statement_end_string}', found '{end}'",
                    linenum=linenum,
                )

            yield Token(linenum, TOKEN_STATEMENT, expr)

        elif ptr.at_pattern(self.tag_start_re):
            # The start of a tag. Could be the start or end of a tag block, or
            # non-block tag.

            # Eat the start tag sequence (traditionally "{%") and any whitespace
            # control character.
            ptr.eat(self.tag_start_re)

            # Every tag starts with a name, terminated by whitespace or an end
            # tag sequence.
            name = self.read_tag_name(ptr)
            yield Token(linenum, TOKEN_TAG_NAME, sys.intern(name))

            # Everything between the tag name and end tag sequence is the tag's
            # expression, which is possibly empty. Lexing of tag expressions
            # happens in the `parse` method of the tag definition class.
            if expr := self.read_tag(ptr).strip():
                yield Token(linenum, TOKEN_EXPRESSION, expr)

            # Eat the end tag sequence (traditionally "%}") and check to see if
            # someone forgot to close their tag.
            if (end := self.eat_end(ptr)) != self.env.tag_end_string:
                raise LiquidSyntaxError(
                    f"expected '{self.env.tag_end_string}', found '{end}'",
                    linenum=linenum,
                )

            # Special case for "raw" tags. Treat everything up to the next "ENDRAW"
            # tag as a template literal.
            if name == "raw":
                val = self.read_raw(ptr)
                yield Token(linenum, TOKEN_LITERAL, val)

        else:
            # A template literal. Thats anything that is not inside an output
            # statement or tag. Other than controlling leading or trailing
            # whitespace, template literals are passed through unchanged.
            val, rstrip = self.read_literal(ptr)
            if rstrip:
                val = val.rstrip()
            yield Token(linenum, TOKEN_LITERAL, val)

    def read_raw(self, ptr: Pointer) -> str:
        """Return all characters up to the next ENDRAW tag."""
        idx = ptr.idx
        ptr.jump_to_pattern(RE_ENDRAW)
        return ptr.source[idx : ptr.idx]

    def read_tag_name(self, ptr: Pointer) -> str:
        """Return all characters up to the next whitespace."""
        ptr.eat(RE_WHITESPACE)
        idx = ptr.idx
        ptr.jump_to_pattern(self.tag_name_end_re)
        tag_name = ptr.source[idx : ptr.idx]
        return tag_name

    def read_tag(self, ptr: Pointer) -> str:
        """Return all characters up to the next tag_end_String."""
        idx = ptr.idx
        ptr.jump_to_pattern(self.tag_end_re)
        return ptr.source[idx : ptr.idx]

    def read_statement(self, ptr: Pointer) -> str:
        """Read an output statement expression from the pointer's current position."""
        idx = ptr.idx
        ptr.jump_to_pattern(self.statement_end_re)
        return ptr.source[idx : ptr.idx]

    def read_literal(self, ptr: Pointer) -> Tuple[str, bool]:
        """Return all characters up to the next tag or statement and an rstrip flag."""
        idx = ptr.idx
        match = ptr.jump_to_pattern(self.literal_end_re)

        strip = self.env.strip_tags or match.endswith(TOKEN_WHITESPACE_CONTROL)
        return ptr.source[idx : ptr.idx], strip

    def eat_end(self, ptr: Pointer) -> str:
        """Advance the lexer passed the current end tag or end statement
        characters.

        Strips trailing whitespace if the end tag or statement starts with a
        whitespace control character.

        Returns the matched end tag/statement characters.
        """
        match = ptr.eat(self.tag_or_statement_end_re)

        if not match:
            return TOKEN_EOF

        if self.env.strip_tags or match.startswith(TOKEN_WHITESPACE_CONTROL):
            ptr.eat(RE_WHITESPACE)
            match = match[1:]

        return match


class LiquidLexer(TemplateLexer):
    """Tokenize "liquid" tag expressions.

    See https://shopify.dev/docs/themes/liquid/reference/tags/theme-tags#liquid
    """

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


class ExpressionLexer(Lexer):
    """Tokenize tag or output statement expressions."""

    def tokeniter(self, source: str, linenum: int = 1) -> Iterator[Token]:
        ptr = Pointer(source, linenum=linenum)

        while ptr.ch != TOKEN_EOF:
            ptr.eat(RE_WHITESPACE)
            yield from self._tokeniter(ptr)

        yield Token(ptr.linecount, TOKEN_EOF, "")

    def _tokeniter(self, ptr):
        if ptr.at_pattern(RE_QUOTE):
            # The opening quote ("'" or '"') of a string literal. Escaped quote
            # chars are not supported. Will keep reading characters until the
            # next matching quote char is found.
            str_literal = self.read_string(ptr)
            yield Token(ptr.linecount, TOKEN_STRING, str_literal)

        elif ptr.ch.isdigit():
            # The first digit of an integer literal, float literal or range
            # expression.
            num_literal = ptr.eat(RE_DIGITS)
            if ptr.at(reverse_operators[TOKEN_RANGE]):
                yield Token(ptr.linecount, TOKEN_INTEGER, num_literal)
            elif ptr.at(reverse_operators[TOKEN_DOT]):
                # A float literal
                ptr.read_char()  # Eat the decimal point
                decimal = ptr.eat(RE_DIGITS)
                float_literal = "".join((num_literal, ".", decimal))
                yield Token(
                    ptr.linecount,
                    TOKEN_FLOAT,
                    float_literal,
                )
            else:
                # A simple integer literal
                yield Token(ptr.linecount, TOKEN_INTEGER, num_literal)

        elif ptr.ch.isalpha():
            # The first character of an identifer or keyword (true, and ..).
            identifier = self.read_identifier(ptr)
            token_type = keywords.get(identifier, TOKEN_IDENTIFIER)
            yield Token(ptr.linecount, token_type, identifier)

        else:
            # A one or two character symbol.
            try:
                symbol = ptr.ch + ptr.peek(1)
                token_type = operators[symbol]
                ptr.read_char()
            except KeyError:
                symbol = ptr.ch
                token_type = operators.get(symbol, TOKEN_ILLEGAL)

            ptr.read_char()
            yield Token(ptr.linecount, token_type, symbol)

    def read_string(self, ptr: Pointer) -> str:
        """Return all characters up to the next `quote` char."""
        # Opening quote
        quote = ptr.ch
        ptr.read_char()

        # Jump to the next quote that matches the opening quote.
        idx = ptr.idx
        ptr.jump_to(quote)

        val = ptr.source[idx : ptr.idx]
        ptr.read_char()  # Eat the closing quote.

        return val

    def read_identifier(self, ptr) -> str:
        """Return all characters up to the next period, bracket or whitespace."""
        idx = ptr.idx
        ptr.jump_to_pattern(RE_ENDIDENTIFIER)
        return ptr.source[idx : ptr.idx]


class TokType(IntEnum):
    STATEMENT_START = 1
    STATEMENT_END = 2
    TAG_START = 3
    TAG_END = 4
    STATEMENT = 5
    TAG = 6
    EXPRESSION = 7
    LITERAL = 8
    EOF = 9
    LSTRIP = 10
    RSTRIP = 11


class RangeToken(NamedTuple):
    type: int
    start: int
    end: int


class RangeLexer(Lexer):
    def __init__(self, env):
        super().__init__(env)
        self.stmt_s = sys.intern(env.statement_start_string)
        self.stmt_e = sys.intern(env.statement_end_string)
        self.tag_s = sys.intern(env.tag_start_string)
        self.tag_e = sys.intern(env.tag_end_string)

        self.literal_end_re = re.compile(
            fr"({re.escape(env.tag_start_string)}|{re.escape(env.statement_start_string)})-?"
        )

        self.stmt_sl = len(self.stmt_s)
        self.stmt_el = len(self.stmt_e)
        self.tag_sl = len(self.tag_s)
        self.tag_el = len(self.tag_e)
        self.wsc_l = len(TOKEN_WHITESPACE_CONTROL)

    def _scan(self, source: str) -> Iterator[RangeToken]:
        size: int = len(source)
        pos: int = 0

        while pos < size:
            if source.find(self.stmt_s, pos) == pos:
                # The start of an output statement.
                pos += self.stmt_sl

                wsc = source.find(TOKEN_WHITESPACE_CONTROL, pos) == pos
                if wsc:
                    pos += self.wsc_l

                end = source.find(self.stmt_e, pos)
                if end == -1:
                    raise LiquidSyntaxError(f"expected '{self.stmt_e}', found 'eof'")

                # We're deliberatly moving the whitespace control token ahead
                # of the tag token here. Just to be consistent with RSTRIP
                # tokens that must precede their LITERAL.
                if source[end - 1] == TOKEN_WHITESPACE_CONTROL:
                    yield RangeToken(TokType.LSTRIP, end - 1, end)
                    yield RangeToken(TokType.STATEMENT, pos, end - 1)
                else:
                    yield RangeToken(TokType.STATEMENT, pos, end)
                pos = end + self.stmt_el

            elif source.find(self.tag_s, pos) == pos:
                # The start of a tag. Could be the start or end of a tag block, or
                # non-block tag.
                pos += self.tag_sl

                wsc = source.find(TOKEN_WHITESPACE_CONTROL, pos) == pos
                if wsc:
                    pos += self.wsc_l

                end = source.find(self.tag_e, pos)
                if end == -1:
                    raise LiquidSyntaxError(f"expected '{self.tag_e}', found 'eof'")

                # Peek at the tag name before moving past it.
                raw = self.is_raw(source, pos, end)

                # We're deliberatly moving the whitespace control token ahead
                # of the tag token here. Just to be consistent with RSTRIP
                # tokens that must precede their LITERAL.
                if source[end - 1] == TOKEN_WHITESPACE_CONTROL:
                    yield RangeToken(TokType.LSTRIP, end - 1, end)
                    yield RangeToken(TokType.TAG, pos, end - 1)
                else:
                    yield RangeToken(TokType.TAG, pos, end)
                pos = end + self.tag_el

                # Special case for raw tags.
                if raw:
                    match = RE_ENDRAW.search(source, pos)
                    if match:
                        end = match.start()
                    else:
                        end = size

                    yield RangeToken(TokType.LITERAL, pos, end)
                    pos = end
            else:
                # A template literal
                match = self.literal_end_re.search(source, pos)
                if match:
                    end = match.start()
                else:
                    end = size  # EOF

                # Look ahead for whitespace control.
                if source.find("-", end) == end + 2:
                    yield RangeToken(TokType.RSTRIP, end + 2, end + 3)

                yield RangeToken(TokType.LITERAL, pos, end)
                pos = end

        yield RangeToken(TokType.EOF, 0, 0)

    def tokeniter(self, source: str, linenum: int = 1) -> Iterator[Token]:

        # TODO: Better.
        lstrip = False
        rstrip = False

        try:
            for tok in self._scan(source):
                val = source[tok.start : tok.end]

                if tok.type == TokType.STATEMENT:
                    yield Token(linenum, TOKEN_STATEMENT, val.strip())
                elif tok.type == TokType.TAG:
                    _val = val.strip()
                    if " " in _val:
                        name, expr = _val.split(None, 1)
                        yield Token(linenum, TOKEN_TAG_NAME, name)
                        yield Token(linenum, TOKEN_EXPRESSION, expr.lstrip())
                    else:
                        yield Token(linenum, TOKEN_TAG_NAME, _val)
                elif tok.type == TokType.LSTRIP:
                    lstrip = True
                elif tok.type == TokType.RSTRIP:
                    rstrip = True
                else:
                    if lstrip and rstrip:
                        _val = val.strip()
                    elif lstrip:
                        _val = val.lstrip()
                    elif rstrip:
                        _val = val.rstrip()
                    else:
                        _val = val

                    lstrip = False
                    rstrip = False
                    if _val:
                        yield Token(linenum, TOKEN_LITERAL, _val)

                linenum += val.count("\n")
        except LiquidSyntaxError as err:
            err.linenum = linenum
            raise

        yield Token(linenum, TOKEN_EOF, "")

    def is_raw(self, source: str, pos: int, end: int) -> bool:
        val = source[pos:end].strip()
        return val == "raw"


@lru_cache
def get_lexer(env):
    """Return a template lexer for the given environment."""
    # return TemplateLexer(env)
    return RangeLexer(env)


@lru_cache
def get_expression_lexer(env):
    """Return an expression lexer for the given environment."""
    return ExpressionLexer(env)


@lru_cache
def get_liquid_lexer(env):
    """Return a "liquid" tag lexer for the given environment."""
    return LiquidLexer(env)
