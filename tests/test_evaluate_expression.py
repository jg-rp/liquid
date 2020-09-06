"""Liquid expression evaluator test cases."""

import unittest
from typing import NamedTuple, Any

from liquid.environment import Environment
from liquid.context import Context
from liquid.lex import get_expression_lexer
from liquid.parse import (
    parse_filtered_expression,
    parse_boolean_expression,
    parse_assignment_expression,
    parse_loop_expression,
)


class Case(NamedTuple):
    """Subtest helper"""

    description: str
    context: Context
    expression: str
    expect: Any


class LiquidStatementEvalTestCase(unittest.TestCase):
    """Liquid statement expression evaluator test cases."""

    def _test(self, test_cases, parse_func):
        """Utility method for evaluating lists of test cases."""
        env = Environment()
        lex = get_expression_lexer(env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = lex.tokenize(case.expression)
                expr = parse_func(tokens)
                res = expr.evaluate(case.context)
                self.assertEqual(res, case.expect)

    def test_eval_statement_expression(self):
        """Test that we can evaluate a liquid statement expression."""
        test_cases = [
            Case("string literal", Context(), "'foobar'", "foobar"),
            Case("integer literal", Context(), "7", 7),
            Case("float literal", Context(), "7.5", 7.5),
            Case("negative integer literal", Context(), "-7", -7),
            Case("negative float literal", Context(), "-7.5", -7.5),
            Case(
                "single global object identifier",
                Context({"collection": "foo"}),
                "collection",
                "foo",
            ),
            Case(
                "string literal with no arg filter",
                Context(filters={"upcase": lambda s: str(s).upper()}),
                "'foo' | upcase",
                "FOO",
            ),
            Case(
                "object identifier with no arg filter",
                Context(
                    {"collection": {"title": "foo"}},
                    filters={"upcase": lambda s: str(s).upper()},
                ),
                "collection.title | upcase",
                "FOO",
            ),
            Case(
                "string literal with two arg filter",
                Context(
                    filters={"slice": lambda s, start, length: str(s)[start:][:length]},
                ),
                '"Liquid" | slice: 2, 5',
                "quid",
            ),
            Case(
                "string literal with two filters",
                Context(
                    filters={
                        "upcase": lambda s: str(s).upper(),
                        "slice": lambda s, start, length: str(s)[start:][:length],
                    },
                ),
                '"Liquid" | slice: 2, 5 | upcase',
                "QUID",
            ),
            Case(
                "resolve identifier chain",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.c",
                "hello",
            ),
            Case(
                "resolve identifier chain not in context",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.x",
                None,
            ),
            Case(
                "resolve identifier chain containing whitespace.",
                Context(
                    global_objects={"a": {"b x": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a['b x'].c",
                "hello",
            ),
            Case(
                "resolve identifier chain ending in an array",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.array",
                [1, 2, 3],
            ),
            Case(
                "resolve identifier chain ending in an array index",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.array.1",
                2,
            ),
            Case(
                "resolve identifier chain ending in an array index using subscript",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.array[1]",
                2,
            ),
            Case(
                "try to read past an array",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.array.foo",
                None,
            ),
            Case(
                "array `first` special method",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.array.first",
                1,
            ),
            Case(
                "array `last` special method",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.array.last",
                3,
            ),
            Case(
                "array `size` special method",
                Context(
                    global_objects={"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                ),
                "a.b.array.size",
                3,
            ),
            Case(
                "size of an empty array",
                Context(global_objects={"a": {"b": {"c": "hello", "array": []}}},),
                "a.b.array.size",
                0,
            ),
            Case(
                "size of an object",
                Context(global_objects={"a": {"b": {"c": "hello", "array": []}}},),
                "a.b.size",
                2,
            ),
        ]

        self._test(test_cases, parse_filtered_expression)

    def test_eval_boolean_expression(self):
        """Test that we can evaluate boolean expressions."""
        test_cases = [
            Case(
                description="true literal",
                context=Context(),
                expression="true",
                expect=True,
            ),
            Case(
                description="false literal",
                context=Context(),
                expression="false",
                expect=False,
            ),
            Case(
                description="string literal",
                context=Context(),
                expression="'some'",
                expect=True,
            ),
            Case(
                description="empty string",
                context=Context(),
                expression="''",
                expect=True,
            ),
            Case(
                description="truthy identifier",
                context=Context(global_objects={"collection": {"title": "foo"}}),
                expression="collection.title",
                expect=True,
            ),
            Case(
                description="falsey identifier",
                context=Context(global_objects={"collection": {"title": "foo"}}),
                expression="collection.tags",
                expect=False,
            ),
            Case(
                description="truthy comparision",
                context=Context(global_objects={"user": {"age": 21}}),
                expression="user.age >= 21",
                expect=True,
            ),
            Case(
                description="not equal comparision",
                context=Context(global_objects={"user": {"age": 21}}),
                expression="user.age != 21",
                expect=False,
            ),
            Case(
                description="truthy comparision and logic operator",
                context=Context(
                    global_objects={
                        "user": {"age": 20},
                        "collection": {"tags": ["safe",]},
                    }
                ),
                expression="user.age >= 21 or collection.tags contains 'safe'",
                expect=True,
            ),
            Case(
                description="boolean with logic operators",
                context=Context(),
                expression="true and false and false or true",
                expect=False,
            ),
            Case(
                description="empty array",
                context=Context({"a": {"array": []}}),
                expression="a.array == empty",
                expect=True,
            ),
            Case(
                description="empty object",
                context=Context({"a": {"obj": {}}}),
                expression="a.obj == empty",
                expect=True,
            ),
            Case(
                description="not empty array",
                context=Context({"a": {"array": [1, 2]}}),
                expression="a.array == empty",
                expect=False,
            ),
            Case(
                description="not empty object",
                context=Context({"a": {"obj": {"foo": "bar"}}}),
                expression="a.obj == empty",
                expect=False,
            ),
            Case(
                description="invalid comparison to empty",
                context=Context({"a": {"foo": 1}}),
                expression="a.foo == empty",
                expect=False,
            ),
            Case(
                description="empty equals empty",
                context=Context(),
                expression="empty == empty",
                expect=True,
            ),
            Case(
                description="empty not equals true",
                context=Context(),
                expression="empty != true",
                expect=True,
            ),
            Case(
                description="nil equals nil",
                context=Context(),
                expression="nil == nil",
                expect=True,
            ),
            Case(
                description="string contains string",
                context=Context(),
                expression="'hello' contains 'ell'",
                expect=True,
            ),
            Case(
                description="string contains int",
                context=Context(),
                expression="'hel1lo' contains 1",
                expect=True,
            ),
            Case(
                description="string not equal int",
                context=Context(),
                expression="'hello' != 1",
                expect=True,
            ),
            Case(
                description="array contains",
                context=Context({"foo": [1, 2, 4]}),
                expression="foo contains 2",
                expect=True,
            ),
            Case(
                description="array does not contain",
                context=Context({"foo": [1, 2, 4]}),
                expression="foo contains 3",
                expect=False,
            ),
            Case(
                description="int equals",
                context=Context(),
                expression="1 == 1",
                expect=True,
            ),
            Case(
                description="int less than",
                context=Context(),
                expression="1 < 2",
                expect=True,
            ),
            Case(
                description="int less than or equal",
                context=Context(),
                expression="1 <= 1",
                expect=True,
            ),
            Case(
                description="int greater than",
                context=Context(),
                expression="1 > 0",
                expect=True,
            ),
            Case(
                description="int greater than or equal",
                context=Context(),
                expression="1 >= 1",
                expect=True,
            ),
            Case(
                description="true equals true",
                context=Context(),
                expression="true == true",
                expect=True,
            ),
            Case(
                description="true equal false",
                context=Context(),
                expression="true == false",
                expect=False,
            ),
            Case(
                description="true not equal false",
                context=Context(),
                expression="true != false",
                expect=True,
            ),
            Case(
                description="string equals int",
                context=Context(),
                expression="'2' == 2",
                expect=False,
            ),
        ]

        self._test(test_cases, parse_boolean_expression)

    def test_eval_assignment_expression(self):
        """Test that we can evaluate assignment expressions."""

        test_cases = [
            Case(
                description="assign a string literal",
                context=Context(),
                expression="some = 'foo'",
                expect=("some", "foo"),
            ),
            Case(
                description="assign an integer literal",
                context=Context(),
                expression="some = 5",
                expect=("some", 5),
            ),
            Case(
                description="assign a float literal",
                context=Context(),
                expression="some = 5.7",
                expect=("some", 5.7),
            ),
            Case(
                description="assign an array using a split filter",
                context=Context(filters={"split": lambda x, y: x.split(y)}),
                expression='some = "apples, oranges, peaches" | split: ", "',
                expect=("some", ["apples", "oranges", "peaches"]),
            ),
            Case(
                description="assign from a filtered identifier",
                context=Context(
                    global_objects={"user": {"title": "Mr"}},
                    filters={"downcase": lambda x: x.lower()},
                ),
                expression="title = user.title | downcase",
                expect=("title", "mr"),
            ),
        ]

        env = Environment()
        lex = get_expression_lexer(env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                stream = lex.tokenize(case.expression)
                expr = parse_assignment_expression(stream)
                expr.evaluate(case.context)

                name, val = case.expect
                self.assertEqual(case.context.get([name,]), val)

    def test_eval_loop_expression(self):
        """Test that we can evaluate loop expressions."""

        test_cases = [
            Case(
                description="simple range loop",
                context=Context(),
                expression="i in (0..3)",
                expect=[0, 1, 2, 3],
            ),
            Case(
                description="reversed range",
                context=Context(),
                expression="i in (0..3) reversed",
                expect=[3, 2, 1, 0],
            ),
            Case(
                description="loop over an object from context",
                context=Context({"a": {"name": "foo", "title": "bar"}}),
                expression="i in a",
                expect=[("name", "foo"), ("title", "bar")],
            ),
        ]

        env = Environment()
        lex = get_expression_lexer(env)

        for case in test_cases:
            with self.subTest(msg=case.description):
                stream = lex.tokenize(case.expression)
                expr = parse_loop_expression(stream)
                loopiter = expr.evaluate(case.context)

                self.assertEqual(list(loopiter), case.expect)
