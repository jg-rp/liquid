"""A wrapper for token iterators that lets us step through and peek ahead."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING
from typing import Deque
from typing import Iterator

from liquid.exceptions import LiquidSyntaxError
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_INITIAL
from liquid.token import reverse_operators

if TYPE_CHECKING:
    from liquid.expressions.common import Token


class TokenStream:
    """Step through or iterate a stream of tokens."""

    def __init__(self, tokeniter: Iterator[Token], *, shorthand_indexes: bool = False):
        self.iter = tokeniter
        self._pushed: Deque[Token] = deque()

        self.current: Token = (0, TOKEN_INITIAL, "")
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
            if tok[1] is TOKEN_EOF:
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
        elif self.current[1] is not TOKEN_EOF:
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
        self.current = (0, TOKEN_EOF, "")

    def expect(self, typ: str) -> None:
        """Raise a `LiquidSyntaxError` if the current token type doesn't match `typ`."""
        if self.current[1] != typ:
            raise LiquidSyntaxError(
                f"expected {reverse_operators.get(typ, typ)!r}, "
                f"found {reverse_operators.get(self.current[1], self.current[1])!r}",
                linenum=self.current[0],
            )

    def expect_peek(self, typ: str) -> None:
        """Raise a `LiquidSyntaxError` if the next token type does not match `typ`."""
        if self.peek[1] != typ:
            raise LiquidSyntaxError(
                f"expected {reverse_operators.get(typ, typ)!r}, "
                f"found {reverse_operators.get(self.peek[1], self.peek[1])!r}",
                linenum=self.peek[0],
            )
