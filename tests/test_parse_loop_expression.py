# pylint: disable=missing-class-docstring missing-module-docstring
import unittest

from dataclasses import dataclass
from typing import Union

from liquid.expression import Expression
from liquid.expression import IdentifierPathElement
from liquid.expression import Identifier
from liquid.expression import IntegerLiteral
from liquid.expression import RangeLiteral
from liquid.expression import LoopExpression

from liquid.expressions import parse_loop_expression


@dataclass
class Case:
    description: str
    expression: str
    expect: Union[Expression, str]


class ParseBooleanExpressionTestCase(unittest.TestCase):
    def test_parse_boolean_expression(self):
        """Test that we can parse liquid loop expressions."""
        test_cases = [
            Case(
                "item in array",
                "product in collection.products",
                LoopExpression(
                    name="product",
                    iterable=Identifier(
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
                    iterable=Identifier(
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
                    iterable=Identifier(
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
                    iterable=Identifier(
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
                    iterable=Identifier(
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
                    iterable=Identifier(
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
                    iterable=Identifier(
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
                    iterable=Identifier(
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
                    iterable=RangeLiteral(
                        start=IntegerLiteral(1),
                        stop=IntegerLiteral(10),
                    ),
                ),
            ),
            Case(
                "item in range with integer literal start and identifier stop",
                "product in (1..collection.products.size)",
                LoopExpression(
                    name="product",
                    iterable=RangeLiteral(
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
            ),
            Case(
                "item in range with integer identifier start and stop",
                "product in (num..collection.products.size)",
                LoopExpression(
                    name="product",
                    iterable=RangeLiteral(
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
            ),
            Case(
                "item in range with options",
                "product in (1..10) offset:2 limit:5 reversed",
                LoopExpression(
                    name="product",
                    iterable=RangeLiteral(
                        start=IntegerLiteral(1),
                        stop=IntegerLiteral(10),
                    ),
                    limit=IntegerLiteral(5),
                    offset=IntegerLiteral(2),
                    reversed_=True,
                ),
            ),
            Case(
                "items in a nested array",
                "product in collections[0]['tags']",
                LoopExpression(
                    name="product",
                    iterable=Identifier(
                        path=[
                            IdentifierPathElement("collections"),
                            IdentifierPathElement(0),
                            IdentifierPathElement("tags"),
                        ],
                    ),
                ),
            ),
            Case(
                "split over multiple lines",
                "product\n in \ncollections[0]['tags']",
                LoopExpression(
                    name="product",
                    iterable=Identifier(
                        path=[
                            IdentifierPathElement("collections"),
                            IdentifierPathElement(0),
                            IdentifierPathElement("tags"),
                        ],
                    ),
                ),
            ),
            Case(
                "comma separated arguments",
                "i in array, limit: 4, offset: 2",
                LoopExpression(
                    name="i",
                    iterable=Identifier(
                        path=[
                            IdentifierPathElement("array"),
                        ],
                    ),
                    limit=IntegerLiteral(4),
                    offset=IntegerLiteral(2),
                ),
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                expr = parse_loop_expression(case.expression)
                self.assertEqual(expr, case.expect)
