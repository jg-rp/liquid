import unittest
from typing import NamedTuple, List, Any

from liquid import Environment
from liquid import code
from liquid.code import Opcode
from liquid.compiler import Compiler


class Case(NamedTuple):
    description: str
    source: str
    expected_constants: List[Any]
    expected_instructions: code.Instructions


class CompilerTestCase(unittest.TestCase):
    def _test(self, test_cases):
        """Helper method for testing lists of Cases."""
        env = Environment()

        for case in test_cases:
            with self.subTest(msg=case.description):
                root = env.parse(case.source)

                compiler = Compiler()
                compiler.compile(root)

                bytecode = compiler.bytecode()

                self._test_instructions(
                    case.expected_instructions, bytecode.instructions
                )
                self._test_constants(case.expected_constants, bytecode.constants)

    def _test_instructions(self, expected, actual):
        # print("---")
        # print(actual, "\n\n")
        # print(expected)
        # print("---")

        self.assertEqual(len(expected), len(actual), msg="instruction length mismatch")

        for i, pair in enumerate(zip(actual, expected)):
            got, want = pair
            self.assertEqual(got, want, msg=f"wrong instruction at {i}")

    def _test_constants(self, expected, actual):
        self.assertEqual(len(expected), len(actual), msg="constants length mismatch")

        for i, pair in enumerate(zip(actual, expected)):
            got, want = pair
            self.assertEqual(got, want, msg=f"constants do not match at {i}")

    def test_literals(self):
        """Test that we can compile literals."""
        test_cases = [
            Case(
                description="integer literal",
                source="{{ 1 }}",
                expected_constants=[1],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="float literal",
                source="{{ 1.2 }}",
                expected_constants=[1.2],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="string literal",
                source="{{ 'hello' }}",
                expected_constants=["hello"],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="template literal",
                source="hello",
                expected_constants=["hello"],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="negative integer literal",
                source="{{ -1 }}",
                expected_constants=[1],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.MINUS),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_boolean_expressions(self):
        """Test that we can compile boolean expressions."""
        test_cases = [
            Case(
                description="literal true",
                source="{{ true }}",
                expected_constants=[],
                expected_instructions=code.Instructions(
                    code.make(Opcode.TRUE), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="literal false",
                source="{{ false }}",
                expected_constants=[],
                expected_instructions=code.Instructions(
                    code.make(Opcode.FALSE), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="greater than",
                source="{{ 1 > 2 }}",
                expected_constants=[1, 2],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.GT),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="less than",
                source="{{ 1 < 2 }}",
                expected_constants=[2, 1],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.GT),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="euqals",
                source="{{ 1 == 2 }}",
                expected_constants=[1, 2],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.EQ),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="not equals",
                source="{{ 1 != 2 }}",
                expected_constants=[1, 2],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.NE),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="boolean and",
                source="{{ true and false }}",
                expected_constants=[],
                expected_instructions=code.Instructions(
                    code.make(Opcode.TRUE),
                    code.make(Opcode.FALSE),
                    code.make(Opcode.AND),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="boolean or",
                source="{{ true or false }}",
                expected_constants=[],
                expected_instructions=code.Instructions(
                    code.make(Opcode.TRUE),
                    code.make(Opcode.FALSE),
                    code.make(Opcode.OR),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_conditionals(self):
        """Test that we can compile "if" tags."""
        test_cases = [
            Case(
                description="if true no alternative",
                source="{% if true %}10{% endif %}3333",
                expected_constants=["10", "3333"],
                expected_instructions=code.Instructions(
                    code.make(Opcode.TRUE),
                    code.make(Opcode.JUMPIFNOT, 10),
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.JUMP, 11),
                    code.make(Opcode.NOP),
                    code.make(Opcode.POP),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="if true with alternative",
                source="{% if true %}10{% else %}20{% endif %}3333",
                expected_constants=["10", "20", "3333"],
                expected_instructions=code.Instructions(
                    code.make(Opcode.TRUE),  # 0000
                    code.make(Opcode.JUMPIFNOT, 10),  # 0001
                    code.make(Opcode.CONSTANT, 0),  # 0004
                    code.make(Opcode.JUMP, 13),  # 0007
                    code.make(Opcode.CONSTANT, 1),  # 0010
                    code.make(Opcode.POP),  # 0013
                    code.make(Opcode.CONSTANT, 2),  # 0014
                    code.make(Opcode.POP),  # 0017
                ),
            ),
            Case(
                description="false condition, true conditional alternative",
                source="{% if false %}10{% elsif true %}20{% else %}30{% endif %}3333",
                expected_constants=["10", "20", "30", "3333"],
                expected_instructions=code.Instructions(
                    code.make(Opcode.FALSE),  # 0000
                    code.make(Opcode.JUMPIFNOT, 10),  # 0001 Jump to next alternative
                    code.make(Opcode.CONSTANT, 0),  # 0004
                    code.make(Opcode.JUMP, 23),  # 0007 Jump to end of condition
                    code.make(Opcode.TRUE),  # 0010
                    code.make(Opcode.JUMPIFNOT, 20),  # 0011 Jump to next alternative
                    code.make(Opcode.CONSTANT, 1),  # 0014
                    code.make(Opcode.JUMP, 23),  # 0017 Jump to end of condition
                    code.make(Opcode.CONSTANT, 2),  # 0020
                    code.make(Opcode.POP),  # 0023
                    code.make(Opcode.CONSTANT, 3),  # 0024
                    code.make(Opcode.POP),  # 0027
                ),
            ),
        ]

        self._test(test_cases)

    def test_assign(self):
        """Test that we can compile assign tags."""
        test_cases = [
            Case(
                description="simple assigns",
                source="{% assign one = 1 %}{% assign two = 2 %}",
                expected_constants=[1, 2],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SETLOCAL, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.SETLOCAL, 1),
                ),
            ),
            Case(
                description="assign and resolve",
                source="{% assign one = 1 %}{{ one }}",
                expected_constants=[1],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SETLOCAL, 0),
                    code.make(Opcode.GETLOCAL, 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="assign from identifier",
                source="{% assign one = 1 %}{% assign two = one %}{{ two }}",
                expected_constants=[1],
                expected_instructions=code.Instructions(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SETLOCAL, 0),
                    code.make(Opcode.GETLOCAL, 0),
                    code.make(Opcode.SETLOCAL, 1),
                    code.make(Opcode.GETLOCAL, 1),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)
