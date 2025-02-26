"""A wrapper for token iterators that lets us step through and peek ahead."""

from __future__ import annotations

from collections import deque
from typing import Deque
from typing import Iterator
from typing import Optional

from .builtin.expressions import tokenize
from .exceptions import LiquidSyntaxError
from .token import TOKEN_EOF
from .token import TOKEN_EXPRESSION
from .token import TOKEN_INITIAL
from .token import Token
from .token import reverse_operators


class TokenStream:
    """Step through or iterate a stream of tokens."""

    eof = Token(TOKEN_EOF, "", -1, "")

    def __init__(
        self,
        tokeniter: Iterator[Token],
        *,
        shorthand_indexes: bool = False,
    ):
        self.iter = tokeniter

        # Queue of peeked tokens
        self._pushed: Deque[Token] = deque()

        self.current: Token = Token(TOKEN_INITIAL, "", 0, "")
        next(self)

        self.shorthand_indexes = shorthand_indexes  # TODO:

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
        # TODO: loose close
        self.current = self.eof

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
            raise LiquidSyntaxError(msg, token=tok)

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

    def eat(self, typ: str) -> Token:
        """Consume and return the next token.

        If the type of the next token is equal to _typ_, raise an exceptions.

        This is equivalent to `stream.expect(typ)` followed by `next(stream)`.
        """
        tok = self.current
        if tok.kind != typ:
            msg = (
                f"expected {reverse_operators.get(typ, typ)!r}, "
                f"found {reverse_operators.get(tok.kind, tok.kind)!r}"
            )
            raise LiquidSyntaxError(msg, token=tok)
        return next(self)

    def eat_one_of(self, *typ: str) -> Token:
        """Consume and return the next token.

        If the type of the next token is equal to _typ_, raise an exceptions.

        This is equivalent to `stream.expect(typ)` followed by `next(stream)`.
        """
        tok = self.current
        if tok.kind not in typ:
            msg = (
                f"expected on of {typ!r}, "
                f"found {reverse_operators.get(tok.kind, tok.kind)!r}"
            )
            raise LiquidSyntaxError(msg, token=tok)
        return next(self)

    def into_inner(self) -> TokenStream:
        """Return a stream of tokens for the current expression token.

        If the current token is not an expression, a LiquidSyntaxError is
        raised.
        """
        token = self.current
        if token.kind != TOKEN_EXPRESSION:
            msg = (
                "expected an expression, "
                f"found {reverse_operators.get(token.kind, token.kind)!r}"
            )
            raise LiquidSyntaxError(msg, token=token)
        next(self)
        return TokenStream(tokenize(token.value, parent_token=token))

    def expect_eos(self) -> None:
        """Raise a syntax error if we're not at the end of the stream."""
        if self.current.kind != TOKEN_EOF:
            raise LiquidSyntaxError(
                f"unexpected token {self.current.kind}", token=self.current
            )
