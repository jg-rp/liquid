# pylint: disable=missing-class-docstring missing-module-docstring
import unittest
from dataclasses import dataclass

from liquid.expression import ConditionalExpression
from liquid.expression import Expression
from liquid.expression import FilteredExpression
from liquid.expression import InfixExpression
from liquid.expression import PrefixExpression
from liquid.expression import IdentifierPathElement
from liquid.expression import Identifier
from liquid.expression import Filter
from liquid.expression import StringLiteral
from liquid.expression import IntegerLiteral
from liquid.expression import FloatLiteral
from liquid.expression import RangeLiteral
from liquid.expression import TRUE
from liquid.expression import FALSE

from liquid.expressions import parse_filtered_expression
from liquid.expressions import parse_conditional_expression
from liquid.expressions import parse_conditional_expression_with_parens

from liquid.exceptions import LiquidSyntaxError


@dataclass
class Case:
    description: str
    expression: str
    expect: Expression


class ParseFilteredExpressionTestCase(unittest.TestCase):
    test_cases = [
        Case(
            "string literal single quotes",
            "'foobar'",
            FilteredExpression(
                expression=StringLiteral("foobar"),
                filters=[],
            ),
        ),
        Case(
            "string literal double quotes",
            '"foobar"',
            FilteredExpression(
                expression=StringLiteral("foobar"),
                filters=[],
            ),
        ),
        Case(
            "integer literal",
            "7",
            FilteredExpression(
                expression=IntegerLiteral(7),
                filters=[],
            ),
        ),
        Case(
            "negative integer literal statement expression",
            "-7",
            FilteredExpression(
                expression=IntegerLiteral(-7),
                filters=[],
            ),
        ),
        Case(
            "float literal statement expression",
            "3.14",
            FilteredExpression(
                expression=FloatLiteral(3.14),
                filters=[],
            ),
        ),
        Case(
            "negative float literal statement expression",
            "-3.14",
            FilteredExpression(
                expression=FloatLiteral(-3.14),
                filters=[],
            ),
        ),
        Case(
            "literal true",
            "true",
            FilteredExpression(
                expression=TRUE,
                filters=[],
            ),
        ),
        Case(
            "literal false",
            "false",
            FilteredExpression(
                expression=FALSE,
                filters=[],
            ),
        ),
        Case(
            "range expression with integer start and stop",
            "(1..4)",
            FilteredExpression(
                expression=RangeLiteral(IntegerLiteral(1), IntegerLiteral(4)),
                filters=[],
            ),
        ),
        Case(
            "range expression with identifier start and stop",
            "(a..b.c)",
            FilteredExpression(
                expression=RangeLiteral(
                    Identifier(
                        path=[
                            IdentifierPathElement("a"),
                        ]
                    ),
                    Identifier(
                        path=[
                            IdentifierPathElement("b"),
                            IdentifierPathElement("c"),
                        ]
                    ),
                ),
                filters=[],
            ),
        ),
        Case(
            "single identifier statement expression",
            "collection",
            FilteredExpression(
                expression=Identifier(
                    path=[IdentifierPathElement("collection")],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier",
            "collection.products",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier by double quoted key",
            'collection["products"]',
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier by double quoted key followed by index",
            'collection["products"][0]',
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                        IdentifierPathElement(0),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier by double quoted key followed by identifier",
            'collection["products"].title',
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                        IdentifierPathElement("title"),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier by single quoted key",
            "collection['products']",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier with array index",
            "collection.products[0]",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                        IdentifierPathElement(0),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier with array index from variable",
            "collection.products[i]",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                        Identifier(
                            path=[IdentifierPathElement("i")],
                        ),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier with array index from chained identifier",
            "collection.products[some.['object'].count]",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("products"),
                        Identifier(
                            path=[
                                IdentifierPathElement("some"),
                                IdentifierPathElement("object"),
                                IdentifierPathElement("count"),
                            ],
                        ),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "chained identifier with object from chained identifier",
            "linklists[section.settings.menu]",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("linklists"),
                        Identifier(
                            path=[
                                IdentifierPathElement("section"),
                                IdentifierPathElement("settings"),
                                IdentifierPathElement("menu"),
                            ],
                        ),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            (
                "chained identifier with object from chained identifier "
                "and trailing identifier"
            ),
            "linklists[section.settings.menu].links",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("linklists"),
                        Identifier(
                            path=[
                                IdentifierPathElement("section"),
                                IdentifierPathElement("settings"),
                                IdentifierPathElement("menu"),
                            ],
                        ),
                        IdentifierPathElement("links"),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "string literal with filter",
            "'foo' | upcase",
            FilteredExpression(
                expression=StringLiteral("foo"),
                filters=[Filter(name="upcase", args=[])],
            ),
        ),
        Case(
            "string literal with filter and filter arguments",
            "'foo' | append: 'bar'",
            FilteredExpression(
                expression=StringLiteral("foo"),
                filters=[Filter(name="append", args=[StringLiteral("bar")])],
            ),
        ),
        Case(
            "identifier with filter",
            "collection.title | upcase",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("collection"),
                        IdentifierPathElement("title"),
                    ],
                ),
                filters=[Filter(name="upcase", args=[])],
            ),
        ),
        Case(
            "integer literal with filter and integer argument",
            "4 | at_least: 5",
            FilteredExpression(
                expression=IntegerLiteral(4),
                filters=[Filter(name="at_least", args=[IntegerLiteral(5)])],
            ),
        ),
        Case(
            "float literal with filter and float argument",
            "4.1 | divided_by: 5.2",
            FilteredExpression(
                expression=FloatLiteral(4.1),
                filters=[Filter(name="divided_by", args=[FloatLiteral(5.2)])],
            ),
        ),
        Case(
            "string literal with filter and string argument",
            "'foo' | append: 'bar'",
            FilteredExpression(
                expression=StringLiteral("foo"),
                filters=[Filter(name="append", args=[StringLiteral("bar")])],
            ),
        ),
        Case(
            "string literal with filter and identifier argument",
            "'foo' | append: collection.title",
            FilteredExpression(
                expression=StringLiteral("foo"),
                filters=[
                    Filter(
                        name="append",
                        args=[
                            Identifier(
                                path=[
                                    IdentifierPathElement("collection"),
                                    IdentifierPathElement("title"),
                                ],
                            )
                        ],
                    )
                ],
            ),
        ),
        Case(
            "string literal with filter and multiple arguments",
            '"Liquid" | slice: 2, 5',
            FilteredExpression(
                expression=StringLiteral("Liquid"),
                filters=[
                    Filter(
                        name="slice",
                        args=[
                            IntegerLiteral(2),
                            IntegerLiteral(5),
                        ],
                    )
                ],
            ),
        ),
        Case(
            "string literal with multiple filters",
            '"Liquid" | slice: 2, 5 | upcase',
            FilteredExpression(
                expression=StringLiteral("Liquid"),
                filters=[
                    Filter(
                        name="slice",
                        args=[
                            IntegerLiteral(2),
                            IntegerLiteral(5),
                        ],
                    ),
                    Filter(name="upcase", args=[]),
                ],
            ),
        ),
        Case(
            "inconsistent whitespace",
            ' "Liquid"   |slice: 2,5',
            FilteredExpression(
                expression=StringLiteral("Liquid"),
                filters=[
                    Filter(
                        name="slice",
                        args=[
                            IntegerLiteral(2),
                            IntegerLiteral(5),
                        ],
                    )
                ],
            ),
        ),
        Case(
            "negative array index",
            "products[-1]",
            FilteredExpression(
                expression=Identifier(
                    path=[
                        IdentifierPathElement("products"),
                        IdentifierPathElement(-1),
                    ],
                ),
                filters=[],
            ),
        ),
        Case(
            "filter with a named argument",
            "'Liquid' | default: 'hello', allow_false: true",
            FilteredExpression(
                expression=StringLiteral("Liquid"),
                filters=[
                    Filter(
                        name="default",
                        args=[StringLiteral("hello")],
                        kwargs={"allow_false": TRUE},
                    )
                ],
            ),
        ),
    ]

    def test_parse_filtered_expression(self):
        """Test that we can parse liquid statement expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                expr = parse_filtered_expression(case.expression)
                self.assertEqual(expr, case.expect)

    def test_parse_conditional_expression(self):
        """Test that the non-standard conditional expression parser is backwards
        compatible with standard filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                expr = parse_conditional_expression(case.expression)
                self.assertEqual(expr, case.expect)

    def test_parse_conditional_expression_with_parens(self):
        """Test that the non-standard conditional expression parser is backwards
        compatible with standard filtered expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                expr = parse_conditional_expression_with_parens(case.expression)
                self.assertEqual(expr, case.expect)

    def test_double_pipe(self):
        """Test that a two consecutive pipe characters raises a syntax error."""
        expr = r'"failure" || upcase'
        with self.assertRaises(LiquidSyntaxError) as raised:
            parse_filtered_expression(expr)
        self.assertEqual(
            str(raised.exception),
            "unexpected pipe or missing filter name, on line 1",
        )

    def test_double_comma(self):
        """Test that two consecutive comma characters raises a syntax error."""
        expr = r'"hello" | slice: 2,, 4'
        with self.assertRaises(LiquidSyntaxError) as raised:
            parse_filtered_expression(expr)
        self.assertEqual(str(raised.exception), "unexpected ',', on line 1")

    def test_double_colon(self):
        """Test that two consecutive colon characters raises a syntax error."""
        expr = r'"hello" | slice:: 2'
        with self.assertRaises(LiquidSyntaxError) as raised:
            parse_filtered_expression(expr)
        self.assertEqual(str(raised.exception), "unexpected ':', on line 1")

    def test_invalid_filter_name(self):
        """Test that an invalid filter name raises a syntax error."""
        expr = r'"hello" | £%1 '
        with self.assertRaises(LiquidSyntaxError) as raised:
            parse_filtered_expression(expr)
        self.assertEqual(str(raised.exception), "unexpected '£', on line 1")

    def test_missing_comma(self):
        """Test that a missing comma raises a syntax error."""
        expr = r'"hello" | slice: 1 3 '
        with self.assertRaises(LiquidSyntaxError) as raised:
            parse_filtered_expression(expr)
        self.assertEqual(
            str(raised.exception),
            "expected ',', found 'integer', on line 1",
        )

    def test_missing_colon(self):
        """Test that a missing colon raises a syntax error."""
        expr = r'"hello" | slice 1, 3 '
        with self.assertRaises(LiquidSyntaxError) as raised:
            parse_filtered_expression(expr)
        self.assertEqual(
            str(raised.exception), "expected ':', found 'integer', on line 1"
        )


class ParseConditionalExpressionTestCase(unittest.TestCase):
    """Test cases for the non-standard filtered expressions with inline conditions."""

    test_cases = [
        Case(
            description="string literal with condition",
            expression="'foo' if true",
            expect=ConditionalExpression(
                expression=FilteredExpression(StringLiteral("foo")),
                condition=TRUE,
            ),
        ),
        Case(
            description="string literal with condition and alternative",
            expression="'foo' if true else 'bar'",
            expect=ConditionalExpression(
                expression=FilteredExpression(StringLiteral("foo")),
                condition=TRUE,
                alternative=FilteredExpression(StringLiteral("bar")),
            ),
        ),
        Case(
            description="identifiers with condition and alternative",
            expression="products[0] if products else 'bar'",
            expect=ConditionalExpression(
                expression=FilteredExpression(
                    Identifier(
                        path=[
                            IdentifierPathElement("products"),
                            IdentifierPathElement(0),
                        ]
                    )
                ),
                condition=Identifier(path=[IdentifierPathElement("products")]),
                alternative=FilteredExpression(StringLiteral("bar")),
            ),
        ),
        Case(
            description="string literal with condition, alternative and filter",
            expression="'foo' | upcase if true else 'bar'",
            expect=ConditionalExpression(
                expression=FilteredExpression(
                    StringLiteral("foo"),
                    filters=[Filter(name="upcase", args=[])],
                ),
                condition=TRUE,
                alternative=FilteredExpression(StringLiteral("bar")),
                filters=[],
            ),
        ),
        Case(
            description=("string literal with condition and alternative filter"),
            expression="'foo' if true else 'bar' | upcase",
            expect=ConditionalExpression(
                expression=FilteredExpression(StringLiteral("foo")),
                condition=TRUE,
                alternative=FilteredExpression(
                    StringLiteral("bar"),
                    filters=[Filter(name="upcase", args=[])],
                ),
                filters=[],
            ),
        ),
        Case(
            description=("string literal with condition, alternative and tail filter"),
            expression="'foo' if true else 'bar' || append: 'baz' | upcase",
            expect=ConditionalExpression(
                expression=FilteredExpression(StringLiteral("foo")),
                condition=TRUE,
                alternative=FilteredExpression(StringLiteral("bar")),
                filters=[
                    Filter(name="append", args=[StringLiteral("baz")]),
                    Filter(name="upcase", args=[]),
                ],
            ),
        ),
        Case(
            description=("tail filter with keyword argument"),
            expression="'foo' if true else 'bar' || default: 'baz', allow_false:true",
            expect=ConditionalExpression(
                expression=FilteredExpression(StringLiteral("foo")),
                condition=TRUE,
                alternative=FilteredExpression(StringLiteral("bar")),
                filters=[
                    Filter(
                        name="default",
                        args=[StringLiteral("baz")],
                        kwargs={"allow_false": TRUE},
                    )
                ],
            ),
        ),
    ]

    def test_parse_conditional_expression(self):
        """Test that we can parse conditional expressions."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                expr = parse_conditional_expression(case.expression)
                self.assertEqual(expr, case.expect)

    def test_parse_conditional_expression_with_parens(self):
        """Test that the other conditional expression parser is backwards
        compatible with conditional expressions that don't support parentheses."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                expr = parse_conditional_expression_with_parens(case.expression)
                self.assertEqual(expr, case.expect)


class ParseConditionalNotExpressionTestCase(unittest.TestCase):
    """Test cases for the non-standard filtered expressions with inline conditions that
    support logical `not` and grouping with parentheses."""

    test_cases = [
        Case(
            description="string literal with condition",
            expression="'foo' if not true",
            expect=ConditionalExpression(
                expression=FilteredExpression(StringLiteral("foo")),
                condition=PrefixExpression(
                    "not",
                    right=TRUE,
                ),
            ),
        ),
        Case(
            description="string literal with condition and alternative",
            expression="'foo' if (true and false and false) or true else 'bar'",
            expect=ConditionalExpression(
                expression=FilteredExpression(StringLiteral("foo")),
                condition=InfixExpression(
                    left=InfixExpression(
                        left=TRUE,
                        operator="and",
                        right=InfixExpression(
                            left=FALSE,
                            operator="and",
                            right=FALSE,
                        ),
                    ),
                    operator="or",
                    right=TRUE,
                ),
                alternative=FilteredExpression(StringLiteral("bar")),
            ),
        ),
    ]

    def test_parse_conditional_expression_with_parens(self):
        """Test that the other conditional expression parser is backwards
        compatible with conditional expressions that don't support parentheses."""
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                expr = parse_conditional_expression_with_parens(case.expression)
                self.assertEqual(expr, case.expect)
