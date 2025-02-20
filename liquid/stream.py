"""A wrapper for token iterators that lets us step through and peek ahead."""

from __future__ import annotations

from collections import deque
from typing import Deque
from typing import Iterator
from typing import Optional

from .exceptions import LiquidSyntaxError
from .token import TOKEN_EOF
from .token import TOKEN_INITIAL
from .token import Token
from .token import reverse_operators


class TokenStream:
    """Step through or iterate a stream of tokens."""

    def __init__(
        self,
        tokeniter: Iterator[Token],
        *,
        shorthand_indexes: bool = False,
    ):
        self.iter = tokeniter

        # Queue of peeked tokens
        self._pushed: Deque[Token] = deque()

        self.current: Token = Token(0, TOKEN_INITIAL, "")
        next(self)

        self.shorthand_indexes = shorthand_indexes

    class TokenStreamIterator:
        """An iterable token stream."""

        def __init__(self, stream: TokenStream):
            self.stream = stream

        def __iter__(self) -> Iterator[Token]:
            return self

        def __next__(self) -> Token:
            tok = self.stream.current
            if tok.kind is TOKEN_EOF:
                self.stream.close()
                raise StopIteration
            next(self.stream)
            return tok

    def __iter__(self) -> Iterator[Token]:
        return self.TokenStreamIterator(self)

    def __next__(self) -> Token:
        tok = self.current
        if self._pushed:
            self.current = self._pushed.popleft()
        elif self.current.kind is not TOKEN_EOF:
            try:
                self.current = next(self.iter)
            except StopIteration:
                self.close()
        return tok

    def __str__(self) -> str:  # pragma: no cover
        buf = [
            f"current: {self.current}",
            f"next: {self.peek}",
        ]
        return "\n".join(buf)

    def next_token(self) -> Token:
        """Return the next token from the stream."""
        return next(self)

    @property
    def peek(self) -> Token:
        """Look at the next token."""
        current = next(self)
        result = self.current
        self.push(current)
        return result

    def push(self, tok: Token) -> None:
        """Push a token back to the stream."""
        self._pushed.append(self.current)
        self.current = tok

    def close(self) -> None:
        """Close the stream."""
        self.current = Token(0, TOKEN_EOF, "")

    def _expect(self, tok: Token, typ: str, value: Optional[str] = None) -> None:
        if tok.kind != typ or (value is not None and tok.value != value):
            _typ = reverse_operators.get(tok.kind, tok.kind)
            _expected_typ = reverse_operators.get(typ, typ)
            if value is not None:
                msg = (
                    f"expected {_expected_typ} with value '{value}', "
                    f"found {_typ} with value '{tok.value}'"
                )
            else:
                msg = f"expected '{_expected_typ}', found '{_typ}'"
            raise LiquidSyntaxError(msg, linenum=tok.start_index)

    def expect(self, typ: str, value: Optional[str] = None) -> None:
        """Check the current token in the stream matches the given type and value.

        Raises a `LiquidSyntaxError` if they don't.
        """
        self._expect(self.current, typ, value)

    def expect_peek(self, typ: str, value: Optional[str] = None) -> None:
        """Check the next token in the stream matches the given type and value.

        Raises a `LiquidSyntaxError` if they don't.
        """
        self._expect(self.peek, typ, value)
