import unittest
from typing import NamedTuple, List

from liquid import code
from liquid.code import Opcode


class MakeCase(NamedTuple):
    description: str
    op: Opcode
    operands: List[int]
    expected: List[int]


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
                expected=[Opcode.CONSTANT, 255, 254],
            ),
            MakeCase(
                description="no operands",
                op=Opcode.POP,
                operands=[],
                expected=[Opcode.POP],
            ),
        ]

        for case in test_cases:
            instruction = code.make(case.op, *case.operands)

            with self.subTest(msg=case.description):
                self.assertEqual(
                    len(instruction),
                    len(case.expected),
                    msg=f"expected {len(case.expected)} bytes, found {len(instruction)}",
                )

                for byte in instruction:
                    self.assertLessEqual(
                        byte,
                        255,
                        msg="instruction bytes must be less than or equal to 255",
                    )

                for got, want in zip(instruction, case.expected):
                    self.assertEqual(got, want)

    def test_instruction_string(self):
        """Test that we can pretty print instructions."""
        instructions = code.chain(
            code.make(Opcode.CONSTANT, 2),
            code.make(Opcode.CONSTANT, 65535),
        )

        expected = "0000 OpConstant 2\n0003 OpConstant 65535"
        self.assertEqual(
            code.string(instructions), expected, msg="bad instruction formatting"
        )

    def test_read_operands(self):
        """Test that we can read back operands from a byte code instruction."""
        test_cases = [
            OperandsCase(
                description="one one-byte operand",
                op=Opcode.CYC,
                operands=[254],
                read=1,
            ),
            OperandsCase(
                description="one two-byte operand",
                op=Opcode.CONSTANT,
                operands=[65535],
                read=2,
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                instruction = code.make(case.op, *case.operands)

                opdef = code.lookup(case.op)

                operands, read = code.read_operands(opdef, instruction[1:])
                self.assertEqual(read, case.read, "read wrong number of bytes")

                for got, want in zip(operands, case.operands):
                    self.assertEqual(got, want, msg="wrong operand")
