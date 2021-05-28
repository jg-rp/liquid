"""Liquid expression evaluator test cases."""

import unittest
from typing import NamedTuple, Any, Mapping

from liquid.environment import Environment
from liquid.context import Context
from liquid.stream import TokenStream
from liquid.lex import (
    tokenize_filtered_expression,
    tokenize_boolean_expression,
    tokenize_loop_expression,
    tokenize_assignment_expression,
)
from liquid.parse import (
    parse_filtered_expression,
    parse_boolean_expression,
    parse_assignment_expression,
    parse_loop_expression,
)


class Case(NamedTuple):
    """Subtest helper"""

    description: str
    context: Mapping
    expression: str
    expect: Any


class LiquidStatementEvalTestCase(unittest.TestCase):
    """Liquid statement expression evaluator test cases."""

    def _test(self, test_cases, lex_func, parse_func):
        """Utility method for evaluating lists of test cases."""
        env = Environment()

        for case in test_cases:
            context = Context(env, case.context)
            with self.subTest(msg=case.description):
                tokens = TokenStream(lex_func(case.expression))
                expr = parse_func(tokens)
                res = expr.evaluate(context)
                self.assertEqual(res, case.expect)

    def test_eval_statement_expression(self):
        """Test that we can evaluate a liquid statement expression."""
        test_cases = [
            Case("string literal", {}, "'foobar'", "foobar"),
            Case("integer literal", {}, "7", 7),
            Case("float literal", {}, "7.5", 7.5),
            Case("negative integer literal", {}, "-7", -7),
            Case("negative float literal", {}, "-7.5", -7.5),
            Case(
                "single global object identifier",
                {"collection": "foo"},
                "collection",
                "foo",
            ),
            Case(
                "string literal with no arg filter",
                {},
                "'foo' | upcase",
                "FOO",
            ),
            Case(
                "object identifier with no arg filter",
                {"collection": {"title": "foo"}},
                "collection.title | upcase",
                "FOO",
            ),
            Case(
                "string literal with two arg filter",
                {},
                '"Liquid" | slice: 2, 5',
                "quid",
            ),
            Case(
                "string literal with two filters",
                {},
                '"Liquid" | slice: 2, 5 | upcase',
                "QUID",
            ),
            Case(
                "resolve identifier chain",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.c",
                "hello",
            ),
            Case(
                "resolve identifier chain not in context",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.x",
                None,
            ),
            Case(
                "resolve identifier chain containing whitespace.",
                {"a": {"b x": {"c": "hello", "array": [1, 2, 3]}}},
                "a['b x'].c",
                "hello",
            ),
            Case(
                "resolve identifier chain ending in an array",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.array",
                [1, 2, 3],
            ),
            Case(
                "resolve identifier chain ending in an array index",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.array.1",
                2,
            ),
            Case(
                "resolve identifier chain ending in an array index using subscript",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.array[1]",
                2,
            ),
            Case(
                "try to read past an array",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.array.foo",
                None,
            ),
            Case(
                "array `first` special method",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.array.first",
                1,
            ),
            Case(
                "array `last` special method",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.array.last",
                3,
            ),
            Case(
                "array `size` special method",
                {"a": {"b": {"c": "hello", "array": [1, 2, 3]}}},
                "a.b.array.size",
                3,
            ),
            Case(
                "size of an empty array",
                {"a": {"b": {"c": "hello", "array": []}}},
                "a.b.array.size",
                0,
            ),
            Case(
                "size of an object",
                {"a": {"b": {"c": "hello", "array": []}}},
                "a.b.size",
                2,
            ),
            Case(
                "nested and chained",
                {
                    "linklists": {"main": "main menu"},
                    "section": {"settings": {"menu": "main"}},
                },
                "linklists[section.settings.menu]",
                "main menu",
            ),
        ]

        self._test(test_cases, tokenize_filtered_expression, parse_filtered_expression)

    def test_eval_boolean_expression(self):
        """Test that we can evaluate boolean expressions."""
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
                description="falsey identifier",
                context={"collection": {"title": "foo"}},
                expression="collection.tags",
                expect=False,
            ),
            Case(
                description="truthy comparision",
                context={"user": {"age": 21}},
                expression="user.age >= 21",
                expect=True,
            ),
            Case(
                description="not equal comparision",
                context={"user": {"age": 21}},
                expression="user.age != 21",
                expect=False,
            ),
            Case(
                description="truthy comparision and logic operator",
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
        ]

        self._test(test_cases, tokenize_boolean_expression, parse_boolean_expression)

    def test_eval_assignment_expression(self):
        """Test that we can evaluate assignment expressions."""

        test_cases = [
            Case(
                description="assign a string literal",
                context={},
                expression="some = 'foo'",
                expect=("some", "foo"),
            ),
            Case(
                description="assign an integer literal",
                context={},
                expression="some = 5",
                expect=("some", 5),
            ),
            Case(
                description="assign a float literal",
                context={},
                expression="some = 5.7",
                expect=("some", 5.7),
            ),
            Case(
                description="assign an array using a split filter",
                context={},
                expression='some = "apples, oranges, peaches" | split: ", "',
                expect=("some", ["apples", "oranges", "peaches"]),
            ),
            Case(
                description="assign from a filtered identifier",
                context={"user": {"title": "Mr"}},
                expression="title = user.title | downcase",
                expect=("title", "mr"),
            ),
        ]

        env = Environment()

        for case in test_cases:
            context = Context(env, case.context)
            with self.subTest(msg=case.description):
                stream = TokenStream(tokenize_assignment_expression(case.expression))
                expr = parse_assignment_expression(stream)
                expr.evaluate(context)

                name, val = case.expect
                self.assertEqual(context.get(name), val)

    def test_eval_loop_expression(self):
        """Test that we can evaluate loop expressions."""

        test_cases = [
            Case(
                description="simple range loop",
                context={},
                expression="i in (0..3)",
                expect=[0, 1, 2, 3],
            ),
            Case(
                description="reversed range",
                context={},
                expression="i in (0..3) reversed",
                expect=[3, 2, 1, 0],
            ),
            Case(
                description="loop over an object from context",
                context={"a": {"name": "foo", "title": "bar"}},
                expression="i in a",
                expect=[("name", "foo"), ("title", "bar")],
            ),
            Case(
                description="loop over nested and chained object from context",
                context={
                    "linklists": {"main": ["1", "2"]},
                    "section": {"settings": {"menu": "main"}},
                },
                expression="link in linklists[section.settings.menu]",
                expect=["1", "2"],
            ),
            Case(
                description=(
                    "loop over nested and chained object from context "
                    "with trailing identifier"
                ),
                context={
                    "linklists": {"main": {"links": ["1", "2"]}},
                    "section": {"settings": {"menu": "main"}},
                },
                expression="link in linklists[section.settings.menu].links",
                expect=["1", "2"],
            ),
            Case(
                description="chained identifier in range loop",
                context={
                    "foo": {"bar": 3},
                },
                expression="x in (1..foo.bar)",
                expect=[1, 2, 3],
            ),
        ]

        env = Environment()

        for case in test_cases:
            context = Context(env, case.context)
            with self.subTest(msg=case.description):
                stream = TokenStream(tokenize_loop_expression(case.expression))
                expr = parse_loop_expression(stream)
                loopiter, length = expr.evaluate(context)

                self.assertEqual(list(loopiter), case.expect)
                self.assertEqual(length, len(case.expect))

    def test_eval_continue_loop_expression(self):
        """Test that we can evaluate loop expressions that use a continue offset."""

        env = Environment()
        context = Context(env, {"array": [1, 2, 3, 4, 5, 6]})

        # Mock a for loop with a limit
        context.stopindex("item-array", 3)

        stream = TokenStream(tokenize_loop_expression("item in array offset: continue"))
        expr = parse_loop_expression(stream)

        loopiter, length = expr.evaluate(context)

        self.assertEqual(list(loopiter), [4, 5, 6])
        self.assertEqual(length, 3)
