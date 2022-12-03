"""Test cases for parsing common Liquid literals and identifiers."""
import unittest

from liquid.expressions.common import parse_common_expression
from liquid.expressions.common import tokenize_common_expression
from liquid.expressions.stream import TokenStream

from liquid.expression import FloatLiteral
from liquid.expression import Identifier
from liquid.expression import IdentifierPathElement
from liquid.expression import IntegerLiteral
from liquid.expression import RangeLiteral
from liquid.expression import StringLiteral
from liquid.expression import BLANK
from liquid.expression import EMPTY
from liquid.expression import TRUE
from liquid.expression import FALSE
from liquid.expression import NIL

from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_RBRACKET


class ParseLiteralOrIdentifierTestCase(unittest.TestCase):
    """Test cases for parsing expression literals and identifiers."""

    def test_parse_literal_int(self) -> None:
        """Test that we can parse a literal integer."""
        expr = "42"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, IntegerLiteral(42))
        self.assertEqual(stream.current, (1, TOKEN_INTEGER, "42"))

    def test_parse_literal_float(self) -> None:
        """Test that we can parse a literal float."""
        expr = "42.2"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, FloatLiteral(42.2))
        self.assertEqual(stream.current, (1, TOKEN_FLOAT, "42.2"))

    def test_parse_literal_string(self) -> None:
        """Test that we can parse a literal string."""
        expr = "'42.2'"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, StringLiteral("42.2"))
        self.assertEqual(stream.current, (1, TOKEN_STRING, "42.2"))

    def test_parse_literal_range(self) -> None:
        """Test that we can parse a literal range."""
        expr = "(1..5)"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, RangeLiteral(IntegerLiteral(1), IntegerLiteral(5)))
        self.assertEqual(stream.current, (1, TOKEN_RPAREN, ")"))

    def test_parse_blank(self) -> None:
        """Test that we can parse a literal blank."""
        expr = "blank"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, BLANK)
        self.assertEqual(stream.current, (1, TOKEN_BLANK, "blank"))

    def test_parse_nil(self) -> None:
        """Test that we can parse a literal nil."""
        expr = "nil"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, NIL)
        self.assertEqual(stream.current, (1, TOKEN_NIL, "nil"))

    def test_parse_empty(self) -> None:
        """Test that we can parse a literal empty."""
        expr = "empty"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, EMPTY)
        self.assertEqual(stream.current, (1, TOKEN_EMPTY, "empty"))

    def test_parse_true(self) -> None:
        """Test that we can parse a literal true."""
        expr = "true"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, TRUE)
        self.assertEqual(stream.current, (1, TOKEN_TRUE, "true"))

    def test_parse_false(self) -> None:
        """Test that we can parse a literal false."""
        expr = "false"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(rv, FALSE)
        self.assertEqual(stream.current, (1, TOKEN_FALSE, "false"))

    def test_parse_identifier(self) -> None:
        """Test that we can parse an identifier."""
        expr = "a.b[1].c['foo']"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(
            rv,
            Identifier(
                [
                    IdentifierPathElement("a"),
                    IdentifierPathElement("b"),
                    IdentifierPathElement(1),
                    IdentifierPathElement("c"),
                    IdentifierPathElement("foo"),
                ]
            ),
        )
        self.assertEqual(stream.current, (1, TOKEN_IDENTIFIER, "foo"))

    def test_parse_nested_identifier(self) -> None:
        """Test that we can parse a nested identifier."""
        expr = "a.b[c.d[1]]"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(
            rv,
            Identifier(
                [
                    IdentifierPathElement("a"),
                    IdentifierPathElement("b"),
                    Identifier(
                        [
                            IdentifierPathElement("c"),
                            IdentifierPathElement("d"),
                            IdentifierPathElement(1),
                        ]
                    ),
                ]
            ),
        )
        self.assertEqual(stream.current, (1, TOKEN_RBRACKET, "]"))

    def test_parse_identifier_followed_by_comma(self) -> None:
        """Test that we can parse an identifier followed by other tokens."""
        expr = "a.b[1],"
        tokens = tokenize_common_expression(expr)
        stream = TokenStream(tokens)
        rv = parse_common_expression(stream)
        self.assertEqual(
            rv,
            Identifier(
                [
                    IdentifierPathElement("a"),
                    IdentifierPathElement("b"),
                    IdentifierPathElement(1),
                ]
            ),
        )
        self.assertEqual(stream.current, (1, TOKEN_IDENTINDEX, "1"))
