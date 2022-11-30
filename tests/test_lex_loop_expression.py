"""Test loop-style expression tokenization.

Loop-style expressions are those found in the `for` tag and
the `tablerow` tag.
"""

import unittest
from typing import Any
from typing import NamedTuple

from liquid.expressions.loop import tokenize

from liquid.token import TOKEN_IN
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_COMMA
from liquid.token import Token


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    source: str
    expect: Any


class LexIncludeExpressionTestCase(unittest.TestCase):
    """Test cases for `include` expressions."""

    def test_lex_include_expression(self) -> None:
        """Test that we can tokenize `include` expressions."""
        test_cases = [
            Case(
                "loop over identifier",
                "product in collection.products",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                ],
            ),
            Case(
                "loop over identifier with limit and offset",
                "product in collection.products limit:4 offset:2",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_IDENTIFIER, "collection"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_LIMIT, "limit"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "4"),
                    Token(1, TOKEN_OFFSET, "offset"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "2"),
                ],
            ),
            Case(
                "loop over reversed range",
                "num in (1..10) reversed",
                [
                    Token(1, TOKEN_IDENTIFIER, "num"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_LPAREN, "("),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_INTEGER, "10"),
                    Token(1, TOKEN_RPAREN, ")"),
                    Token(1, TOKEN_REVERSED, "reversed"),
                ],
            ),
            Case(
                "loop over range with identifier",
                "i in (1..num)",
                [
                    Token(1, TOKEN_IDENTIFIER, "i"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_LPAREN, "("),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_IDENTIFIER, "num"),
                    Token(1, TOKEN_RPAREN, ")"),
                ],
            ),
            Case(
                "loop over range with float start",
                "i in (2.4..5)",
                [
                    Token(1, TOKEN_IDENTIFIER, "i"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_LPAREN, "("),
                    Token(1, TOKEN_FLOAT, "2.4"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_INTEGER, "5"),
                    Token(1, TOKEN_RPAREN, ")"),
                ],
            ),
            Case(
                description="loop over named iterable with continue offset",
                source="item in array limit: 3 offset: continue",
                expect=[
                    Token(1, TOKEN_IDENTIFIER, "item"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_IDENTIFIER, "array"),
                    Token(1, TOKEN_LIMIT, "limit"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "3"),
                    Token(1, TOKEN_OFFSET, "offset"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_CONTINUE, "continue"),
                ],
            ),
            Case(
                description="comma separated arguments",
                source="i in array, limit: 4, offset: 2",
                expect=[
                    Token(1, TOKEN_IDENTIFIER, "i"),
                    Token(1, TOKEN_IN, "in"),
                    Token(1, TOKEN_IDENTIFIER, "array"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_LIMIT, "limit"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "4"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_OFFSET, "offset"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "2"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)
