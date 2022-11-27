"""Test cases for parsing loop-style expressions."""
import unittest

from typing import Any
from typing import Mapping
from typing import NamedTuple

from liquid import Context
from liquid import Environment
from liquid.expressions import parse_loop_expression


class Case(NamedTuple):
    """Table-driven test case helper."""

    description: str
    context: Mapping[str, Any]
    expression: str
    expect: Any


class EvalLoopExpressionTestCase(unittest.TestCase):
    """Test cases for evaluating `for` loop expressions."""

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
                expr = parse_loop_expression(case.expression)
                loop_iter, length = expr.evaluate(context)
                self.assertEqual(list(loop_iter), case.expect)
                self.assertEqual(length, len(case.expect))

    def test_eval_continue_loop_expression(self):
        """Test that we can evaluate loop expressions that use a continue offset."""
        env = Environment()
        context = Context(env, {"array": [1, 2, 3, 4, 5, 6]})

        # Mock a for loop with a limit
        context.stopindex("item-array", 3)
        expr = parse_loop_expression("item in array offset: continue")

        loop_iter, length = expr.evaluate(context)
        self.assertEqual(list(loop_iter), [4, 5, 6])
        self.assertEqual(length, 3)
