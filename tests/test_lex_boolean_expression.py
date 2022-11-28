"""Test Liquid boolean expression tokenization."""

import unittest

from typing import Any
from typing import NamedTuple

from liquid.exceptions import LiquidSyntaxError

from liquid.expressions.boolean import tokenize
from liquid.expressions.boolean import tokenize_with_parens

from liquid.token import TOKEN_AND
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_EQ
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_GE
from liquid.token import TOKEN_GT
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LE
from liquid.token import TOKEN_LG
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_NE
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NOT
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_RANGE_LITERAL
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import Token


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    source: str
    expect: Any


class LexBooleanExpressionTestCase(unittest.TestCase):
    """Test cases for the standard boolean expression."""

    test_cases = [
        Case(
            "literal boolean",
            "false == true",
            [
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_TRUE, "true"),
            ],
        ),
        Case(
            "not nil identifier",
            "user != nil",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_NE, "!="),
                Token(1, TOKEN_NIL, "nil"),
            ],
        ),
        Case(
            "not null identifier",
            "user != null",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_NE, "!="),
                Token(1, TOKEN_NULL, "null"),
            ],
        ),
        Case(
            "alternate not nil",
            "user <> nil",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_LG, "<>"),
                Token(1, TOKEN_NIL, "nil"),
            ],
        ),
        Case(
            "identifier equals string literal",
            "user.name == 'brian'",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "name"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_STRING, "brian"),
            ],
        ),
        Case(
            "equality with or",
            "user.name == 'bill' or user.name == 'bob'",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "name"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_STRING, "bill"),
                Token(1, TOKEN_OR, "or"),
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "name"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_STRING, "bob"),
            ],
        ),
        Case(
            "equality with and",
            "user.name == 'bob' and user.age > 45",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "name"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_STRING, "bob"),
                Token(1, TOKEN_AND, "and"),
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "age"),
                Token(1, TOKEN_GT, ">"),
                Token(1, TOKEN_INTEGER, "45"),
            ],
        ),
        Case(
            "greater than or equal to integer literal",
            "user.age >= 21",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "age"),
                Token(1, TOKEN_GE, ">="),
                Token(1, TOKEN_INTEGER, "21"),
            ],
        ),
        Case(
            "less than or equal to integer literal",
            "user.age <= 21",
            [
                Token(1, TOKEN_IDENTIFIER, "user"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "age"),
                Token(1, TOKEN_LE, "<="),
                Token(1, TOKEN_INTEGER, "21"),
            ],
        ),
        Case(
            "identifier contains string",
            "product.tags contains 'sale'",
            [
                Token(1, TOKEN_IDENTIFIER, "product"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "tags"),
                Token(1, TOKEN_CONTAINS, "contains"),
                Token(1, TOKEN_STRING, "sale"),
            ],
        ),
        Case(
            "identifier equals blank",
            "product.title == blank",
            [
                Token(1, TOKEN_IDENTIFIER, "product"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "title"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_BLANK, "blank"),
            ],
        ),
        Case(
            "identifier equals empty",
            "product.title == empty",
            [
                Token(1, TOKEN_IDENTIFIER, "product"),
                Token(1, TOKEN_DOT, "."),
                Token(1, TOKEN_IDENTIFIER, "title"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_EMPTY, "empty"),
            ],
        ),
    ]

    def test_default_lexer(self) -> None:
        """Test that we can tokenize standard boolean expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_lexer_with_parens(self) -> None:
        """Test that the non-standard boolean expression lexer is backwards
        compatible with standard boolean expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_with_parens(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)

    def test_not(self) -> None:
        """Test that the `not` keyword is not recognized in default boolean
        expressions."""
        source = "not true"
        tokens = list(tokenize(source))
        self.assertEqual(len(tokens), 2)
        self.assertEqual(
            tokens,
            [
                Token(1, TOKEN_IDENTIFIER, "not"),  # ident, not TOKEN_NOT
                Token(1, TOKEN_TRUE, "true"),
            ],
        )


class LexBooleanNotExpressionTestCase(unittest.TestCase):
    """Test cases for the non-standard boolean expression that supports
    logical `not` and grouping with parentheses."""

    test_cases = [
        Case(
            "literal boolean not true",
            "false == not true",
            [
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_NOT, "not"),
                Token(1, TOKEN_TRUE, "true"),
            ],
        ),
        Case(
            "literal boolean not false",
            "false == not false",
            [
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_NOT, "not"),
                Token(1, TOKEN_FALSE, "false"),
            ],
        ),
        Case(
            "parens",
            "(false and false)",
            [
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_AND, "and"),
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_RPAREN, ")"),
            ],
        ),
        Case(
            "range literals",
            "(1..3) == (1..3)",
            [
                Token(1, TOKEN_RANGE_LITERAL, "rangeliteral"),
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_INTEGER, "1"),
                Token(1, TOKEN_RANGE, ".."),
                Token(1, TOKEN_INTEGER, "3"),
                Token(1, TOKEN_RPAREN, ")"),
                Token(1, TOKEN_EQ, "=="),
                Token(1, TOKEN_RANGE_LITERAL, "rangeliteral"),
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_INTEGER, "1"),
                Token(1, TOKEN_RANGE, ".."),
                Token(1, TOKEN_INTEGER, "3"),
                Token(1, TOKEN_RPAREN, ")"),
            ],
        ),
        Case(
            "nested grouped boolean with logic operators",
            "((true or false) or (false)) and true",
            [
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_TRUE, "true"),
                Token(1, TOKEN_OR, "or"),
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_RPAREN, ")"),
                Token(1, TOKEN_OR, "or"),
                Token(1, TOKEN_LPAREN, "("),
                Token(1, TOKEN_FALSE, "false"),
                Token(1, TOKEN_RPAREN, ")"),
                Token(1, TOKEN_RPAREN, ")"),
                Token(1, TOKEN_AND, "and"),
                Token(1, TOKEN_TRUE, "true"),
            ],
        ),
    ]

    def test_lexer_with_parens(self) -> None:
        """Test that we can tokenize boolean expressions that support logical
        `not` and grouping with parentheses."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_with_parens(case.source))
                self.assertEqual(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)


class LexBooleanExpressionErrorsTestCase(unittest.TestCase):
    """Test cases for tokens that are illegal in a boolean expression."""

    test_cases = [
        Case(
            description="illegal characters",
            source="} == %",
            expect=LiquidSyntaxError,
        ),
        Case(
            description="unknown operator",
            source="x >< y",
            expect=LiquidSyntaxError,
        ),
    ]

    def test_lex_illegal_expression(self) -> None:
        """Test that we raise a syntax error upon illegal characters."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                with self.assertRaises(case.expect):
                    list(tokenize(case.source))

    def test_lex_illegal_expression_with_parens(self) -> None:
        """Test that we raise a syntax error upon illegal characters when using the
        non-standard lexer."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                with self.assertRaises(case.expect):
                    list(tokenize_with_parens(case.source))
