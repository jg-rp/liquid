"""Test include-style expression tokenization.

Include-style expressions are those found in the `include` tag,
the `render` tag, or any tag accepting comma separated, key/value
arguments.
"""

import unittest
from typing import Any
from typing import NamedTuple

from liquid.expressions.include import tokenize

from liquid.token import TOKEN_AS
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_FOR
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_WITH
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
                "string literal name no local variable",
                "'product'",
                [
                    Token(1, TOKEN_STRING, "product"),
                ],
            ),
            Case(
                "name from identifier and no local variable",
                "section.name",
                [
                    Token(1, TOKEN_IDENTIFIER, "section"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                ],
            ),
            Case(
                "string literal name with identifier local variable",
                "'product' with products[0]",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_WITH, "with"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_IDENTINDEX, "0"),
                ],
            ),
            Case(
                "string literal name with keyword arguments",
                "'product', foo: 'bar', some: other.tags",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_STRING, "bar"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "some"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_IDENTIFIER, "other"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "tags"),
                ],
            ),
            Case(
                "string literal name with keyword arguments including a range literal",
                "'product', foo: (1..3)",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_LPAREN, "("),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_INTEGER, "3"),
                    Token(1, TOKEN_RPAREN, ")"),
                ],
            ),
            Case(
                "string literal name with identifier aliased local variable",
                "'product' with products[0] as foo",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_WITH, "with"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_IDENTINDEX, "0"),
                    Token(1, TOKEN_AS, "as"),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                ],
            ),
            Case(
                "string literal name with iterable local variable",
                "'product' for products",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_FOR, "for"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                ],
            ),
            Case(
                "string literal name with aliased iterable local variable",
                "'product' for products as foo",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_FOR, "for"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_AS, "as"),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                ],
            ),
            Case(
                "literal name with identifier aliased local variable and arguments",
                "'product' with products[0] as foo, bar: 42, baz: 'hello'",
                [
                    Token(1, TOKEN_STRING, "product"),
                    Token(1, TOKEN_WITH, "with"),
                    Token(1, TOKEN_IDENTIFIER, "products"),
                    Token(1, TOKEN_IDENTINDEX, "0"),
                    Token(1, TOKEN_AS, "as"),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "bar"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "42"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "baz"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_STRING, "hello"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)
