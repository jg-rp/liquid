from __future__ import annotations

import re
from collections.abc import Callable
from typing import TYPE_CHECKING

from .tokens import TOKEN_WC

if TYPE_CHECKING:
    from .environment import Environment
    from .tokens import Token, TokenKind


type State = Callable[[], State | None]


class Lexer:
    """Template source tokenizer."""

    __slots__ = (
        "length",
        "pos",
        "source",
        "start",
        "tokens",
    )

    def __init__(self, env: Environment, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.start = 0
        self.pos = 0
        self.tokens: list[Token] = []

    @classmethod
    def tokenize(cls, env: Environment, source: str) -> list[Token]:
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
