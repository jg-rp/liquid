"""A wrapper for token iterators that lets us step through and peek ahead."""

from __future__ import annotations

from collections import deque
from typing import Iterator

from liquid.token import Token
from liquid.token import TOKEN_INITIAL
from liquid.token import TOKEN_EOF


class TokenStream:
    """Step through or iterate a stream of tokens."""

    def __init__(self, tokeniter: Iterator[Token]):
        self.iter = tokeniter

        # Queue of peeked tokens
        self._pushed = deque()

        # Stack of tags
        self.balancing_stack = []

        self.current: Token = Token(0, TOKEN_INITIAL, "")
        next(self)

    class TokenStreamIterator:
        """An iterable token stream."""

        def __init__(self, stream: TokenStream):
            self.stream = stream

        def __iter__(self):
            return self

        def __next__(self) -> Token:
            tok = self.stream.current
            if tok.type is TOKEN_EOF:
                self.stream.close()
                raise StopIteration()
            next(self.stream)
            return tok

    def __iter__(self):
        return self.TokenStreamIterator(self)

    def __next__(self):
        tok = self.current
        if self._pushed:
            self.current = self._pushed.popleft()
        elif self.current.type is not TOKEN_EOF:
            try:
                self.current = next(self.iter)
            except StopIteration:
                self.close()
        return tok

    def __str__(self):  # pragma: no cover
        buf = [
            f"current: {self.current}",
            f"next: {self.peek}",
        ]
        return "\n".join(buf)

    def next_token(self):
        """Return the next token from the stream."""
        return next(self)

    @property
    def peek(self) -> Token:
        """Look at the next token."""
        old_token = next(self)
        result = self.current
        self.push(result)
        self.current = old_token
        return result

    def push(self, tok: Token):
        """Push a token back to the stream."""
        self._pushed.append(tok)

    def close(self):
        """Close the stream."""
        self.current = Token(0, TOKEN_EOF, "")
