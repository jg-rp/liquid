import unittest

from liquid.symbol import SymbolTable, SymbolScope, Symbol


class SymbolTableTestCase(unittest.TestCase):
    def setUp(self):
        self.table = SymbolTable()

    def test_define(self):
        """Test that we can defined new symbols in the symbol table."""
        sym = self.table.define("a")
        self.assertEqual(sym, Symbol(name="a", scope=SymbolScope.LOCAL, index=0))

        sym = self.table.define("b")
        self.assertEqual(sym, Symbol(name="b", scope=SymbolScope.LOCAL, index=1))

    def test_resolve(self):
        """Test that we can get symbols back from the symbol table."""
        self.table.define("a")
        self.table.define("b")

        expected = [
            Symbol(name="a", scope=SymbolScope.LOCAL, index=0),
            Symbol(name="b", scope=SymbolScope.LOCAL, index=1),
        ]

        for want in expected:
            got = self.table.resolve(want.name)
            self.assertEqual(got, want)
