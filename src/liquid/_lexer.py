from __future__ import annotations

import re
from collections.abc import Callable
from typing import TYPE_CHECKING

from ._tokens import TOKEN_WC

if TYPE_CHECKING:
    from ._tokens import Token, TokenKind
    from .environment import LiquidEnvironment


type State = Callable[[], State | None]


class Lexer:
    """Template source tokenizer."""

    __slots__ = (
        "comment_end",
        "comment_start",
        "length",
        "out_end",
        "out_start",
        "pos",
        "source",
        "start",
        "tag_start",
        "tag_start",
        "tokens",
    )

    def __init__(self, env: LiquidEnvironment, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.start = 0
        self.pos = 0
        self.tokens: list[Token] = []

        self.comment_start = env.comment_start_delimiter
        self.comment_end = env.comment_end_delimiter
        self.out_start = env.output_start_delimiter
        self.out_end = env.output_end_delimiter
        self.tag_start = env.tag_start_delimiter
        self.tag_start = env.tag_end_delimiter

    @classmethod
    def tokenize(cls, env: LiquidEnvironment, source: str) -> list[Token]:
        lexer = cls(env, source)
        lexer.run()
        return lexer.tokens

    def run(self) -> None:
        state: State | None = self.scan_markup
        while state:
            state = state()

    def emit(self, kind: TokenKind) -> None:
        self.tokens.append((kind, self.start, self.pos))
        self.start = self.pos

    def index(self, pattern: re.Pattern[str]) -> int | None:
        if match := pattern.search(self.source, self.pos):
            return match.start()
        return None

    def scan(self, pattern: re.Pattern[str]) -> str | None:
        if match := pattern.match(self.source, self.pos):
            self.pos = match.end()
            return match[0]
        return None

    def scan_until(self, pattern: re.Pattern[str]) -> str | None:
        if match := pattern.search(self.source, self.pos):
            self.pos = match.start()
            return self.source[self.start : match.start()]
        return None

    def skip(self, pattern: re.Pattern[str]) -> bool:
        if match := pattern.match(self.source, self.pos):
            self.pos = match.end()
            self.start = self.pos
            return True
        return False

    def skip_until(self, pattern: re.Pattern[str]) -> re.Match[str] | None:
        if match := pattern.search(self.source, self.pos):
            self.pos = match.start()
            return match
        return None

    def accept_whitespace_control(self) -> bool:
        if self.pos < self.length and self.source[self.pos] == "-":
            self.pos += 1
            self.emit(TOKEN_WC)
            return True
        return False

    def scan_markup(self) -> State | None:
        raise NotImplementedError
