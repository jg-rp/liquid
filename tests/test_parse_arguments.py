"""Test cases for parsing list of positional and keyword arguments."""
import unittest

from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union

from liquid.expression import Expression
from liquid.expression import FloatLiteral
from liquid.expression import IdentifierPathElement
from liquid.expression import Identifier
from liquid.expression import IntegerLiteral
from liquid.expression import StringLiteral
from liquid.expression import FALSE
from liquid.expression import TRUE
from liquid.expression import NIL

from liquid.expressions import parse_call_arguments
from liquid.expressions import parse_keyword_arguments
from liquid.expressions import parse_macro_arguments

from liquid.expressions.arguments.lex import tokenize
from liquid.expressions.arguments.parse import parse_equals_separated_arguments
from liquid.expressions.stream import TokenStream

from liquid.exceptions import Error
from liquid.exceptions import LiquidSyntaxError

Arguments = List[Tuple[Optional[str], Optional[Expression]]]


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    expression: str
    expect: Union[Arguments, Error]


class ParseKeywordArgumentsTestCase(unittest.TestCase):
    """Test cases for parsing keyword arguments."""

    def test_parse_keywords(self) -> None:
        """Test that we can parse a list of keyword arguments."""
        test_cases = [
            Case(
                description="empty expression",
                expression="",
                expect=[],
            ),
            Case(
                description="string literal value",
                expression="val: 'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="no whitespace",
                expression="val:'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="extra whitespace",
                expression="val :    'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="newline",
                expression="val:\n'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="leading comma",
                expression=", val: 'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="trailing comma",
                expression="val: 'hello',",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="multiple arguments",
                expression="a: 'hello', b: 'goodbye', c: 'you'",
                expect=[
                    ("a", StringLiteral("hello")),
                    ("b", StringLiteral("goodbye")),
                    ("c", StringLiteral("you")),
                ],
            ),
            Case(
                description="literal types",
                expression="a: 'hello', b: false, c: true, d: nil, e: 1, f: 1.1",
                expect=[
                    ("a", StringLiteral("hello")),
                    ("b", FALSE),
                    ("c", TRUE),
                    ("d", NIL),
                    ("e", IntegerLiteral(1)),
                    ("f", FloatLiteral(1.1)),
                ],
            ),
            Case(
                description="identifiers",
                expression=(
                    "a: title, b: product.title, "
                    "c: products[0], d: products['foo'].title"
                ),
                expect=[
                    ("a", Identifier([IdentifierPathElement("title")])),
                    (
                        "b",
                        Identifier(
                            [
                                IdentifierPathElement("product"),
                                IdentifierPathElement("title"),
                            ]
                        ),
                    ),
                    (
                        "c",
                        Identifier(
                            [
                                IdentifierPathElement("products"),
                                IdentifierPathElement(0),
                            ]
                        ),
                    ),
                    (
                        "d",
                        Identifier(
                            [
                                IdentifierPathElement("products"),
                                IdentifierPathElement("foo"),
                                IdentifierPathElement("title"),
                            ]
                        ),
                    ),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                args = parse_keyword_arguments(case.expression)
                self.assertEqual(args, dict(case.expect))

    def test_parse_equals_separated_arguments(self) -> None:
        """Test that we can use `=` instead of `:` to separate key/value pairs."""
        expr = "a='hello', b=false, c=true, d=nil, e=1, f=1.1"
        expect = [
            ("a", StringLiteral("hello")),
            ("b", FALSE),
            ("c", TRUE),
            ("d", NIL),
            ("e", IntegerLiteral(1)),
            ("f", FloatLiteral(1.1)),
        ]
        args = dict(parse_equals_separated_arguments(TokenStream(tokenize(expr))))
        self.assertEqual(args, dict(expect))

    def test_missing_comma(self) -> None:
        """Test that we handle missing commas."""
        expr = "a: 'hello' b: 'goodbye'"
        with self.assertRaises(LiquidSyntaxError):
            parse_keyword_arguments(expr)

    def test_too_many_commas(self) -> None:
        """Test that we handle excess commas."""
        expr = "a: 'hello',, b: 'goodbye'"
        with self.assertRaises(LiquidSyntaxError):
            parse_keyword_arguments(expr)

    def test_missing_colon(self) -> None:
        """Test that we handle missing colons."""
        expr = "a 'hello'"
        with self.assertRaises(LiquidSyntaxError):
            parse_keyword_arguments(expr)

    def test_too_many_colon(self) -> None:
        """Test that we handle excess colons."""
        expr = "a:: 'hello'"
        with self.assertRaises(LiquidSyntaxError):
            parse_keyword_arguments(expr)


class ParseCallArgumentsTestCase(unittest.TestCase):
    """Test cases for parsing call-style argument lists."""

    def test_parse_call_arguments(self) -> None:
        """Test that we can parse a list of positional and/or keyword arguments."""
        test_cases = [
            Case(
                description="empty expression",
                expression="",
                expect=[],
            ),
            Case(
                description="string literal value",
                expression="val: 'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="no whitespace",
                expression="val:'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="extra whitespace",
                expression="val :    'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="multiple arguments",
                expression="a: 'hello', b: 'goodbye', c: 'you'",
                expect=[
                    ("a", StringLiteral("hello")),
                    ("b", StringLiteral("goodbye")),
                    ("c", StringLiteral("you")),
                ],
            ),
            Case(
                description="literal types",
                expression="a: 'hello', b: false, c: true, d: nil, e: 1, f: 1.1",
                expect=[
                    ("a", StringLiteral("hello")),
                    ("b", FALSE),
                    ("c", TRUE),
                    ("d", NIL),
                    ("e", IntegerLiteral(1)),
                    ("f", FloatLiteral(1.1)),
                ],
            ),
            Case(
                description="identifiers",
                expression=(
                    "a: title, b: product.title, c: products[0], d: products[0].title"
                ),
                expect=[
                    ("a", Identifier([IdentifierPathElement("title")])),
                    (
                        "b",
                        Identifier(
                            [
                                IdentifierPathElement("product"),
                                IdentifierPathElement("title"),
                            ]
                        ),
                    ),
                    (
                        "c",
                        Identifier(
                            [
                                IdentifierPathElement("products"),
                                IdentifierPathElement(0),
                            ]
                        ),
                    ),
                    (
                        "d",
                        Identifier(
                            [
                                IdentifierPathElement("products"),
                                IdentifierPathElement(0),
                                IdentifierPathElement("title"),
                            ]
                        ),
                    ),
                ],
            ),
            Case(
                description="positional argument",
                expression="'hello'",
                expect=[(None, StringLiteral("hello"))],
            ),
            Case(
                description="multiple positional arguments",
                expression="'hello', 'you'",
                expect=[(None, StringLiteral("hello")), (None, StringLiteral("you"))],
            ),
            Case(
                description="positional no whitespace",
                expression="'hello','you'",
                expect=[(None, StringLiteral("hello")), (None, StringLiteral("you"))],
            ),
            Case(
                description="positional extra whitespace",
                expression="'hello'  ,    'you'",
                expect=[(None, StringLiteral("hello")), (None, StringLiteral("you"))],
            ),
            Case(
                description="positional argument followed by keyword",
                expression="'hello', greeting: 'you'",
                expect=[
                    (None, StringLiteral("hello")),
                    ("greeting", StringLiteral("you")),
                ],
            ),
            Case(
                description="keyword argument followed by positional",
                expression="greeting: 'you', 'hello'",
                expect=[
                    ("greeting", StringLiteral("you")),
                    (None, StringLiteral("hello")),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                expr = "'func' " + case.expression  # pretend macro name
                _, args = parse_call_arguments(expr)
                self.assertEqual(args, case.expect)

    def test_missing_comma(self) -> None:
        """Test that we handle missing commas."""
        expr = "'func' a: 'hello' b: 'goodbye'"
        with self.assertRaises(LiquidSyntaxError):
            parse_call_arguments(expr)

    def test_too_many_commas(self) -> None:
        """Test that we handle excess commas."""
        expr = "'func' a: 'hello',, b: 'goodbye'"
        with self.assertRaises(LiquidSyntaxError):
            parse_call_arguments(expr)


class ParseMacroArgumentsTestCase(unittest.TestCase):
    """Test cases for parsing macro-style argument lists."""

    def test_parse_call_arguments(self) -> None:
        """Test that we can parse a list of positional and/or keyword arguments."""
        test_cases = [
            Case(
                description="empty expression",
                expression="",
                expect=[],
            ),
            Case(
                description="string literal value",
                expression="val: 'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="no whitespace",
                expression="val:'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="extra whitespace",
                expression="val :    'hello'",
                expect=[("val", StringLiteral("hello"))],
            ),
            Case(
                description="multiple arguments",
                expression="a: 'hello', b: 'goodbye', c: 'you'",
                expect=[
                    ("a", StringLiteral("hello")),
                    ("b", StringLiteral("goodbye")),
                    ("c", StringLiteral("you")),
                ],
            ),
            Case(
                description="literal types",
                expression="a: 'hello', b: false, c: true, d: nil, e: 1, f: 1.1",
                expect=[
                    ("a", StringLiteral("hello")),
                    ("b", FALSE),
                    ("c", TRUE),
                    ("d", NIL),
                    ("e", IntegerLiteral(1)),
                    ("f", FloatLiteral(1.1)),
                ],
            ),
            Case(
                description="identifiers",
                expression=(
                    "a: title, b: product.title, c: products[0], d: products[0].title"
                ),
                expect=[
                    ("a", Identifier([IdentifierPathElement("title")])),
                    (
                        "b",
                        Identifier(
                            [
                                IdentifierPathElement("product"),
                                IdentifierPathElement("title"),
                            ]
                        ),
                    ),
                    (
                        "c",
                        Identifier(
                            [
                                IdentifierPathElement("products"),
                                IdentifierPathElement(0),
                            ]
                        ),
                    ),
                    (
                        "d",
                        Identifier(
                            [
                                IdentifierPathElement("products"),
                                IdentifierPathElement(0),
                                IdentifierPathElement("title"),
                            ]
                        ),
                    ),
                ],
            ),
            Case(
                description="identifier without a default value",
                expression="name",
                expect=[("name", NIL)],
            ),
            Case(
                description="multiple identifiers without a default value",
                expression="name, greeting",
                expect=[("name", NIL), ("greeting", NIL)],
            ),
            Case(
                description=(
                    "identifier without default followed by identifier with a default"
                ),
                expression="name, greeting: 'hello'",
                expect=[("name", NIL), ("greeting", StringLiteral("hello"))],
            ),
            Case(
                description=(
                    "identifier with a default followed by identifier without default"
                ),
                expression="greeting: 'hello', name",
                expect=[("greeting", StringLiteral("hello")), ("name", NIL)],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                expr = "'func' " + case.expression  # pretend macro name
                name, args = parse_macro_arguments(expr)
                self.assertEqual(name, "func")
                self.assertEqual(args, case.expect)

    def test_missing_comma(self) -> None:
        """Test that we handle missing commas."""
        expr = "'func' a: 'hello' b: 'goodbye'"
        with self.assertRaises(LiquidSyntaxError):
            parse_macro_arguments(expr)

    def test_too_many_commas(self) -> None:
        """Test that we handle excess commas."""
        expr = "'func' a: 'hello',, b: 'goodbye'"
        with self.assertRaises(LiquidSyntaxError):
            parse_macro_arguments(expr)
