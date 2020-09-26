import unittest
from typing import NamedTuple, List

from liquid.symbol import SymbolTable, SymbolScope, Symbol


class Case(NamedTuple):
    description: str
    symbol_table: SymbolTable
    expected_symbols: List[Symbol]


class SymbolTableTestCase(unittest.TestCase):
    def setUp(self):
        self.template_locals = SymbolTable()

    def test_define(self):
        """Test that we can defined new symbols in the symbol table."""
        sym = self.template_locals.define("a")
        self.assertEqual(sym, Symbol(name="a", scope=SymbolScope.LOCAL, index=0))

        sym = self.template_locals.define("b")
        self.assertEqual(sym, Symbol(name="b", scope=SymbolScope.LOCAL, index=1))

        first_block = SymbolTable(outer=self.template_locals)

        sym = first_block.define("c")
        self.assertEqual(sym, Symbol(name="c", scope=SymbolScope.BLOCK, index=0))

        sym = first_block.define("d")
        self.assertEqual(sym, Symbol(name="d", scope=SymbolScope.BLOCK, index=1))

        second_block = SymbolTable(outer=self.template_locals)

        sym = second_block.define("e")
        self.assertEqual(sym, Symbol(name="e", scope=SymbolScope.BLOCK, index=0))

        sym = second_block.define("f")
        self.assertEqual(sym, Symbol(name="f", scope=SymbolScope.BLOCK, index=1))

    def test_resolve(self):
        """Test that we can get symbols back from the symbol table."""
        self.template_locals.define("a")
        self.template_locals.define("b")

        expected = [
            Symbol(name="a", scope=SymbolScope.LOCAL, index=0),
            Symbol(name="b", scope=SymbolScope.LOCAL, index=1),
        ]

        for want in expected:
            got = self.template_locals.resolve(want.name)
            self.assertEqual(got, want)

    def test_resolve_block(self):
        self.template_locals.define("a")
        self.template_locals.define("b")

        block = SymbolTable(outer=self.template_locals)
        block.define("c")
        block.define("d")

        expected = [
            Symbol(name="a", scope=SymbolScope.LOCAL, index=0),
            Symbol(name="b", scope=SymbolScope.LOCAL, index=1),
            Symbol(name="c", scope=SymbolScope.BLOCK, index=0),
            Symbol(name="d", scope=SymbolScope.BLOCK, index=1),
        ]

        for want in expected:
            got = block.resolve(want.name)
            self.assertEqual(got, want)

    def test_resolve_nested_block(self):
        self.template_locals.define("a")
        self.template_locals.define("b")

        first_block = SymbolTable(outer=self.template_locals)
        first_block.define("c")
        first_block.define("d")

        second_block = SymbolTable(outer=first_block)
        second_block.define("e")
        second_block.define("f")

        self.template_locals.define("g")

        tests_cases = [
            Case(
                description="first block",
                symbol_table=first_block,
                expected_symbols=[
                    Symbol(name="a", scope=SymbolScope.LOCAL, index=0),
                    Symbol(name="b", scope=SymbolScope.LOCAL, index=1),
                    Symbol(name="c", scope=SymbolScope.BLOCK, index=0),
                    Symbol(name="d", scope=SymbolScope.BLOCK, index=1),
                    Symbol(name="g", scope=SymbolScope.LOCAL, index=2),
                ],
            ),
            Case(
                description="second block",
                symbol_table=second_block,
                expected_symbols=[
                    Symbol(name="a", scope=SymbolScope.LOCAL, index=0),
                    Symbol(name="b", scope=SymbolScope.LOCAL, index=1),
                    Symbol(name="e", scope=SymbolScope.BLOCK, index=0),
                    Symbol(name="f", scope=SymbolScope.BLOCK, index=1),
                    Symbol(name="c", scope=SymbolScope.FREE, index=0),
                    Symbol(name="d", scope=SymbolScope.FREE, index=1),
                    Symbol(name="g", scope=SymbolScope.LOCAL, index=2),
                ],
            ),
        ]

        for case in tests_cases:
            with self.subTest(msg=case.description):
                for sym in case.expected_symbols:
                    got = case.symbol_table.resolve(sym.name)
                    self.assertEqual(got, sym)
