"""Test Liquid filtered expression tokenization.

Filtered expression are those found in output statements, `assign` tags
and `echo` tags.
"""

import unittest

from typing import Any
from typing import NamedTuple

from liquid.expressions.filtered import tokenize
from liquid.expressions.conditional import tokenize as tokenize_conditional
from liquid.expressions.conditional import (
    tokenize_with_parens as tokenize_conditional_with_parens,
)

from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_DPIPE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_IF
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_ELSE
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_LT
from liquid.token import Token


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    source: str
    expect: Any


class LexFilteredExpressionTestCase(unittest.TestCase):
    """Test cases for the standard filtered expression."""

    test_cases = [
        Case(
            "string literal single quotes",
            "'foobar'",
            [Token(1, TOKEN_STRING, "foobar")],
        ),
        Case(
            "string literal double quotes",
            "'foobar'",
            [Token(1, TOKEN_STRING, "foobar")],
        ),
        Case(
            "integer literal",
            "7",
            [Token(1, TOKEN_INTEGER, "7")],
        ),
        Case(
            "negative integer literal",
            "-7",
            [
                Token(1, TOKEN_INTEGER, "-7"),
            ],
        ),
        Case(
            "float literal",
            "3.14",
            [Token(1, TOKEN_FLOAT, "3.14")],
        ),
        Case(
            "negative float literal",
            "-3.14",
            [
                Token(1, TOKEN_FLOAT, "-3.14"),
            ],
        ),
        Case(
            "lone identifier",
            "collection",
            [Token(1, TOKEN_IDENTIFIER, "collection")],
        ),
        Case(
            "lone identifier with a hyphen",
            "main-collection",
            [Token(1, TOKEN_IDENTIFIER, "main-collection")],
        ),
        Case(
            "chained identifier",
            "collection.products",
            [
                Token(1, TOKEN_IDENTIFIER, "collection"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "products"),
            ],
        ),
        Case(
            "chained identifier by double quoted key",
            'collection["products"]',
            [
                Token(1, TOKEN_IDENTIFIER, "collection"),
                Token(1, TOKEN_IDENTIFIER, "products"),
            ],
        ),
        Case(
            "chained identifier by single quoted key",
            "collection['products']",
            [
                Token(1, TOKEN_IDENTIFIER, "collection"),
                Token(1, TOKEN_IDENTIFIER, "products"),
            ],
        ),
        Case(
            "chained identifier with array index",
            "collection.products[0]",
            [
                Token(1, TOKEN_IDENTIFIER, "collection"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "products"),
                Token(1, TOKEN_IDENTINDEX, "0"),
            ],
        ),
        Case(
            "chained identifier with array index from identifier",
            "collection.products[i]",
            [
                Token(1, TOKEN_IDENTIFIER, "collection"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "products"),
                Token(1, TOKEN_LBRACKET, "["),
                Token(1, TOKEN_IDENTIFIER, "i"),
                Token(1, TOKEN_RBRACKET, "]"),
            ],
        ),
        Case(
            "string literal with filter",
            "'foo' | upcase",
            [
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "upcase"),
            ],
        ),
        Case(
            "identifier with filter",
            "collection.title | upcase",
            [
                Token(1, TOKEN_IDENTIFIER, "collection"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "title"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "upcase"),
            ],
        ),
        Case(
            "integer literal with filter and integer argument",
            "4 | at_least: 5",
            [
                Token(1, TOKEN_INTEGER, "4"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "at_least"),
                Token(1, TOKEN_COLON, ":"),
                Token(1, TOKEN_INTEGER, "5"),
            ],
        ),
        Case(
            "float literal with filter and float argument",
            "4.1 | divided_by: 5.2",
            [
                Token(1, TOKEN_FLOAT, "4.1"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "divided_by"),
                Token(1, TOKEN_COLON, ":"),
                Token(1, TOKEN_FLOAT, "5.2"),
            ],
        ),
        Case(
            "string literal with filter and string argument",
            "'foo' | append: 'bar'",
            [
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "append"),
                Token(1, TOKEN_COLON, ":"),
                Token(1, TOKEN_STRING, "bar"),
            ],
        ),
        Case(
            "string literal with filter and identifier argument",
            "'foo' | append: collection.title",
            [
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "append"),
                Token(1, TOKEN_COLON, ":"),
                Token(1, TOKEN_IDENTIFIER, "collection"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "title"),
            ],
        ),
        Case(
            "string literal with filter and multiple arguments",
            '"Liquid" | slice: 2, 5',
            [
                Token(1, TOKEN_STRING, "Liquid"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "slice"),
                Token(1, TOKEN_COLON, ":"),
                Token(1, TOKEN_INTEGER, "2"),
                Token(1, TOKEN_COMMA, ","),
                Token(1, TOKEN_INTEGER, "5"),
            ],
        ),
        Case(
            "string literal with multiple filters",
            '"Liquid" | slice: 2, 5 | upcase',
            [
                Token(1, TOKEN_STRING, "Liquid"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "slice"),
                Token(1, TOKEN_COLON, ":"),
                Token(1, TOKEN_INTEGER, "2"),
                Token(1, TOKEN_COMMA, ","),
                Token(1, TOKEN_INTEGER, "5"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "upcase"),
            ],
        ),
        Case(
            "inconsistent whitespace",
            ' "Liquid"   |slice: 2,5',
            [
                Token(1, TOKEN_STRING, "Liquid"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "slice"),
                Token(1, TOKEN_COLON, ":"),
                Token(1, TOKEN_INTEGER, "2"),
                Token(1, TOKEN_COMMA, ","),
                Token(1, TOKEN_INTEGER, "5"),
            ],
        ),
        Case(
            "range literal",
            "(1..5)",
            [
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_INTEGER, "1"),
                Token(1, TOKEN_RANGE, ".."),
                Token(1, TOKEN_INTEGER, "5"),
                Token(1, TOKEN_RPAREN, ")"),
            ],
        ),
        Case(
            "range literal with float literal start",
            "(2.4..5)",
            [
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_FLOAT, "2.4"),
                Token(1, TOKEN_RANGE, ".."),
                Token(1, TOKEN_INTEGER, "5"),
                Token(1, TOKEN_RPAREN, ")"),
            ],
        ),
        Case(
            "range literal with identifiers",
            "(a..b)",
            [
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_IDENTIFIER, "a"),
                Token(1, TOKEN_RANGE, ".."),
                Token(1, TOKEN_IDENTIFIER, "b"),
                Token(1, TOKEN_RPAREN, ")"),
            ],
        ),
    ]

    def test_standard_lexer(self) -> None:
        """Test that we can tokenize standard filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_conditional_lexer(self) -> None:
        """Test that the non-standard conditional expression lexer
        is backwards compatible with standard filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_conditional(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_conditional_lexer_with_parens(self) -> None:
        """Test that the non-standard conditional expression lexer, including
        logical `not` and parentheses, is backwards compatible with standard
        filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                range_count = len([tok for tok in case.expect if tok[1] == TOKEN_RANGE])
                tokens = list(tokenize_conditional_with_parens(case.source))
                self.assertEqual(len(tokens) - range_count, len(case.expect))


class LexConditionalExpressionTestCase(unittest.TestCase):
    """Test cases for the non-standard filtered expressions with inline conditions."""

    test_cases = [
        Case(
            description="simple condition",
            source="'foo' if true",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_TRUE, "true"),
            ],
        ),
        Case(
            description="comparison operator",
            source="'foo' if x < y",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_IDENTIFIER, "x"),
                Token(1, TOKEN_LT, "<"),
                Token(1, TOKEN_IDENTIFIER, "y"),
            ],
        ),
        Case(
            description="simple condition with alternative",
            source="'foo' if true else 'bar'",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_TRUE, "true"),
                Token(1, TOKEN_ELSE, "else"),
                Token(1, TOKEN_STRING, "bar"),
            ],
        ),
        Case(
            description="condition with preceding filter",
            source="'foo' | upcase if true else 'bar'",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "upcase"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_TRUE, "true"),
                Token(1, TOKEN_ELSE, "else"),
                Token(1, TOKEN_STRING, "bar"),
            ],
        ),
        Case(
            description="condition with alternative filter",
            source="'foo' if true else 'bar' | upcase",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_TRUE, "true"),
                Token(1, TOKEN_ELSE, "else"),
                Token(1, TOKEN_STRING, "bar"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "upcase"),
            ],
        ),
        Case(
            description="condition with tail filter",
            source="'foo' if true else 'bar' || upcase",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_TRUE, "true"),
                Token(1, TOKEN_ELSE, "else"),
                Token(1, TOKEN_STRING, "bar"),
                Token(1, TOKEN_DPIPE, "||"),
                Token(1, TOKEN_IDENTIFIER, "upcase"),
            ],
        ),
        Case(
            description="multi-line condition with tail filter",
            source="'foo'\nif true\nelse 'bar' || upcase",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(2, TOKEN_IF, "if"),
                Token(2, TOKEN_TRUE, "true"),
                Token(3, TOKEN_ELSE, "else"),
                Token(3, TOKEN_STRING, "bar"),
                Token(3, TOKEN_DPIPE, "||"),
                Token(3, TOKEN_IDENTIFIER, "upcase"),
            ],
        ),
    ]

    def test_conditional_lexer(self) -> None:
        """Test that the non-standard conditional expression lexer
        is backwards compatible with standard filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_conditional(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_conditional_lexer_with_parens(self) -> None:
        """Test that the non-standard conditional expression lexer, including
        logical `not` and parentheses, is backwards compatible with standard
        filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                range_count = len([tok for tok in case.expect if tok[1] == TOKEN_RANGE])
                tokens = list(tokenize_conditional_with_parens(case.source))
                self.assertEqual(len(tokens) - range_count, len(case.expect))


class LexConditionalNotExpressionTestCase(unittest.TestCase):
    """Test cases for the non-standard filtered expressions with inline conditions
    and logical `not` with parentheses for grouping terms."""

    test_cases = [
        Case(
            description="negated condition",
            source="'foo' if not true",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_NOT, "not"),
                Token(1, TOKEN_TRUE, "true"),
            ],
        ),
        Case(
            description="negated condition with alternative",
            source="'foo' if not true else 'bar'",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_NOT, "not"),
                Token(1, TOKEN_TRUE, "true"),
                Token(1, TOKEN_ELSE, "else"),
                Token(1, TOKEN_STRING, "bar"),
            ],
        ),
        Case(
            description="grouped condition with alternative",
            source="'foo' if not (false and false) else 'bar'",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_NOT, "not"),
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_AND, "and"),
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_RPAREN, ")"),
                Token(1, TOKEN_ELSE, "else"),
                Token(1, TOKEN_STRING, "bar"),
            ],
        ),
        Case(
            description="condition with preceding filter",
            source="'foo' | upcase if not true else 'bar'",
            expect=[
                Token(1, TOKEN_STRING, "foo"),
                Token(1, TOKEN_PIPE, "|"),
                Token(1, TOKEN_IDENTIFIER, "upcase"),
                Token(1, TOKEN_IF, "if"),
                Token(1, TOKEN_NOT, "not"),
                Token(1, TOKEN_TRUE, "true"),
                Token(1, TOKEN_ELSE, "else"),
                Token(1, TOKEN_STRING, "bar"),
            ],
        ),
    ]

    def test_conditional_lexer_with_parens(self) -> None:
        """Test that the non-standard conditional expression lexer, including
        logical `not` and parentheses, is backwards compatible with standard
        filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_conditional_with_parens(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)
