"""Token stream test cases."""
from unittest import TestCase

from liquid.token import Token
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_EOF

from liquid.stream import TokenStream


class TokenStreamTestCase(TestCase):
    """Test the token stream."""

    def setUp(self) -> None:
        self.tokens = [
            Token(1, TOKEN_STRING, "Liquid"),
            Token(1, TOKEN_PIPE, "|"),
            Token(1, TOKEN_IDENTIFIER, "slice"),
            Token(1, TOKEN_COLON, ":"),
            Token(1, TOKEN_INTEGER, "2"),
            Token(1, TOKEN_COMMA, ","),
            Token(1, TOKEN_INTEGER, "5"),
        ]

    def test_iterate_stream(self):
        """Test that we can iterate a token stream."""
        stream = TokenStream(iter(self.tokens))

        for i, token in enumerate(stream):
            self.assertEqual(token, self.tokens[i])

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
        self.assertEqual(stream.current.type, TOKEN_EOF)
        self.assertEqual(next(stream).type, TOKEN_EOF)

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
