"""Token stream test cases."""
from unittest import TestCase

from typing import List

from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_EOF

from liquid.exceptions import LiquidSyntaxError

from liquid.expressions import Token
from liquid.expressions import TokenStream


class ExpresssionTokenStreamTestCase(TestCase):
    """Test the expression token stream."""

    def setUp(self) -> None:
        self.tokens: List[Token] = [
            (1, TOKEN_STRING, "Liquid"),
            (1, TOKEN_PIPE, "|"),
            (1, TOKEN_IDENTIFIER, "slice"),
            (1, TOKEN_COLON, ":"),
            (1, TOKEN_INTEGER, "2"),
            (1, TOKEN_COMMA, ","),
            (1, TOKEN_INTEGER, "5"),
        ]

    def test_iterate_stream(self):
        """Test that we can iterate a token stream."""
        stream = TokenStream(iter(self.tokens))

        for i, token in enumerate(stream):
            self.assertEqual(token, self.tokens[i])

        stream = TokenStream(iter(self.tokens))
        stream_iter = iter(stream)

        self.assertEqual(list(stream_iter), self.tokens)

    def test_step_through_stream(self):
        """Test that we can step through a token stream."""
        stream = TokenStream(iter(self.tokens))

        for token in self.tokens:
            self.assertEqual(token, stream.next_token())

    def test_step_through_stream_with_next(self):
        """Test that we can step through a token stream using next."""
        stream = TokenStream(iter(self.tokens))

        for token in self.tokens:
            self.assertEqual(token, next(stream))

    def test_end_of_stream(self):
        """Test that we get an EOF token when the stream is exhausted."""
        stream = TokenStream(iter(self.tokens))
        _ = list(stream)
        self.assertEqual(stream.current[1], TOKEN_EOF)
        self.assertEqual(next(stream)[1], TOKEN_EOF)

    def test_peek(self):
        """Test that we can peek at the next token."""
        stream = TokenStream(iter(self.tokens))

        for i in range(len(self.tokens) - 1):
            self.assertEqual(stream.peek, self.tokens[i + 1])
            next(stream)

    def test_push(self):
        """Test that we can push tokens back onto the stream."""
        stream = TokenStream(iter(self.tokens))

        self.assertEqual(stream.current, self.tokens[0])
        self.assertEqual(stream.peek, self.tokens[1])

        token = next(stream)
        self.assertEqual(token, self.tokens[0])
        self.assertEqual(stream.current, self.tokens[1])
        self.assertEqual(stream.peek, self.tokens[2])

        stream.push(token)
        self.assertEqual(next(stream), self.tokens[0])

        stream.push(token)
        self.assertEqual(stream.current, self.tokens[0])
        self.assertEqual(stream.peek, self.tokens[1])

    def test_expect(self):
        """Test that we can make assertions about the current token."""
        stream = TokenStream(iter(self.tokens))
        stream.expect(TOKEN_STRING)

        with self.assertRaises(LiquidSyntaxError):
            stream.expect(TOKEN_INTEGER)

    def test_expect_peek(self):
        """Test that we can make assertions about the next token."""
        stream = TokenStream(iter(self.tokens))
        stream.expect_peek(TOKEN_PIPE)

        with self.assertRaises(LiquidSyntaxError):
            stream.expect_peek(TOKEN_INTEGER)
