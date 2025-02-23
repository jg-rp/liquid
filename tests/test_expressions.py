"""Test liquid expressions."""

from unittest import TestCase

from liquid import Environment
from liquid import RenderContext
from liquid.exceptions import LiquidTypeError
from liquid.expression import BLANK
from liquid.expression import CONTINUE
from liquid.expression import NIL
from liquid.expression import Identifier
from liquid.expression import IntegerLiteral
from liquid.expression import PrefixExpression
from liquid.expression import RangeLiteral
from liquid.expression import Segment
from liquid.expression import StringLiteral


class CompareExpressionTestCase(TestCase):
    def test_compare_nil_to_none(self) -> None:
        """Test that nil is equal to None."""
        self.assertTrue(NIL.__eq__(None))

    def test_compare_blank_to_blank(self) -> None:
        """Test that blank is equal to blank."""
        self.assertTrue(BLANK.__eq__(BLANK))

    def test_compare_continue(self) -> None:
        """Test that continue is only equal to itself."""
        self.assertFalse(CONTINUE.__eq__(object()))


class EvaluateExpressionTestCase(TestCase):
    def test_evaluate_continue(self) -> None:
        """Test that continue always evaluates to zero."""
        env = Environment()
        template = env.from_string("")
        ctx = RenderContext(template)

        self.assertEqual(CONTINUE.evaluate(ctx), 0)

    def test_evaluate_range_literal(self) -> None:
        """Test that ranges can not descend."""
        env = Environment()
        template = env.from_string("")
        ctx = RenderContext(template)

        rng = RangeLiteral(IntegerLiteral(9), IntegerLiteral(1))
        self.assertEqual(list(rng.evaluate(ctx)), [])

    def test_evaluate_prefix_expression(self) -> None:
        """Test that prefix expression raise a type error if the operator is
        unknown."""
        env = Environment()
        template = env.from_string("")
        ctx = RenderContext(template)

        expr = PrefixExpression("@", IntegerLiteral(1))
        with self.assertRaises(LiquidTypeError):
            expr.evaluate(ctx)


class HashExpressionTestCase(TestCase):
    def test_hash_literal(self) -> None:
        """Test that literals are hashable."""
        hash(StringLiteral("foo"))

    def test_hash_range(self) -> None:
        """Test that range literals are hashable."""
        rng = RangeLiteral(IntegerLiteral(9), IntegerLiteral(1))
        hash(rng)

    def test_hash_identifier(self) -> None:
        """Test that range identifiers are hashable."""
        ident = Identifier([Segment(0)])
        hash(ident)
