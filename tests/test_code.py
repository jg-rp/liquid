import unittest
from typing import NamedTuple, List

from liquid import code
from liquid.code import Opcode


class MakeCase(NamedTuple):
    description: str
    op: Opcode
    operands: List[int]
    expected: code.Instruction


class OperandsCase(NamedTuple):
    description: str
    op: Opcode
    operands: List[int]
    read: int


class CodeTestCase(unittest.TestCase):
    def test_make(self):
        """Test that we can make bytecode instructions."""
        test_cases = [
            MakeCase(
                description="one two-byte operand",
                op=Opcode.CONSTANT,
                operands=[65534],
                expected=code.Instruction(Opcode.CONSTANT, [65534], 1),
            ),
            MakeCase(
                description="no operands",
                op=Opcode.POP,
                operands=[],
                expected=code.Instruction(Opcode.POP, [], 0),
            ),
        ]

        for case in test_cases:
            instruction = code.make(case.op, *case.operands)

            with self.subTest(msg=case.description):
                self.assertEqual(instruction, case.expected)

    def test_instruction_string(self):
        """Test that we can pretty print instructions."""
        instructions = [
            code.make(Opcode.CONSTANT, 2),
            code.make(Opcode.CONSTANT, 65535),
        ]

        expected = "0000 OpConstant 2\n0001 OpConstant 65535"
        self.assertEqual(
            code.string(instructions), expected, msg="bad instruction formatting"
        )
