"""Test cases for representing an Identifier as a tuple."""

from unittest import TestCase

from liquid.expression import Identifier
from liquid.expression import Segment


class IdentifierAsTupleTestCase(TestCase):
    """Test cases for representing an Identifier as a tuple."""

    def test_simple_variable(self):
        """Test that we can represent a simple variable as a tuple."""
        ident = Identifier(path=[Segment("some")])
        self.assertEqual(ident.as_tuple(), ("some",))

    def test_dotted_variable(self):
        """Test that we can represent a dotted variable as a tuple."""
        ident = Identifier(
            path=[
                Segment("some"),
                Segment("thing"),
            ]
        )
        self.assertEqual(ident.as_tuple(), ("some", "thing"))

    def test_bracketed_variable(self):
        """Test that we can represent a bracketed variable as a tuple."""
        ident = Identifier(
            path=[
                Segment("some"),
                Segment("other.thing"),
            ]
        )
        self.assertEqual(ident.as_tuple(), ("some", "other.thing"))

    def test_nested_variable(self):
        """Test that we can represent nested variables as a tuple."""
        ident = Identifier(
            path=[
                Segment("some"),
                Identifier(
                    path=[
                        Segment("foo"),
                        Segment("bar"),
                        Identifier(
                            path=[
                                Segment("a"),
                                Segment("b"),
                            ]
                        ),
                    ]
                ),
                Segment("other.thing"),
            ]
        )
        self.assertEqual(
            ident.as_tuple(), ("some", ("foo", "bar", ("a", "b")), "other.thing")
        )
