"""Liquid expression parser test cases."""

import unittest
from typing import NamedTuple, Any

from liquid.expression import FilteredExpression
from liquid.expression import BooleanExpression
from liquid.expression import AssignmentExpression
from liquid.expression import LoopExpression
from liquid.expression import IdentifierPathElement
from liquid.expression import Identifier
from liquid.expression import Boolean
from liquid.expression import Filter
from liquid.expression import StringLiteral
from liquid.expression import IntegerLiteral
from liquid.expression import FloatLiteral
from liquid.expression import PrefixExpression
from liquid.expression import InfixExpression

from liquid.token import Token
from liquid.token import TOKEN_INITIAL

from liquid.stream import TokenStream

from liquid.lex import tokenize_loop_expression
from liquid.lex import tokenize_filtered_expression
from liquid.lex import tokenize_boolean_expression
from liquid.lex import tokenize_assignment_expression

from liquid.parse import parse_filtered_expression
from liquid.parse import parse_boolean_expression
from liquid.parse import parse_assignment_expression
from liquid.parse import parse_loop_expression


class Case(NamedTuple):
    """Subtest helper"""

    description: str
    expression: str
    expect: Any


MockToken = Token(1, TOKEN_INITIAL, "MOCK")


class LiquidFilteredExpressionParserTestCase(unittest.TestCase):
    """Liquid expression parser test cases."""

    def _test(self, test_cases, lex_func, parse_func):
        """Helper method for testing lists of Cases."""

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = TokenStream(lex_func(case.expression))
                expr = parse_func(tokens)
                self.assertEqual(expr, case.expect)

    def test_parse_filtered_expression(self):
        """Test that we can parse liquid statement expressions."""
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
                    expression=PrefixExpression(
                        "-",
                        right=IntegerLiteral(7),
                    ),
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
                    expression=PrefixExpression(
                        "-",
                        right=FloatLiteral(3.14),
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
                "chained identifier with object from chained identifier and trailing identifier",
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
        ]

        self._test(test_cases, tokenize_filtered_expression, parse_filtered_expression)

    def test_parse_boolean_expression(self):
        """Test that we can parse boolean expressions."""
        test_cases = [
            Case(
                "string literal double quotes",
                '"foobar"',
                BooleanExpression(
                    expression=StringLiteral("foobar"),
                ),
            ),
            Case(
                "integer literal",
                "7",
                BooleanExpression(
                    expression=IntegerLiteral(7),
                ),
            ),
            Case(
                "negative integer literal statement expression",
                "-7",
                BooleanExpression(
                    expression=PrefixExpression(
                        "-",
                        right=IntegerLiteral(7),
                    ),
                ),
            ),
            Case(
                "float literal statement expression",
                "3.14",
                BooleanExpression(
                    expression=FloatLiteral(3.14),
                ),
            ),
            Case(
                "negative float literal statement expression",
                "-3.14",
                BooleanExpression(
                    expression=PrefixExpression(
                        "-",
                        right=FloatLiteral(3.14),
                    ),
                ),
            ),
            Case(
                "single identifier statement expression",
                "collection",
                BooleanExpression(
                    expression=Identifier(
                        path=[IdentifierPathElement("collection")],
                    ),
                ),
            ),
            Case(
                "chained identifier",
                "collection.products",
                BooleanExpression(
                    expression=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                ),
            ),
            Case(
                "keyword true",
                "true",
                BooleanExpression(
                    expression=Boolean(True),
                ),
            ),
            Case(
                "keyword false",
                "false",
                BooleanExpression(
                    expression=Boolean(False),
                ),
            ),
            Case(
                "boolean equality",
                "true == true",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="==",
                        right=Boolean(True),
                    ),
                ),
            ),
            Case(
                "boolean inequality",
                "true != false",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="!=",
                        right=Boolean(False),
                    ),
                ),
            ),
            Case(
                "boolean inequality alternate",
                "true <> false",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="<>",
                        right=Boolean(False),
                    ),
                ),
            ),
            Case(
                "identifier greater than literal",
                "user.age > 21",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[
                                IdentifierPathElement("user"),
                                IdentifierPathElement("age"),
                            ],
                        ),
                        operator=">",
                        right=IntegerLiteral(21),
                    ),
                ),
            ),
            Case(
                "identifier less than literal",
                "age < 18",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[IdentifierPathElement("age")],
                        ),
                        operator="<",
                        right=IntegerLiteral(18),
                    ),
                ),
            ),
            Case(
                "identifier less than or equal to literal",
                "age <= 18",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[IdentifierPathElement("age")],
                        ),
                        operator="<=",
                        right=IntegerLiteral(18),
                    ),
                ),
            ),
            Case(
                "identifier greater than or equal to literal",
                "age >= 18",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[IdentifierPathElement("age")],
                        ),
                        operator=">=",
                        right=IntegerLiteral(18),
                    ),
                ),
            ),
            Case(
                "boolean or boolean",
                "true or false",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="or",
                        right=Boolean(False),
                    ),
                ),
            ),
            Case(
                "identifier contains string",
                "product.tags contains 'sale'",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[
                                IdentifierPathElement("product"),
                                IdentifierPathElement("tags"),
                            ],
                        ),
                        operator="contains",
                        right=StringLiteral("sale"),
                    ),
                ),
            ),
        ]

        self._test(test_cases, tokenize_boolean_expression, parse_boolean_expression)

    def test_parse_boolean_expression_precedence(self):
        """Test that we get the expected precedence when parsing boolean expressions."""
        test_cases = [
            Case(
                "boolean and logic operators",
                "true and false and false or true",
                "(True and (False and (False or True)))",
            ),
            Case(
                "equality and logic operators",
                "user.name == 'bob' and user.age < 50 or collection.title == 'offers'",
                "((user.name == 'bob') and ((user.age < 50) or (collection.title == 'offers')))",
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = TokenStream(tokenize_boolean_expression(case.expression))
                expr = parse_boolean_expression(tokens)
                self.assertEqual(str(expr), case.expect)

    def test_parse_assignment_expression(self):
        """Test that we can parse assignment expressions."""
        test_cases = [
            Case(
                "assign a string literal",
                "some = 'foo'",
                AssignmentExpression(
                    name="some",
                    expression=FilteredExpression(
                        expression=StringLiteral(value="foo"),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign an integer literal",
                "some = 5",
                AssignmentExpression(
                    name="some",
                    expression=FilteredExpression(
                        expression=IntegerLiteral(value=5),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign a float literal",
                "some = 5.6",
                AssignmentExpression(
                    name="some",
                    expression=FilteredExpression(
                        expression=FloatLiteral(value=5.6),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign a negative integer literal",
                "some = -5.6",
                AssignmentExpression(
                    name="some",
                    expression=FilteredExpression(
                        expression=PrefixExpression(
                            operator="-",
                            right=FloatLiteral(value=5.6),
                        ),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign a boolean",
                "some = true",
                AssignmentExpression(
                    name="some",
                    expression=FilteredExpression(
                        expression=Boolean(value=True),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign with a filter",
                'fruits = "apples, oranges, peaches, tomatoes" | split: ", "',
                AssignmentExpression(
                    name="fruits",
                    expression=FilteredExpression(
                        expression=StringLiteral(
                            value="apples, oranges, peaches, tomatoes",
                        ),
                        filters=[Filter(name="split", args=[StringLiteral(", ")])],
                    ),
                ),
            ),
            Case(
                "assign with multiple filters and identifier arguments",
                "everything = fruits | concat: vegetables | concat: furniture",
                AssignmentExpression(
                    name="everything",
                    expression=FilteredExpression(
                        expression=Identifier(
                            path=[IdentifierPathElement("fruits")],
                        ),
                        filters=[
                            Filter(
                                name="concat",
                                args=[
                                    Identifier(
                                        path=[IdentifierPathElement("vegetables")],
                                    )
                                ],
                            ),
                            Filter(
                                name="concat",
                                args=[
                                    Identifier(
                                        path=[IdentifierPathElement("furniture")],
                                    )
                                ],
                            ),
                        ],
                    ),
                ),
            ),
        ]

        self._test(
            test_cases, tokenize_assignment_expression, parse_assignment_expression
        )

    def test_parse_loop_expression(self):
        """Test that we can parse loop expressions."""
        test_cases = [
            Case(
                "item in array",
                "product in collection.products",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                ),
            ),
            Case(
                "item in array with integer literal limit",
                "product in collection.products limit:5",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                    limit=IntegerLiteral(5),
                ),
            ),
            Case(
                "item in array with identifier limit",
                "product in collection.products limit:max",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                    limit=Identifier(path=[IdentifierPathElement("max")]),
                ),
            ),
            Case(
                "item in array with integer literal offset",
                "product in collection.products offset:2",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                    offset=IntegerLiteral(2),
                ),
            ),
            Case(
                "item in array with integer literal offset and limit",
                "product in collection.products limit:5 offset:2",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                    limit=IntegerLiteral(5),
                    offset=IntegerLiteral(2),
                ),
            ),
            Case(
                "item in array with integer literal offset and limit out of order",
                "product in collection.products offset:2 limit:5",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                    limit=IntegerLiteral(5),
                    offset=IntegerLiteral(2),
                ),
            ),
            Case(
                "item in array reversed",
                "product in collection.products reversed",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                    reversed_=True,
                ),
            ),
            Case(
                "item in array with all options",
                "product in collection.products offset:2 limit:5 reversed",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                    limit=IntegerLiteral(5),
                    offset=IntegerLiteral(2),
                    reversed_=True,
                ),
            ),
            Case(
                "item in range with integer literal start and stop",
                "product in (1..10)",
                LoopExpression(
                    name="product",
                    start=IntegerLiteral(1),
                    stop=IntegerLiteral(10),
                ),
            ),
            Case(
                "item in range with integer literal start and identifier stop",
                "product in (1..collection.products.size)",
                LoopExpression(
                    name="product",
                    start=IntegerLiteral(1),
                    stop=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                            IdentifierPathElement("size"),
                        ],
                    ),
                ),
            ),
            Case(
                "item in range with integer identifier start and stop",
                "product in (num..collection.products.size)",
                LoopExpression(
                    name="product",
                    start=Identifier(path=[IdentifierPathElement("num")]),
                    stop=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                            IdentifierPathElement("size"),
                        ],
                    ),
                ),
            ),
            Case(
                "item in range with options",
                "product in (1..10) offset:2 limit:5 reversed",
                LoopExpression(
                    name="product",
                    start=IntegerLiteral(1),
                    stop=IntegerLiteral(10),
                    limit=IntegerLiteral(5),
                    offset=IntegerLiteral(2),
                    reversed_=True,
                ),
            ),
        ]

        self._test(test_cases, tokenize_loop_expression, parse_loop_expression)
