"""Test liquid expressions."""
# pylint: disable=missing-class-docstring
from unittest import TestCase

from liquid import Context
from liquid import Environment

from liquid.expression import NIL
from liquid.expression import BLANK
from liquid.expression import CONTINUE
from liquid.expression import StringLiteral
from liquid.expression import RangeLiteral
from liquid.expression import IntegerLiteral
from liquid.expression import Identifier
from liquid.expression import IdentifierPathElement
from liquid.expression import PrefixExpression

from liquid.exceptions import LiquidTypeError


class CompareExpressionTestCase(TestCase):
    def test_compare_nil_to_none(self):
        """Test that nil is equal to None."""
        self.assertTrue(NIL.__eq__(None))  # pylint: disable=unnecessary-dunder-call

    def test_compare_blank_to_blank(self):
        """Test that blank is equal to blank."""
        self.assertTrue(BLANK.__eq__(BLANK))  # pylint: disable=unnecessary-dunder-call

    def test_compare_continue(self):
        """Test that continue is only equal to itself."""
        # pylint: disable=unnecessary-dunder-call
        self.assertFalse(CONTINUE.__eq__(object()))


class EvaluateExpressionTestCase(TestCase):
    def test_evaluate_continue(self):
        """Test that continue always evaluates to zero."""
        env = Environment()
        ctx = Context(env=env)

        self.assertEqual(CONTINUE.evaluate(ctx), 0)

    def test_evaluate_range_literal(self):
        """Test that ranges can not descend."""
        env = Environment()
        ctx = Context(env=env)

        rng = RangeLiteral(IntegerLiteral(9), IntegerLiteral(1))
        self.assertEqual(list(rng.evaluate(ctx)), [])

    def test_evaluate_prefix_expression(self):
        """Test that prefix expression raise a type error if the operator is
        unknown."""
        env = Environment()
        ctx = Context(env=env)

        expr = PrefixExpression("@", IntegerLiteral(1))
        with self.assertRaises(LiquidTypeError):
            expr.evaluate(ctx)


class HashExpressionTestCase(TestCase):
    def test_hash_literal(self):
        """Test that literals are hashable."""
        hash(StringLiteral("foo"))

    def test_hash_range(self):
        """Test that range literals are hashable."""
        rng = RangeLiteral(IntegerLiteral(9), IntegerLiteral(1))
        hash(rng)

    def test_hash_identifier(self):
        """Test that range identifiers are hashable."""
        ident = Identifier([IdentifierPathElement(0)])
        hash(ident)
