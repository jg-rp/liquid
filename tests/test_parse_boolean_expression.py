# pylint: disable=missing-class-docstring missing-module-docstring
import unittest

from dataclasses import dataclass
from typing import Union

from liquid.expression import Expression
from liquid.expression import BooleanExpression
from liquid.expression import IdentifierPathElement
from liquid.expression import Identifier
from liquid.expression import Boolean
from liquid.expression import StringLiteral
from liquid.expression import IntegerLiteral
from liquid.expression import FloatLiteral
from liquid.expression import RangeLiteral
from liquid.expression import InfixExpression

from liquid.expressions import parse_boolean_expression


@dataclass
class Case:
    description: str
    expression: str
    expect: Union[Expression, str]


class ParseBooleanExpressionTestCase(unittest.TestCase):
    def test_parse_boolean_expression(self):
        """Test that we can parse liquid boolean expressions."""
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
                    expression=IntegerLiteral(-7),
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
                BooleanExpression(expression=FloatLiteral(-3.14)),
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
            Case(
                "identifier equals a range expression",
                "foo == (1..3)",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[
                                IdentifierPathElement("foo"),
                            ],
                        ),
                        operator="==",
                        right=RangeLiteral(
                            IntegerLiteral(1),
                            IntegerLiteral(3),
                        ),
                    ),
                ),
            ),
            Case(
                "chained identifier with bracketed index and string",
                "users[0]['age'] > 21",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[
                                IdentifierPathElement("users"),
                                IdentifierPathElement(0),
                                IdentifierPathElement("age"),
                            ],
                        ),
                        operator=">",
                        right=IntegerLiteral(21),
                    ),
                ),
            ),
            Case(
                "multiple lines",
                "users[0]['age'] \n>  \n21",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[
                                IdentifierPathElement("users"),
                                IdentifierPathElement(0),
                                IdentifierPathElement("age"),
                            ],
                        ),
                        operator=">",
                        right=IntegerLiteral(21),
                    ),
                ),
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                expr = parse_boolean_expression(case.expression)
                self.assertEqual(expr, case.expect)

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
                (
                    "((user.name == 'bob') "
                    "and ((user.age < 50) "
                    "or (collection.title == 'offers')"
                    "))"
                ),
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                expr = parse_boolean_expression(case.expression)
                self.assertEqual(str(expr), case.expect)
