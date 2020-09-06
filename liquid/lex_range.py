from enum import IntEnum
from typing import Iterator, Tuple, NamedTuple

from liquid.lex import Lexer
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

from liquid.exceptions import LiquidSyntaxError


class TokenType(IntEnum):
    STATEMENT_START = 1
    STATEMENT_END = 2
    TAG_START = 3
    TAG_END = 4
    STATEMENT = 5
    TAG = 6
    EXPRESSION = 7
    LITERAL = 8
    EOF = 9
    WSC = 10


class RangeToken(NamedTuple):
    type: int
    start: int
    end: int
    wsc: bool


class RangeLexer(Lexer):
    def tokeniter(self, source: str, linenum: int = 1) -> Iterator[Token]:
        yield from self._tokeniter(source, linenum)

    def _scan(self, source: str) -> Iterator[RangeToken]:
        size: int = len(source)
        pos: int = 0

        while pos < size:
            if source.find(r"{{", pos) == pos:
                pos += 2

                wsc = source[pos] == "-"
                if wsc:
                    pos += 1

                end = source.find(r"}}", pos)
                self.raise_for_end(end)

                yield RangeToken(TokenType.STATEMENT, pos, end, wsc)
                pos = end + 2

            elif source.find(r"{%", pos) == pos:
                pos += 2

                wsc = source[pos] == "-"
                if wsc:
                    pos += 1

                end = source.find(r"%}", pos)
                self.raise_for_end(end)

                yield RangeToken(TokenType.TAG, pos, end, wsc)
                pos = end + 2
            else:
                end = min(
                    [
                        idx
                        for idx in (
                            source.find(r"{{", pos),
                            source.find(r"{%", pos),
                            size,
                        )
                        if idx != -1
                    ]
                )

                yield RangeToken(TokenType.LITERAL, pos, end, False)
                pos = end

        while True:
            yield RangeToken(TokenType.EOF, 0, 0, False)

    def _tokeniter(self, source: str, linenum: int = 1) -> Iterator[Token]:
        it = self._scan(source)
        rt = next(it)
        next_rt = next(it)

        lstrip = False

        while rt.type != TokenType.EOF:
            val = source[rt.start : rt.end]
            print(rt)

            if rt.type == TokenType.STATEMENT:
                _val = val.strip()

                if _val.endswith("-"):
                    _val = _val[:-1]

                yield Token(linenum, TOKEN_STATEMENT, _val)
            elif rt.type == TokenType.TAG:
                _val = val.strip()

                if _val.endswith("-"):
                    _val = _val[:-1]

                if " " in _val:
                    name, expr = _val.split(" ", 1)
                    yield Token(linenum, TOKEN_TAG_NAME, name)
                    yield Token(linenum, TOKEN_EXPRESSION, expr.lstrip())
                else:
                    yield Token(linenum, TOKEN_TAG_NAME, _val)
            else:
                rstrip = next_rt.wsc
                if lstrip and rstrip:
                    _val = val.strip()
                elif lstrip:
                    _val = val.lstrip()
                elif rstrip:
                    _val = val.rstrip()
                else:
                    _val = val

                yield Token(linenum, TOKEN_LITERAL, _val)

            linenum += val.count("\n")

            rt = next_rt
            next_rt = next(it)

        yield Token(linenum, TOKEN_EOF, "")

    def raise_for_end(self, end: int):
        if end == -1:
            raise LiquidSyntaxError("unbalanced delimiters")
