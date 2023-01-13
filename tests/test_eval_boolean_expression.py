# pylint: disable=missing-class-docstring missing-module-docstring
import unittest
from decimal import Decimal

from typing import Any
from typing import Mapping
from typing import NamedTuple

from liquid import Context
from liquid import Environment

from liquid.expressions import parse_boolean_expression
from liquid.expressions import parse_boolean_expression_with_parens


class Case(NamedTuple):
    """Table-driven test case helper."""

    description: str
    context: Mapping[str, Any]
    expression: str
    expect: Any


class EvalBooleanExpressionTestCase(unittest.TestCase):
    """Test cases for evaluating standard boolean expressions."""

    test_cases = [
        Case(
            description="true literal",
            context={},
            expression="true",
            expect=True,
        ),
        Case(
            description="false literal",
            context={},
            expression="false",
            expect=False,
        ),
        Case(
            description="string literal",
            context={},
            expression="'some'",
            expect=True,
        ),
        Case(
            description="empty string",
            context={},
            expression="''",
            expect=True,
        ),
        Case(
            description="truthy identifier",
            context={"collection": {"title": "foo"}},
            expression="collection.title",
            expect=True,
        ),
        Case(
            description="falsely identifier",
            context={"collection": {"title": "foo"}},
            expression="collection.tags",
            expect=False,
        ),
        Case(
            description="truthy comparison",
            context={"user": {"age": 21}},
            expression="user.age >= 21",
            expect=True,
        ),
        Case(
            description="not equal comparison",
            context={"user": {"age": 21}},
            expression="user.age != 21",
            expect=False,
        ),
        Case(
            description="truthy comparison and logic operator",
            context={
                "user": {"age": 20},
                "collection": {
                    "tags": [
                        "safe",
                    ]
                },
            },
            expression="user.age >= 21 or collection.tags contains 'safe'",
            expect=True,
        ),
        Case(
            description="boolean with logic operators",
            context={},
            expression="true and false and false or true",
            expect=False,
        ),
        Case(
            description="empty array",
            context={"a": {"array": []}},
            expression="a.array == empty",
            expect=True,
        ),
        Case(
            description="empty object",
            context={"a": {"obj": {}}},
            expression="a.obj == empty",
            expect=True,
        ),
        Case(
            description="not empty array",
            context={"a": {"array": [1, 2]}},
            expression="a.array == empty",
            expect=False,
        ),
        Case(
            description="not empty object",
            context={"a": {"obj": {"foo": "bar"}}},
            expression="a.obj == empty",
            expect=False,
        ),
        Case(
            description="invalid comparison to empty",
            context={"a": {"foo": 1}},
            expression="a.foo == empty",
            expect=False,
        ),
        Case(
            description="empty equals empty",
            context={},
            expression="empty == empty",
            expect=True,
        ),
        Case(
            description="empty not equals true",
            context={},
            expression="empty != true",
            expect=True,
        ),
        Case(
            description="nil equals nil",
            context={},
            expression="nil == nil",
            expect=True,
        ),
        Case(
            description="nil equals null",
            context={},
            expression="nil == null",
            expect=True,
        ),
        Case(
            description="null equals null",
            context={},
            expression="null == null",
            expect=True,
        ),
        Case(
            description="string contains string",
            context={},
            expression="'hello' contains 'ell'",
            expect=True,
        ),
        Case(
            description="string contains int",
            context={},
            expression="'hel1lo' contains 1",
            expect=True,
        ),
        Case(
            description="string not equal int",
            context={},
            expression="'hello' != 1",
            expect=True,
        ),
        Case(
            description="array contains",
            context={"foo": [1, 2, 4]},
            expression="foo contains 2",
            expect=True,
        ),
        Case(
            description="array does not contain",
            context={"foo": [1, 2, 4]},
            expression="foo contains 3",
            expect=False,
        ),
        Case(
            description="int equals",
            context={},
            expression="1 == 1",
            expect=True,
        ),
        Case(
            description="int less than",
            context={},
            expression="1 < 2",
            expect=True,
        ),
        Case(
            description="int less than or equal",
            context={},
            expression="1 <= 1",
            expect=True,
        ),
        Case(
            description="int greater than",
            context={},
            expression="1 > 0",
            expect=True,
        ),
        Case(
            description="int greater than or equal",
            context={},
            expression="1 >= 1",
            expect=True,
        ),
        Case(
            description="true equals true",
            context={},
            expression="true == true",
            expect=True,
        ),
        Case(
            description="true equal false",
            context={},
            expression="true == false",
            expect=False,
        ),
        Case(
            description="true not equal false",
            context={},
            expression="true != false",
            expect=True,
        ),
        Case(
            description="string equals int",
            context={},
            expression="'2' == 2",
            expect=False,
        ),
        Case(
            description="empty string is truthy",
            context={},
            expression="''",
            expect=True,
        ),
        Case(
            description="empty string and string is truthy",
            context={},
            expression="'' and 'foo'",
            expect=True,
        ),
        Case(
            description="float equals int",
            context={},
            expression="1 == 1.0",
            expect=True,
        ),
        Case(
            description="empty string equals blank",
            context={},
            expression="'' == blank",
            expect=True,
        ),
        Case(
            description="empty string equals empty",
            context={},
            expression="'' == empty",
            expect=True,
        ),
        Case(
            description="empty array equals empty",
            context={"x": []},
            expression="x == empty",
            expect=True,
        ),
        Case(
            description="empty array equals blank",
            context={"x": []},
            expression="x == blank",
            expect=True,
        ),
        Case(
            description="whitespace string equals blank",
            context={"x": "   "},
            expression="x == blank",
            expect=True,
        ),
        Case(
            description="whitespace string does not equal empty",
            context={"x": "   "},
            expression="x == empty",
            expect=False,
        ),
        Case(
            description="blank does not equal empty",
            context={},
            expression="blank == empty",
            expect=False,
        ),
        Case(
            description="empty does not equal blank",
            context={},
            expression="empty == blank",
            expect=False,
        ),
        Case(
            description="blank does not equal empty",
            context={},
            expression="blank != empty",
            expect=True,
        ),
        Case(
            description="undefined equals nil",
            context={},
            expression="nosuchthing == nil",
            expect=True,
        ),
        Case(
            description="undefined equals null",
            context={},
            expression="nosuchthing == null",
            expect=True,
        ),
        Case(
            description="nil equals undefined",
            context={},
            expression="nil == nosuchthing",
            expect=True,
        ),
        Case(
            description="nil equals None",
            context={"nothing": None},
            expression="nil == nothing",
            expect=True,
        ),
        Case(
            description="nil equals nil",
            context={},
            expression="nil == nil",
            expect=True,
        ),
        Case(
            description="zero",
            context={},
            expression="0",
            expect=True,
        ),
        Case(
            description="0.0",
            context={},
            expression="0.0",
            expect=True,
        ),
        Case(
            description="one",
            context={},
            expression="1",
            expect=True,
        ),
        Case(
            description="zero equals false",
            context={},
            expression="0 == false",
            expect=False,
        ),
        Case(
            description="zero equals true",
            context={},
            expression="0 == true",
            expect=False,
        ),
        Case(
            description="0.0 equals false",
            context={},
            expression="0.0 == false",
            expect=False,
        ),
        Case(
            description="0.0 equals true",
            context={},
            expression="0.0 == true",
            expect=False,
        ),
        Case(
            description="one equals true",
            context={},
            expression="1 == true",
            expect=False,
        ),
        Case(
            description="true equals one",
            context={},
            expression="true == 1",
            expect=False,
        ),
        Case(
            description="one is less than true",
            context={},
            expression="1 < true",
            expect=False,
        ),
        Case(
            description="zero is less than true",
            context={},
            expression="0 < true",
            expect=False,
        ),
        Case(
            description="0.0 is less than true",
            context={},
            expression="0.0 < true",
            expect=False,
        ),
        Case(
            description="one is not equal true",
            context={},
            expression="1 != true",
            expect=True,
        ),
        Case(
            description="zero is not equal false",
            context={},
            expression="0 != false",
            expect=True,
        ),
        Case(
            description="0.0 is not equal false",
            context={},
            expression="0.0 != false",
            expect=True,
        ),
        Case(
            description="false is not equal zero",
            context={},
            expression="false != 0",
            expect=True,
        ),
        Case(
            description="false is not equal 0.0",
            context={},
            expression="false != 0.0",
            expect=True,
        ),
        Case(
            description="false is less than string",
            context={},
            expression="false < 'false'",
            expect=False,
        ),
        Case(
            description="decimal zero",
            context={"n": Decimal("0")},
            expression="n",
            expect=True,
        ),
        Case(
            description="decimal non-zero",
            context={"n": Decimal("1")},
            expression="n",
            expect=True,
        ),
        Case(
            description="decimal zero equals false",
            context={"n": Decimal("0")},
            expression="n == false",
            expect=False,
        ),
        Case(
            description="decimal zero equals true",
            context={"n": Decimal("0")},
            expression="n == true",
            expect=False,
        ),
    ]

    def test_eval_boolean_expression(self) -> None:
        """Test that we can evaluate standard boolean expressions."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_boolean_expression(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)

    def test_eval_boolean_expression_with_parens(self) -> None:
        """Test that we can evaluation of non-standard boolean expressions
        is backwards compatible."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_boolean_expression_with_parens(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)


class EvalBooleanNotExpressionTestCase(unittest.TestCase):
    """Test cases for evaluating non-standard boolean expressions."""

    test_cases = [
        Case(
            description="not true literal",
            context={},
            expression="not true",
            expect=False,
        ),
        Case(
            description="not false literal",
            context={},
            expression="not false",
            expect=True,
        ),
        Case(
            description="not nil literal",
            context={},
            expression="not nil",
            expect=True,
        ),
        Case(
            description="not empty",
            context={},
            expression="not empty",
            expect=False,
        ),
        Case(
            description="not string literal",
            context={},
            expression="not 'some'",
            expect=False,
        ),
        Case(
            description="not empty string",
            context={},
            expression="not ''",
            expect=False,
        ),
        Case(
            description="boolean with logic not operators",
            context={},
            expression="true and not false",
            expect=True,
        ),
        Case(
            description="grouped boolean with logic operators",
            context={},
            expression="(true and false and false) or true",
            expect=True,
        ),
        Case(
            description="nested grouped boolean with logic operators",
            context={},
            expression="((true or false) or (false)) and true",
            expect=True,
        ),
        Case(
            description="grouped boolean with not",
            context={},
            expression="(true and false and false) or not true",
            expect=False,
        ),
        Case(
            description="range literal equals range literal",
            context={},
            expression="(1..3) == (1..3)",
            expect=True,
        ),
        Case(
            description="negate a group",
            context={},
            expression="not (false or true)",
            expect=False,
        ),
    ]

    def test_eval_with_parens(self) -> None:
        """Test that we can evaluate boolean expressions that support logical
        `not` and grouping terms with parentheses."""
        env = Environment()
        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_boolean_expression_with_parens(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)
