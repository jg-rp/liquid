"""Liquid expression parser test cases."""

import unittest
from typing import NamedTuple, Any

from liquid.environment import Environment
from liquid.expression import (
    FilteredExpression,
    BooleanExpression,
    AssignmentExpression,
    LoopExpression,
    IdentifierPathElement,
    Identifier,
    Boolean,
    Filter,
    StringLiteral,
    IntegerLiteral,
    FloatLiteral,
    PrefixExpression,
    InfixExpression,
)
from liquid.token import (
    Token,
    TOKEN_INITIAL,
    TOKEN_LITERAL,
    TOKEN_INTEGER,
    TOKEN_NEGATIVE,
    TOKEN_FLOAT,
    TOKEN_IDENTIFIER,
    TOKEN_STRING,
    TOKEN_TRUE,
    TOKEN_FALSE,
)
from liquid.lex import (
    tokenize_identifier,
    tokenize_loop_expression,
    tokenize_include_expression,
    tokenize_filtered_expression,
    tokenize_boolean_expression,
    tokenize_assignment_expression,
)

from liquid.parse import (
    parse_filtered_expression,
    parse_boolean_expression,
    parse_assignment_expression,
    parse_loop_expression,
)

from liquid.stream import TokenStream


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
                    expression=StringLiteral(
                        Token(1, TOKEN_LITERAL, "foobar"), "foobar"
                    ),
                    filters=[],
                ),
            ),
            Case(
                "string literal double quotes",
                '"foobar"',
                FilteredExpression(
                    expression=StringLiteral(
                        Token(1, TOKEN_LITERAL, "foobar"), "foobar"
                    ),
                    filters=[],
                ),
            ),
            Case(
                "integer literal",
                "7",
                FilteredExpression(
                    expression=IntegerLiteral(Token(1, TOKEN_INTEGER, "7"), 7),
                    filters=[],
                ),
            ),
            Case(
                "negative integer literal statement expression",
                "-7",
                FilteredExpression(
                    expression=PrefixExpression(
                        Token(1, TOKEN_NEGATIVE, "-"),
                        "-",
                        right=IntegerLiteral(Token(1, TOKEN_INTEGER, "7"), 7),
                    ),
                    filters=[],
                ),
            ),
            Case(
                "float literal statement expression",
                "3.14",
                FilteredExpression(
                    expression=FloatLiteral(Token(1, TOKEN_FLOAT, "3.14"), 3.14),
                    filters=[],
                ),
            ),
            Case(
                "negative float literal statement expression",
                "-3.14",
                FilteredExpression(
                    expression=PrefixExpression(
                        Token(1, TOKEN_NEGATIVE, "-"),
                        "-",
                        right=FloatLiteral(Token(1, TOKEN_FLOAT, "3.14"), 3.14),
                    ),
                    filters=[],
                ),
            ),
            Case(
                "single identifier statement expression",
                "collection",
                FilteredExpression(
                    expression=Identifier(
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[IdentifierPathElement(MockToken, "collection")],
                    ),
                    filters=[],
                ),
            ),
            Case(
                "chained identifier",
                "collection.products",
                FilteredExpression(
                    expression=Identifier(
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
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
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
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
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                            IdentifierPathElement(MockToken, 0),
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
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                            IdentifierPathElement(MockToken, "title"),
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
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
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
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                            IdentifierPathElement(MockToken, 0),
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
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                            Identifier(
                                tok=Token(1, TOKEN_IDENTIFIER, value="i"),
                                path=[IdentifierPathElement(MockToken, "i")],
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
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                            Identifier(
                                tok=Token(1, TOKEN_IDENTIFIER, value="some"),
                                path=[
                                    IdentifierPathElement(MockToken, "some"),
                                    IdentifierPathElement(MockToken, "object"),
                                    IdentifierPathElement(MockToken, "count"),
                                ],
                            ),
                        ],
                    ),
                    filters=[],
                ),
            ),
            Case(
                "string literal with filter",
                "'foo' | upcase",
                FilteredExpression(
                    expression=StringLiteral(MockToken, "foo"),
                    filters=[Filter(name="upcase", args=[])],
                ),
            ),
            Case(
                "identifier with filter",
                "collection.title | upcase",
                FilteredExpression(
                    expression=Identifier(
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "title"),
                        ],
                    ),
                    filters=[Filter(name="upcase", args=[])],
                ),
            ),
            Case(
                "integer literal with filter and integer argument",
                "4 | at_least: 5",
                FilteredExpression(
                    expression=IntegerLiteral(MockToken, 4),
                    filters=[
                        Filter(name="at_least", args=[IntegerLiteral(MockToken, 5)])
                    ],
                ),
            ),
            Case(
                "float literal with filter and float argument",
                "4.1 | divided_by: 5.2",
                FilteredExpression(
                    expression=FloatLiteral(MockToken, 4.1),
                    filters=[
                        Filter(name="divided_by", args=[FloatLiteral(MockToken, 5.2)])
                    ],
                ),
            ),
            Case(
                "string literal with filter and string argument",
                "'foo' | append: 'bar'",
                FilteredExpression(
                    expression=StringLiteral(MockToken, "foo"),
                    filters=[
                        Filter(name="append", args=[StringLiteral(MockToken, "bar")])
                    ],
                ),
            ),
            Case(
                "string literal with filter and identifier argument",
                "'foo' | append: collection.title",
                FilteredExpression(
                    expression=StringLiteral(MockToken, "foo"),
                    filters=[
                        Filter(
                            name="append",
                            args=[
                                Identifier(
                                    tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                                    path=[
                                        IdentifierPathElement(MockToken, "collection"),
                                        IdentifierPathElement(MockToken, "title"),
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
                    expression=StringLiteral(MockToken, "Liquid"),
                    filters=[
                        Filter(
                            name="slice",
                            args=[
                                IntegerLiteral(MockToken, 2),
                                IntegerLiteral(MockToken, 5),
                            ],
                        )
                    ],
                ),
            ),
            Case(
                "string literal with multiple filters",
                '"Liquid" | slice: 2, 5 | upcase',
                FilteredExpression(
                    expression=StringLiteral(MockToken, "Liquid"),
                    filters=[
                        Filter(
                            name="slice",
                            args=[
                                IntegerLiteral(MockToken, 2),
                                IntegerLiteral(MockToken, 5),
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
                    expression=StringLiteral(MockToken, "Liquid"),
                    filters=[
                        Filter(
                            name="slice",
                            args=[
                                IntegerLiteral(MockToken, 2),
                                IntegerLiteral(MockToken, 5),
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
                    tok=MockToken,
                    expression=StringLiteral(
                        Token(1, TOKEN_STRING, '"foobar"'), "foobar"
                    ),
                ),
            ),
            Case(
                "integer literal",
                "7",
                BooleanExpression(
                    tok=MockToken,
                    expression=IntegerLiteral(Token(1, TOKEN_INTEGER, "7"), 7),
                ),
            ),
            Case(
                "negative integer literal statement expression",
                "-7",
                BooleanExpression(
                    tok=MockToken,
                    expression=PrefixExpression(
                        Token(1, TOKEN_NEGATIVE, "-"),
                        "-",
                        right=IntegerLiteral(Token(1, TOKEN_INTEGER, "7"), 7),
                    ),
                ),
            ),
            Case(
                "float literal statement expression",
                "3.14",
                BooleanExpression(
                    tok=MockToken,
                    expression=FloatLiteral(Token(1, TOKEN_FLOAT, "3.14"), 3.14),
                ),
            ),
            Case(
                "negative float literal statement expression",
                "-3.14",
                BooleanExpression(
                    tok=MockToken,
                    expression=PrefixExpression(
                        Token(1, TOKEN_NEGATIVE, "-"),
                        "-",
                        right=FloatLiteral(Token(1, TOKEN_FLOAT, "3.14"), 3.14),
                    ),
                ),
            ),
            Case(
                "single identifier statement expression",
                "collection",
                BooleanExpression(
                    tok=MockToken,
                    expression=Identifier(
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[IdentifierPathElement(MockToken, "collection")],
                    ),
                ),
            ),
            Case(
                "chained identifier",
                "collection.products",
                BooleanExpression(
                    tok=MockToken,
                    expression=Identifier(
                        tok=Token(1, TOKEN_IDENTIFIER, "collection"),
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                        ],
                    ),
                ),
            ),
            Case(
                "keyword true",
                "true",
                BooleanExpression(
                    tok=MockToken,
                    expression=Boolean(Token(1, TOKEN_TRUE, "true"), True),
                ),
            ),
            Case(
                "keyword false",
                "false",
                BooleanExpression(
                    tok=MockToken,
                    expression=Boolean(Token(1, TOKEN_FALSE, "false"), False),
                ),
            ),
            Case(
                "boolean equality",
                "true == true",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_TRUE, "true"),
                        left=Boolean(Token(1, TOKEN_TRUE, "true"), True),
                        operator="==",
                        right=Boolean(Token(1, TOKEN_TRUE, "true"), True),
                    ),
                ),
            ),
            Case(
                "boolean inequality",
                "true != false",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_TRUE, "true"),
                        left=Boolean(Token(1, TOKEN_TRUE, "true"), True),
                        operator="!=",
                        right=Boolean(Token(1, TOKEN_TRUE, "false"), False),
                    ),
                ),
            ),
            Case(
                "boolean inequality alternate",
                "true <> false",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_TRUE, "true"),
                        left=Boolean(Token(1, TOKEN_TRUE, "true"), True),
                        operator="<>",
                        right=Boolean(Token(1, TOKEN_TRUE, "false"), False),
                    ),
                ),
            ),
            Case(
                "identifier greater than literal",
                "user.age > 21",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_IDENTIFIER, "user"),
                        left=Identifier(
                            Token(1, TOKEN_IDENTIFIER, "user"),
                            path=[
                                IdentifierPathElement(MockToken, "user"),
                                IdentifierPathElement(MockToken, "age"),
                            ],
                        ),
                        operator=">",
                        right=IntegerLiteral(Token(1, TOKEN_INTEGER, "21"), 21),
                    ),
                ),
            ),
            Case(
                "identifier less than literal",
                "age < 18",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_IDENTIFIER, "age"),
                        left=Identifier(
                            Token(1, TOKEN_IDENTIFIER, "age"),
                            path=[IdentifierPathElement(MockToken, "age")],
                        ),
                        operator="<",
                        right=IntegerLiteral(Token(1, TOKEN_INTEGER, "18"), 18),
                    ),
                ),
            ),
            Case(
                "identifier less than or equal to literal",
                "age <= 18",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_IDENTIFIER, "age"),
                        left=Identifier(
                            Token(1, TOKEN_IDENTIFIER, "age"),
                            path=[IdentifierPathElement(MockToken, "age")],
                        ),
                        operator="<=",
                        right=IntegerLiteral(Token(1, TOKEN_INTEGER, "18"), 18),
                    ),
                ),
            ),
            Case(
                "identifier greater than or equal to literal",
                "age >= 18",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_IDENTIFIER, "age"),
                        left=Identifier(
                            Token(1, TOKEN_IDENTIFIER, "age"),
                            path=[IdentifierPathElement(MockToken, "age")],
                        ),
                        operator=">=",
                        right=IntegerLiteral(Token(1, TOKEN_INTEGER, "18"), 18),
                    ),
                ),
            ),
            Case(
                "boolean or boolean",
                "true or false",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_TRUE, "true"),
                        left=Boolean(Token(1, TOKEN_TRUE, "true"), True),
                        operator="or",
                        right=Boolean(Token(1, TOKEN_FALSE, "false"), False),
                    ),
                ),
            ),
            Case(
                "identifier contains string",
                "product.tags contains 'sale'",
                BooleanExpression(
                    tok=MockToken,
                    expression=InfixExpression(
                        Token(1, TOKEN_IDENTIFIER, "product"),
                        left=Identifier(
                            MockToken,
                            path=[
                                IdentifierPathElement(MockToken, "product"),
                                IdentifierPathElement(MockToken, "tags"),
                            ],
                        ),
                        operator="contains",
                        right=StringLiteral(MockToken, "sale"),
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
                    MockToken,
                    name="some",
                    expression=FilteredExpression(
                        expression=StringLiteral(
                            tok=Token(1, TOKEN_STRING, "foo"), value="foo"
                        ),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign an integer literal",
                "some = 5",
                AssignmentExpression(
                    MockToken,
                    name="some",
                    expression=FilteredExpression(
                        expression=IntegerLiteral(
                            tok=Token(1, TOKEN_INTEGER, "5"), value=5
                        ),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign a float literal",
                "some = 5.6",
                AssignmentExpression(
                    MockToken,
                    name="some",
                    expression=FilteredExpression(
                        expression=FloatLiteral(
                            tok=Token(1, TOKEN_FLOAT, "5.6"), value=5.6
                        ),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign a negative integer literal",
                "some = -5.6",
                AssignmentExpression(
                    MockToken,
                    name="some",
                    expression=FilteredExpression(
                        expression=PrefixExpression(
                            tok=MockToken,
                            operator="-",
                            right=FloatLiteral(
                                tok=Token(1, TOKEN_FLOAT, "5.6"), value=5.6
                            ),
                        ),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign a boolean",
                "some = true",
                AssignmentExpression(
                    MockToken,
                    name="some",
                    expression=FilteredExpression(
                        expression=Boolean(
                            tok=Token(1, TOKEN_TRUE, "true"), value=True
                        ),
                        filters=[],
                    ),
                ),
            ),
            Case(
                "assign with a filter",
                'fruits = "apples, oranges, peaches, tomatoes" | split: ", "',
                AssignmentExpression(
                    MockToken,
                    name="fruits",
                    expression=FilteredExpression(
                        expression=StringLiteral(
                            tok=Token(
                                1, TOKEN_STRING, "apples, oranges, peaches, tomatoes"
                            ),
                            value="apples, oranges, peaches, tomatoes",
                        ),
                        filters=[
                            Filter(name="split", args=[StringLiteral(MockToken, ", ")])
                        ],
                    ),
                ),
            ),
            Case(
                "assign with multiple filters and identifier arguments",
                "everything = fruits | concat: vegetables | concat: furniture",
                AssignmentExpression(
                    MockToken,
                    name="everything",
                    expression=FilteredExpression(
                        expression=Identifier(
                            tok=Token(1, TOKEN_IDENTIFIER, "fruits"),
                            path=[IdentifierPathElement(MockToken, "fruits")],
                        ),
                        filters=[
                            Filter(
                                name="concat",
                                args=[
                                    Identifier(
                                        Token(1, TOKEN_IDENTIFIER, "vegetables"),
                                        path=[
                                            IdentifierPathElement(
                                                MockToken, "vegetables"
                                            )
                                        ],
                                    )
                                ],
                            ),
                            Filter(
                                name="concat",
                                args=[
                                    Identifier(
                                        Token(1, TOKEN_IDENTIFIER, "furniture"),
                                        path=[
                                            IdentifierPathElement(
                                                MockToken, "furniture"
                                            )
                                        ],
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
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
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
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                        ],
                    ),
                    limit=IntegerLiteral(MockToken, 5),
                ),
            ),
            Case(
                "item in array with identifier limit",
                "product in collection.products limit:max",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                        ],
                    ),
                    limit=Identifier(
                        MockToken, path=[IdentifierPathElement(MockToken, "max")]
                    ),
                ),
            ),
            Case(
                "item in array with integer literal offset",
                "product in collection.products offset:2",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                        ],
                    ),
                    offset=IntegerLiteral(MockToken, 2),
                ),
            ),
            Case(
                "item in array with integer literal offset and limit",
                "product in collection.products limit:5 offset:2",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                        ],
                    ),
                    limit=IntegerLiteral(MockToken, 5),
                    offset=IntegerLiteral(MockToken, 2),
                ),
            ),
            Case(
                "item in array with integer literal offset and limit out of order",
                "product in collection.products offset:2 limit:5",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                        ],
                    ),
                    limit=IntegerLiteral(MockToken, 5),
                    offset=IntegerLiteral(MockToken, 2),
                ),
            ),
            Case(
                "item in array reversed",
                "product in collection.products reversed",
                LoopExpression(
                    name="product",
                    identifier=Identifier(
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
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
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                        ],
                    ),
                    limit=IntegerLiteral(MockToken, 5),
                    offset=IntegerLiteral(MockToken, 2),
                    reversed_=True,
                ),
            ),
            Case(
                "item in range with integer literal start and stop",
                "product in (1..10)",
                LoopExpression(
                    name="product",
                    start=IntegerLiteral(MockToken, 1),
                    stop=IntegerLiteral(MockToken, 10),
                ),
            ),
            Case(
                "item in range with integer literal start and identifier stop",
                "product in (1..collection.products.size)",
                LoopExpression(
                    name="product",
                    start=IntegerLiteral(MockToken, 1),
                    stop=Identifier(
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                            IdentifierPathElement(MockToken, "size"),
                        ],
                    ),
                ),
            ),
            Case(
                "item in range with integer identifier start and stop",
                "product in (num..collection.products.size)",
                LoopExpression(
                    name="product",
                    start=Identifier(
                        MockToken, path=[IdentifierPathElement(MockToken, "num")]
                    ),
                    stop=Identifier(
                        MockToken,
                        path=[
                            IdentifierPathElement(MockToken, "collection"),
                            IdentifierPathElement(MockToken, "products"),
                            IdentifierPathElement(MockToken, "size"),
                        ],
                    ),
                ),
            ),
            Case(
                "item in range with options",
                "product in (1..10) offset:2 limit:5 reversed",
                LoopExpression(
                    name="product",
                    start=IntegerLiteral(MockToken, 1),
                    stop=IntegerLiteral(MockToken, 10),
                    limit=IntegerLiteral(MockToken, 5),
                    offset=IntegerLiteral(MockToken, 2),
                    reversed_=True,
                ),
            ),
        ]

        self._test(test_cases, tokenize_loop_expression, parse_loop_expression)
