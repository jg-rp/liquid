# pylint: disable=missing-class-docstring missing-module-docstring
import unittest

from typing import Any
from typing import Mapping
from typing import NamedTuple

from liquid import Context
from liquid import Environment

from liquid.context import Undefined

from liquid.expressions import parse_filtered_expression
from liquid.expressions import parse_conditional_expression
from liquid.expressions import parse_conditional_expression_with_parens


class Case(NamedTuple):
    """Table-driven test case helper."""

    description: str
    context: Mapping[str, Any]
    expression: str
    expect: Any


class EvalFilteredExpressionTestCase(unittest.TestCase):
    """Test cases for evaluating standard filtered expressions."""

    test_cases = [
        Case(
            "string literal",
            {},
            "'foobar'",
            "foobar",
        ),
        Case(
            "integer literal",
            {},
            "7",
            7,
        ),
        Case(
            "float literal",
            {},
            "7.5",
            7.5,
        ),
        Case(
            "negative integer literal",
            {},
            "-7",
            -7,
        ),
        Case(
            "negative float literal",
            {},
            "-7.5",
            -7.5,
        ),
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
        Case(
            "array index using negative subscript",
            {"a": [1, 2, 3]},
            "a[-1]",
            3,
        ),
    ]

    def test_eval_filtered_expression(self) -> None:
        """Test that we can evaluate standard boolean expressions."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_filtered_expression(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)

    def test_eval_conditional_expression(self) -> None:
        """Test that we can evaluation of non-standard boolean expressions
        is backwards compatible."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_conditional_expression(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)

    def test_eval_conditional_expression_with_parens(self) -> None:
        """Test that we can evaluation of non-standard boolean expressions
        is backwards compatible."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_conditional_expression_with_parens(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)


class EvalConditionalExpressionTestCase(unittest.TestCase):
    """Test cases for evaluating non-standard conditional expressions."""

    test_cases = [
        Case(
            description="string literal with true condition",
            context={},
            expression="'foo' if true",
            expect="foo",
        ),
        Case(
            description="string literal with false condition",
            context={},
            expression="'foo' if false",
            expect=Undefined(""),
        ),
        Case(
            description="string literal with false condition and alternative",
            context={},
            expression="'foo' if false else 'bar'",
            expect="bar",
        ),
        Case(
            description="object and condition from context",
            context={"settings": {"foo": True}, "greeting": "hello"},
            expression="greeting if settings.foo else 'bar'",
            expect="hello",
        ),
        Case(
            description="object and condition from context with tail filter",
            context={"settings": {"foo": True}, "greeting": "hello"},
            expression="greeting if settings.foo else 'bar' || upcase",
            expect="HELLO",
        ),
        Case(
            description="object filter with true condition",
            context={},
            expression="'foo' | upcase if true else 'bar'",
            expect="FOO",
        ),
        Case(
            description="object filter with false condition",
            context={},
            expression="'foo' | upcase if false else 'bar'",
            expect="bar",
        ),
    ]

    def test_eval_conditional(self) -> None:
        """Test that we can evaluate conditional expressions."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_conditional_expression(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)

    def test_eval_with_parens(self) -> None:
        """Test that we can evaluate conditional expressions that support logical
        `not` and grouping terms with parentheses."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_conditional_expression_with_parens(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)


class EvalConditionalNotExpressionTestCase(unittest.TestCase):
    """Test cases for evaluating non-standard conditional expressions, including
    logical `not` and grouping terms with parentheses."""

    test_cases = [
        Case(
            description="string literal with true condition",
            context={},
            expression="'foo' if not true",
            expect=Undefined(""),
        ),
        Case(
            description="string literal with false condition",
            context={},
            expression="'foo' if not false",
            expect="foo",
        ),
        Case(
            description="string literal with false condition and alternative",
            context={},
            expression="'foo' if not false else 'bar'",
            expect="foo",
        ),
        Case(
            description="object and condition from context",
            context={"settings": {"foo": True}, "greeting": "hello"},
            expression="greeting if not settings.foo else 'bar'",
            expect="bar",
        ),
        Case(
            description="object and condition from context with tail filter",
            context={"settings": {"foo": True}, "greeting": "hello"},
            expression="greeting if not settings.foo else 'bar' || upcase",
            expect="BAR",
        ),
        Case(
            description="object filter with true condition",
            context={},
            expression="'foo' | upcase if not true else 'bar'",
            expect="bar",
        ),
        Case(
            description="object filter with false condition",
            context={},
            expression="'foo' | upcase if not false else 'bar'",
            expect="FOO",
        ),
    ]

    def test_eval_with_parens(self) -> None:
        """Test that we can evaluate conditional expressions that support logical
        `not` and grouping terms with parentheses."""
        env = Environment()

        for case in self.test_cases:
            with self.subTest(msg=case.description):
                context = Context(env, globals=case.context)
                expr = parse_conditional_expression_with_parens(case.expression)
                self.assertEqual(expr.evaluate(context), case.expect)


class MalformedConditionalExpressionTestCase(unittest.TestCase):
    """Test cases for malformed conditional expressions."""

    def test_missing_condition(self) -> None:
        """Test that we handle conditional expressions with missing conditions."""
        env = Environment(undefined=Undefined)
        context = Context(env)

        # Condition defaults to `Undefined`
        expr = parse_conditional_expression("'foo' if")
        self.assertEqual(expr.evaluate(context), Undefined(""))

        # Same for extra boolean expressions
        expr = parse_conditional_expression_with_parens("'foo' if")
        self.assertEqual(expr.evaluate(context), Undefined(""))

    def test_missing_alternative(self) -> None:
        """Test that we handle conditional expressions with a missing alternative."""
        env = Environment(undefined=Undefined)
        context = Context(env)

        # Alternative defaults to `Undefined`
        expr = parse_conditional_expression("'foo' if false else")
        self.assertEqual(expr.evaluate(context), Undefined(""))

        # Same for extra boolean expressions
        expr = parse_conditional_expression_with_parens("'foo' if false else")
        self.assertEqual(expr.evaluate(context), Undefined(""))

    def test_missing_condition_followed_by_else(self) -> None:
        """Test that we handle missing boolean expressions."""
        env = Environment(undefined=Undefined)
        context = Context(env)

        # Alternative defaults to `Undefined`
        expr = parse_conditional_expression("'foo' if else 'bar'")
        self.assertEqual(expr.evaluate(context), "bar")

        # Same for extra boolean expressions
        expr = parse_conditional_expression_with_parens("'foo' if else 'bar'")
        self.assertEqual(expr.evaluate(context), "bar")
