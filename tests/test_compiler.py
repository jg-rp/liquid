"""Compiler test cases."""
import unittest
import textwrap
from typing import NamedTuple, List, Any

from liquid import Environment
from liquid import code
from liquid.code import Opcode
from liquid.compiler import Compiler
from liquid import hash_identifier


class Case(NamedTuple):
    """Test case definition."""

    description: str
    source: str
    expected_constants: List[Any]
    expected_instructions: code.Instructions


class CompilerTestCase(unittest.TestCase):
    """Compiler test cases."""

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
                self._test_constants(bytecode.constants, case.expected_constants)

    def _test_instructions(self, expected, actual):
        # print("---")
        # print(code.string(actual))
        # print("\n\n")
        # print(code.string(expected))
        # print("---")

        self.assertEqual(len(expected), len(actual), msg="instruction length mismatch")

        for i, pair in enumerate(zip(actual, expected)):
            got, want = pair
            self.assertEqual(got, want, msg=f"wrong instruction at {i}")

    def _test_constants(self, actual, expected):
        self.assertEqual(len(expected), len(actual), msg="constants length mismatch")

        for i, pair in enumerate(zip(actual, expected)):
            got, want = pair

            if isinstance(want, list):
                self._test_compiled_capture_constants(got.instructions, want)
            else:
                self.assertEqual(got, want, msg=f"constants do not match at {i}")

    def _test_compiled_capture_constants(self, actual, expected):

        # print(textwrap.indent(code.string(actual), "\t"))
        # print("\n")
        # print(textwrap.indent(code.string(expected), "\t"))

        for i, pair in enumerate(zip(actual, expected)):
            got, want = pair
            self.assertEqual(got, want, msg=f"captured constants do not match at {i}")

    def test_literals(self):
        """Test that we can compile literals."""
        test_cases = [
            Case(
                description="integer literal",
                source="{{ 1 }}",
                expected_constants=[1],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="float literal",
                source="{{ 1.2 }}",
                expected_constants=[1.2],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="string literal",
                source="{{ 'hello' }}",
                expected_constants=["hello"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="template literal",
                source="hello",
                expected_constants=["hello"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="negative integer literal",
                source="{{ -1 }}",
                expected_constants=[1],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.NEG),
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
                source=r"{{ true }}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.TRU), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="literal false",
                source=r"{{ false }}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.FAL), code.make(Opcode.POP)
                ),
            ),
            Case(
                description="greater than",
                source=r"{{ 1 > 2 }}",
                expected_constants=[1, 2],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.GT),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="less than",
                source=r"{{ 1 < 2 }}",
                expected_constants=[2, 1],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.GT),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="euqals",
                source=r"{{ 1 == 2 }}",
                expected_constants=[1, 2],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.EQ),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="not equals",
                source=r"{{ 1 != 2 }}",
                expected_constants=[1, 2],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.NE),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="boolean and",
                source=r"{{ true and false }}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.TRU),
                    code.make(Opcode.FAL),
                    code.make(Opcode.AND),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="boolean or",
                source=r"{{ true or false }}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.TRU),
                    code.make(Opcode.FAL),
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
                source=r"{% if true %}10{% endif %}3333",
                expected_constants=["10", "3333"],
                expected_instructions=code.chain(
                    code.make(Opcode.TRU),
                    code.make(Opcode.JIN, 10),
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.JMP, 11),
                    code.make(Opcode.NOP),
                    code.make(Opcode.POP),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="if true with alternative",
                source=r"{% if true %}10{% else %}20{% endif %}3333",
                expected_constants=["10", "20", "3333"],
                expected_instructions=code.chain(
                    code.make(Opcode.TRU),  # 0000
                    code.make(Opcode.JIN, 10),  # 0001
                    code.make(Opcode.CONSTANT, 0),  # 0004
                    code.make(Opcode.JMP, 13),  # 0007
                    code.make(Opcode.CONSTANT, 1),  # 0010
                    code.make(Opcode.POP),  # 0013
                    code.make(Opcode.CONSTANT, 2),  # 0014
                    code.make(Opcode.POP),  # 0017
                ),
            ),
            Case(
                description="false condition, true conditional alternative",
                source=r"{% if false %}10{% elsif true %}20{% else %}30{% endif %}3333",
                expected_constants=["10", "20", "30", "3333"],
                expected_instructions=code.chain(
                    code.make(Opcode.FAL),  # 0000
                    code.make(Opcode.JIN, 10),  # 0001 Jump to next alternative
                    code.make(Opcode.CONSTANT, 0),  # 0004
                    code.make(Opcode.JMP, 23),  # 0007 Jump to end of condition
                    code.make(Opcode.TRU),  # 0010
                    code.make(Opcode.JIN, 20),  # 0011 Jump to next alternative
                    code.make(Opcode.CONSTANT, 1),  # 0014
                    code.make(Opcode.JMP, 23),  # 0017 Jump to end of condition
                    code.make(Opcode.CONSTANT, 2),  # 0020
                    code.make(Opcode.POP),  # 0023
                    code.make(Opcode.CONSTANT, 3),  # 0024
                    code.make(Opcode.POP),  # 0027
                ),
            ),
        ]

        self._test(test_cases)

    def test_unless(self):
        """Test that we can compile "unless" tags."""
        test_cases = [
            Case(
                description="literal false",
                source=r"{% unless false %}10{% endunless %}3333",
                expected_constants=["10", "3333"],
                expected_instructions=code.chain(
                    code.make(Opcode.FAL),
                    code.make(Opcode.JIF, 8),
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_assign(self):
        """Test that we can compile assign tags."""
        test_cases = [
            Case(
                description="simple assigns",
                source=r"{% assign one = 1 %}{% assign two = 2 %}",
                expected_constants=[1, 2],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SLO, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.SLO, 1),
                ),
            ),
            Case(
                description="assign and resolve",
                source=r"{% assign one = 1 %}{{ one }}",
                expected_constants=[1],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SLO, 0),
                    code.make(Opcode.GLO, 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="assign from identifier",
                source=r"{% assign one = 1 %}{% assign two = one %}{{ two }}",
                expected_constants=[1],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.SLO, 0),
                    code.make(Opcode.GLO, 0),
                    code.make(Opcode.SLO, 1),
                    code.make(Opcode.GLO, 1),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_capture(self):
        """Test that we can compile capture tags."""
        test_cases = [
            Case(
                description="simple capture",
                source=r"{% capture some %}foo{% endcapture %}",
                expected_constants=[
                    "foo",
                ],
                expected_instructions=code.chain(
                    code.make(Opcode.CAPTURE),
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.SETCAPTURE, 0),
                ),
            ),
        ]

        self._test(test_cases)

    def test_case_when(self):
        """Test that we can compile "case" tags."""
        test_cases = [
            Case(
                description="simple case",
                source=r"{% case true %}{% when false %}foo{% when true %}bar{% endcase %}3333",
                expected_constants=["foo", "bar", "3333"],
                expected_instructions=code.chain(
                    code.make(Opcode.TRU),  # 0000
                    code.make(Opcode.FAL),  # 0001
                    code.make(Opcode.EQ),  # 0002
                    code.make(Opcode.JIN, 12),  # 0003
                    code.make(Opcode.CONSTANT, 0),  # 0006
                    code.make(Opcode.JMP, 25),  # 0009
                    code.make(Opcode.TRU),  # 0012
                    code.make(Opcode.TRU),  # 0013
                    code.make(Opcode.EQ),  # 0014
                    code.make(Opcode.JIN, 24),  # 0015
                    code.make(Opcode.CONSTANT, 1),  # 0018
                    code.make(Opcode.JMP, 25),  # 0021
                    code.make(Opcode.NOP),  # 0024
                    code.make(Opcode.POP),  # 0025
                    code.make(Opcode.CONSTANT, 2),  # 0026
                    code.make(Opcode.POP),  # 0029
                ),
            ),
        ]

        self._test(test_cases)

    def test_resolve(self):
        """Test that we can compile global identifiers."""
        test_cases = [
            Case(
                description="not a local identifier",
                source=r"{{ product }}",
                expected_constants=["product"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.RES),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="chained global identifier",
                source=r"{{ product.title }}",
                expected_constants=["product", "title"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.RES),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.GIT),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="get attribute from identifier",
                source=r"{{ collections[product.collection_name] }}",
                expected_constants=["collections", "product", "collection_name"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.RES),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.RES),
                    code.make(Opcode.CONSTANT, 2),
                    code.make(Opcode.GIT),
                    code.make(Opcode.GIT),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_decrement(self):
        """Test that we can compile "decrement" tags."""
        test_cases = [
            Case(
                description="new decrement",
                source=r"{% decrement foo %}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.DEC, 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="existing decrement",
                source=r"{% decrement foo %}{% decrement foo %}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.DEC, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.DEC, 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="distinct decrements",
                source=r"{% decrement foo %}{% decrement bar %}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.DEC, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.DEC, 1),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_increment(self):
        """Test that we can compile "increment" tags."""
        test_cases = [
            Case(
                description="new increment",
                source=r"{% increment foo %}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.INC, 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="existing increment",
                source=r"{% increment foo %}{% increment foo %}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.INC, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.INC, 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="distinct increment",
                source=r"{% increment foo %}{% increment bar %}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.INC, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.INC, 1),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="increment then decrement",
                source=r"{% increment foo %}{% decrement foo %}",
                expected_constants=[],
                expected_instructions=code.chain(
                    code.make(Opcode.INC, 0),
                    code.make(Opcode.POP),
                    code.make(Opcode.DEC, 0),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_cycle(self):
        """Test that we can compile "cycle" tags."""
        test_cases = [
            Case(
                description="default group",
                source=r"{% cycle 'a', 'b', 'c' %}",
                expected_constants=["c", "b", "a", ""],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.CONSTANT, 2),
                    code.make(Opcode.CONSTANT, 3),
                    code.make(Opcode.CYC, 3),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="named group",
                source=r"{% cycle 'foo': 'a', 'b', 'c' %}",
                expected_constants=["c", "b", "a", "foo"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.CONSTANT, 2),
                    code.make(Opcode.CONSTANT, 3),
                    code.make(Opcode.CYC, 3),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)

    def test_for(self):
        """Test that we can compile "for" tags."""
        test_cases = [
            Case(
                description="literal range with no args",
                source=r"{% for i in (0..3) %}{{ i }}{% endfor %}",
                expected_constants=[
                    code.chain(
                        code.make(Opcode.JIE, 12),  # 0000
                        code.make(Opcode.GBL, 0),  # 0003
                        code.make(Opcode.POP),  # 0006
                        code.make(Opcode.STE, 0),  # 0007
                        code.make(Opcode.JMP, 3),  # 0010
                        code.make(Opcode.NOP),  # 0013
                        code.make(Opcode.STO),  # 0014
                    ),
                    3,
                    0,
                ],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),  # compiles block
                    code.make(Opcode.FAL),  # reverse
                    code.make(Opcode.NIL),  # offset
                    code.make(Opcode.NIL),  # limit
                    code.make(Opcode.CONSTANT, 1),  # range stop
                    code.make(Opcode.CONSTANT, 2),  # range start
                    code.make(Opcode.FOR, 2, 0),  # number of block and free vars
                ),
            ),
            Case(
                description="nested for loop",
                source=r"{% for i in (0..3) %}{% for j in (5..7) %}{{ i }}{{ j }}{% endfor %}{% endfor %}",
                expected_constants=[
                    code.chain(
                        code.make(Opcode.JIE, 15),  # 0000
                        code.make(Opcode.GFR, 0),  # 0003
                        code.make(Opcode.POP),  # 0006
                        code.make(Opcode.GBL, 0),  # 0007
                        code.make(Opcode.POP),  # 0010
                        code.make(Opcode.STE, 0),  # 0011
                        code.make(Opcode.JMP, 3),  # 0014
                        code.make(Opcode.NOP),  # 0017
                        code.make(Opcode.STO),  # 0018
                    ),
                    7,
                    5,
                    code.chain(
                        code.make(Opcode.JIE, 26),
                        code.make(Opcode.CONSTANT, 0),
                        code.make(Opcode.GBL, 0),
                        code.make(Opcode.FAL),  # reverse
                        code.make(Opcode.NIL),  # offset
                        code.make(Opcode.NIL),  # limit
                        code.make(Opcode.CONSTANT, 1),  # range stop
                        code.make(Opcode.CONSTANT, 2),  # range start
                        code.make(Opcode.FOR, 2, 1),  # index of loop var
                        code.make(Opcode.STE, 0),
                        code.make(Opcode.JMP, 3),
                        code.make(Opcode.NOP),
                        code.make(Opcode.STO),
                    ),
                    3,
                    0,
                ],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 3),  # compiled block
                    code.make(Opcode.FAL),  # reverse
                    code.make(Opcode.NIL),  # offset
                    code.make(Opcode.NIL),  # limit
                    code.make(Opcode.CONSTANT, 4),  # range stop
                    code.make(Opcode.CONSTANT, 5),  # range start
                    code.make(Opcode.FOR, 2, 0),  # index of loop var
                ),
            ),
        ]

        self._test(test_cases)

    def test_tablerow(self):
        """Test that we can compile "tablerow" tags."""
        test_cases = [
            Case(
                description="literal range with no args",
                source=r"{% tablerow tag in tags %}{{ tag }}{% endtablerow %}",
                expected_constants=[
                    code.chain(
                        code.make(Opcode.GBL, 0),
                        code.make(Opcode.POP),
                        code.make(Opcode.STE, 0),
                        code.make(Opcode.JMP, 0),
                        code.make(Opcode.STO),
                    ),
                    "tags",
                ],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.NIL),  # cols
                    code.make(Opcode.FAL),  # reverse
                    code.make(Opcode.NIL),  # offset
                    code.make(Opcode.NIL),  # limit
                    code.make(Opcode.NIL),  # range stop
                    code.make(Opcode.CONSTANT, 1),  # identifier
                    code.make(Opcode.RES),
                    code.make(Opcode.TAB, 2, 0),
                ),
            ),
        ]

        self._test(test_cases)

    def test_filter(self):
        """Test that we can compile filtered expressions."""

        test_cases = [
            Case(
                description="no arg filter",
                source=r"{{ 'hello' | upcase }}",
                expected_constants=["hello"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.FIL, hash_identifier("upcase"), 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="chained no arg filters",
                source=r"{{ 'hello' | upcase | lstrip }}",
                expected_constants=["hello"],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.FIL, hash_identifier("upcase"), 0),
                    code.make(Opcode.FIL, hash_identifier("lstrip"), 0),
                    code.make(Opcode.POP),
                ),
            ),
            Case(
                description="one arg filter",
                source=r"{{ 'there' | prepend: 'hello ' }}",
                expected_constants=["there", "hello "],
                expected_instructions=code.chain(
                    code.make(Opcode.CONSTANT, 0),
                    code.make(Opcode.CONSTANT, 1),
                    code.make(Opcode.FIL, hash_identifier("prepend"), 1),
                    code.make(Opcode.POP),
                ),
            ),
        ]

        self._test(test_cases)
