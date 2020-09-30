"""Turn a liquid.ast.ParseTree in to bytecode."""
from typing import NamedTuple, List, Any

from liquid import code
from liquid.code import Opcode
from liquid.object import CompiledBlock
from liquid.symbol import SymbolTable, SymbolScope, Symbol


class Bytecode(NamedTuple):
    """Liquid bytecode."""

    instructions: code.Instructions
    constants: List[Any]


class EmittedInstruction(NamedTuple):
    """And opcode at a position in our instruction list."""

    opcode: Opcode
    position: int


class CompilationScope:
    """Compile blocks independently"""

    __slots__ = ("instructions", "last_instruction", "previous_instruction")

    def __init__(
        self,
        instructions: code.Instructions,
        last_instruction: EmittedInstruction,
        previous_instruction: EmittedInstruction,
    ):

        self.instructions = instructions
        self.last_instruction = last_instruction
        self.previous_instruction = previous_instruction

    def __repr__(self):
        return (
            f"CompilationScope("
            f"instructions={self.instructions}, "
            f"last_instruction={self.last_instruction}, "
            f"previous_instruction={self.previous_instruction})"
        )


class Compiler:
    """Liquid parse tree compiler."""

    def __init__(self, symbol_table: SymbolTable = None, constants: List[Any] = None):
        self.constants = constants or []
        self.constants_index = {}
        self.symbol_table = symbol_table or SymbolTable()

        main_scope = CompilationScope(
            instructions=[],
            last_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
            previous_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
        )

        # Stack of scopes
        self.scopes: List[CompilationScope] = [main_scope]

        # A reference to the current scope. Maintained by enter_scope and leave_scope.
        self.current_scope = self.scopes[0]

    def compile(self, node):
        """Compile the template rooted at `node`."""
        node.compile(self)

    def current_instructions(self) -> code.Instructions:
        return self.current_scope.instructions

    def bytecode(self) -> Bytecode:
        """Return compiled bytecode."""
        return Bytecode(self.current_instructions(), self.constants)

    def add_constant(self, obj: Any) -> int:
        """Add the given object to the constant pool."""
        try:
            return self.constants_index[obj]
        except KeyError:
            self.constants.append(obj)
            idx = len(self.constants) - 1
            self.constants_index[obj] = idx
            return idx

    def add_constant_block(self, block: CompiledBlock) -> int:
        try:
            return self.constants.index(block)
        except ValueError:
            self.constants.append(block)
            idx = len(self.constants) - 1
            return idx

    def emit(self, op: code.Opcode, *operands: int) -> int:
        """Emit an instruction from the given opcode and operands."""
        ins = code.make(op, *operands)
        pos = self.add_instruction(ins)

        self.set_last_instruction(op, pos)
        return pos

    def add_instruction(self, ins: code.Instruction) -> int:
        """Append an instruction to the instruction list."""
        pos = len(self.current_instructions())
        self.current_scope.instructions.append(ins)
        return pos

    def last_instruction_is(self, op: Opcode) -> bool:
        if len(self.current_instructions()) == 0:
            return False
        return self.current_scope.last_instruction.opcode == op

    def remove_last_pop(self):
        last = self.current_scope.last_instruction
        prev = self.current_scope.previous_instruction

        old = self.current_instructions()
        new = old[: last.position]

        self.current_scope.instructions = new
        self.current_scope.last_instruction = prev

    def set_last_instruction(self, op: Opcode, pos: int):
        prev = self.current_scope.previous_instruction
        last = EmittedInstruction(op, pos)

        self.current_scope.previous_instruction = prev
        self.current_scope.last_instruction = last

    def replace_instruction(self, pos: int, new_instruction: code.Instruction):
        ins = self.current_instructions()
        ins[pos] = new_instruction

    def change_operand(self, pos: int, *operands: int):
        old_instruction = self.current_instructions()[pos]
        new_instruction = old_instruction._replace(operands=list(operands))
        self.replace_instruction(pos, new_instruction)

    def enter_scope(self):
        scope = CompilationScope(
            instructions=[],
            last_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
            previous_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
        )

        self.scopes.append(scope)
        self.current_scope = scope
        self.symbol_table = SymbolTable(outer=self.symbol_table)

    def leave_scope(self) -> code.Instructions:
        ins = self.current_instructions()

        self.scopes.pop()
        self.current_scope = self.scopes[-1]
        self.symbol_table = self.symbol_table.outer

        return ins

    def load_symbol(self, symbol: Symbol):
        if symbol.scope == SymbolScope.LOCAL:
            self.emit(Opcode.GLO, symbol.index)
        elif symbol.scope == SymbolScope.BLOCK:
            self.emit(Opcode.GBL, symbol.index)
        elif symbol.scope == SymbolScope.FREE:
            self.emit(Opcode.GFR, symbol.index)
