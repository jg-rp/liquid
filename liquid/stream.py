"""Step through a sequence of tokens."""

from __future__ import annotations

from typing import Iterator
from typing import Optional

from .builtin.expressions import tokenize
from .exceptions import LiquidSyntaxError
from .token import TOKEN_EOF
from .token import TOKEN_EXPRESSION
from .token import Token
from .token import reverse_operators


class TokenStream:
    """Step through a sequence of tokens."""

    eof = Token(TOKEN_EOF, "", -1, "")

    def __init__(
        self,
        tokens: Iterator[Token],
    ):
        self.tokens = list(tokens)
        self.pos = 0

    def __next__(self) -> Token:
        return self.next_token()

    def next(self) -> Token:
        """Return the next token and advance the iterator."""
        try:
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        except IndexError:
            return self.eof

    def next_token(self) -> Token:
        """Return the next token and advance the iterator."""
        try:
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        except IndexError:
            return self.eof

    @property
    def current(self) -> Token:
        """Return the token at the head of the stream without advancing."""
        try:
            return self.tokens[self.pos]
        except IndexError:
            return self.eof

    @property
    def peek(self) -> Token:
        """Look at the next token."""
        try:
            return self.tokens[self.pos + 1]
        except IndexError:
            return self.eof

    def _expect(self, tok: Token, typ: str, value: Optional[str] = None) -> Token:
        if tok.kind != typ or (value is not None and tok.value != value):
            _typ = self._operator(tok.kind)
            _expected_typ = self._operator(typ)
            if value is not None:
                msg = f"expected {_expected_typ} {value}, found {_typ}"
            else:
                msg = f"expected {_expected_typ}, found {_typ}"
            raise LiquidSyntaxError(msg, token=tok)
        return tok

    def expect(self, typ: str, value: Optional[str] = None) -> Token:
        """Check the current token in the stream matches the given type and value.

        Returns the current token if its type matches _typ_.
        Raises a `LiquidSyntaxError` if it doesn't.
        """
        return self._expect(self.current, typ, value)

    def expect_peek(self, typ: str, value: Optional[str] = None) -> Token:
        """Check the next token in the stream matches the given type and value.

        Returns the next token if its type matches _typ_.
        Raises a `LiquidSyntaxError` it doesn't.
        """
        return self._expect(self.peek, typ, value)

    def eat(self, typ: str) -> Token:
        """Consume and return the next token.

        If the type of the next token is equal to _typ_, raise an exceptions.

        This is equivalent to `stream.expect(typ)` followed by `next(stream)`.
        """
        tok = self.current
        if tok.kind != typ:
            msg = f"expected {self._operator(typ)}, found {self._operator(tok.kind)}"
            raise LiquidSyntaxError(msg, token=tok)
        return next(self)

    def eat_one_of(self, *typ: str) -> Token:
        """Consume and return the next token.

        If the type of the next token is equal to _typ_, raise an exceptions.

        This is equivalent to `stream.expect(typ)` followed by `next(stream)`.
        """
        tok = self.current
        if tok.kind not in typ:
            msg = f"expected one of {typ!r}, found {self._operator(tok.kind)}"
            raise LiquidSyntaxError(msg, token=tok)
        return next(self)

    def into_inner(
        self, *, tag: Optional[Token] = None, eat: bool = True
    ) -> TokenStream:
        """Return a stream of tokens for the current expression token.

        If the current token is not an expression, a `LiquidSyntaxError` is
        raised.

        If _tag_ is given, it will be used to add context information to the
        syntax error, should one be raised.

        If _eat_ is true (the default), the current token is consumed.
        """
        token = self.current
        if token.kind != TOKEN_EXPRESSION:
            raise LiquidSyntaxError("missing expression", token=tag or token)

        if eat:
            next(self)
        return TokenStream(tokenize(token.value, parent_token=token))

    def expect_eos(self) -> None:
        """Raise a syntax error if we're not at the end of the stream."""
        if self.current.kind != TOKEN_EOF:
            raise LiquidSyntaxError(
                f"unexpected token {self.current.kind}", token=self.current
            )

    def _operator(self, kind: str) -> str:
        try:
            return repr(reverse_operators[kind])
        except KeyError:
            return kind
