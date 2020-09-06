from unittest import TestCase
from typing import NamedTuple, Any, Optional

from liquid.lex import Pointer


class Case(NamedTuple):
    description: str
    source: str
    expect: Any
    at: Optional[str] = None
    read: int = 0


class PointerTestCase(TestCase):
    def test_pointer_at(self):
        """Test that the pointer :meth:`at` behaves correctly."""

        test_cases = [
            Case(
                description="at tag start",
                source=r"{% sometag %}",
                at=r"{%",
                expect=True,
            ),
            Case(
                description="at statement start", source=r"{{", at=r"{{", expect=True,
            ),
            Case(
                description="not at tag start",
                source=r"some literal {% sometag %}",
                at=r"{%",
                expect=False,
            ),
            Case(
                description="advance to tag start",
                source=r"some literal {% sometag %}",
                at=r"{%",
                expect=True,
                read=13,
            ),
            Case(
                description="advance to dot",
                source="3.14",
                at=".",
                expect=True,
                read=1,
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                pointer = Pointer(case.source)
                for _ in range(case.read):
                    pointer.read_char()

                assert case.at is not None
                self.assertEqual(pointer.at(case.at), case.expect)

    def test_pointer_peek(self):
        """Test that the pointer :meth:`peek` behaves correctly."""

        test_cases = [
            Case(description="peek next", source=r"{% sometag %}", expect="%", read=1),
            Case(description="peek ahead", source=r"{% sometag %}", expect="s", read=3),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                pointer = Pointer(case.source)
                self.assertEqual(pointer.peek(n=case.read), case.expect)

    def test_read_eof(self):
        """Test that the pointer handle end of file correctly."""
        pointer = Pointer("123")
        self.assertEqual(pointer.ch, "1")

        pointer.read_char()
        self.assertEqual(pointer.ch, "2")

        pointer.read_char()
        self.assertEqual(pointer.ch, "3")

        pointer.read_char()
        self.assertEqual(pointer.ch, "eof")

        pointer.read_char()
        self.assertEqual(pointer.ch, "eof")
