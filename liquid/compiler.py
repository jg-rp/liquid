"""Turn a liquid.ast.ParseTree in to bytecode."""
from dataclasses import dataclass
from typing import NamedTuple, List, Any

from liquid import code
from liquid.code import Opcode
from liquid.symbol import SymbolTable


# TODO:
# - Compilation scopes for "capture" and "inline render" support
# - Stack frames for adding locals to block tags and executing "capture"
# - "locals" are variables defined with "assign" or "capture"
# - `case` gets compiled to `if else..`
# - `unless` gets compiled to `if else ..`
# - "globals" is a pre-defined mapping populated at render time
# - "render" or "write" stack to buffer
# - filters are built-in functions

# = "built-in globals" = built-in and env/template/render context
# = global bindings = local bindings (assign, capture)
# = local bindings = block bindings (if, tablerow)
# = CompiledFunction = CompiledBlock
# = OpFunctionLiteral + OpCall = OpBlock
# = "call frame" for functions = "block frame" for blocks


class Bytecode(NamedTuple):
    """Liquid bytecode."""

    instructions: code.Instructions
    constants: List[Any]


class EmittedInstruction(NamedTuple):
    """And opcode at a position in our instruction list"""

    opcode: Opcode
    position: int


@dataclass
class CompilationScope:
    """Compile blocks independently"""

    instructions: code.Instructions
    last_instruction: EmittedInstruction
    previous_instruction: EmittedInstruction


class Compiler:
    """Liquid parse tree compiler."""

    def __init__(self, symbol_table: SymbolTable = None, constants: List[Any] = None):
        self.constants = constants or []
        self.symbol_table = symbol_table or SymbolTable()

        main_scope = CompilationScope(
            instructions=[],
            last_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
            previous_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
        )

        self.scopes: List[CompilationScope] = [main_scope]
        self.scope_idx = 0

    def compile(self, node):
        """Compile the template rooted at `node`."""
        node.compile(self)

    def current_instructions(self) -> code.Instructions:
        return self.scopes[self.scope_idx].instructions

    def bytecode(self) -> Bytecode:
        """Return compiled bytecode."""
        return Bytecode(self.current_instructions(), self.constants)

    def add_constant(self, obj: Any) -> int:
        """Add the given object to the constant pool."""
        try:
            return self.constants.index(obj)
        except ValueError:
            self.constants.append(obj)
            return len(self.constants) - 1

    def emit(self, op: code.Opcode, *operands: int) -> int:
        """Emit an instruction from the given opcode and operands."""
        ins = code.make(op, *operands)
        pos = self.add_instruction(ins)

        self.set_last_instruction(op, pos)

        return pos

    def add_instruction(self, ins: code.Instruction) -> int:
        """Append an instruction to the instruction list."""
        pos = len(self.current_instructions())
        self.scopes[self.scope_idx].instructions.extend(ins)
        return pos

    def last_instruction_is(self, op: Opcode) -> bool:
        if len(self.current_instructions()) == 0:
            return False
        return self.scopes[self.scope_idx].last_instruction.opcode == op

    def remove_last_pop(self):
        last = self.scopes[self.scope_idx].last_instruction
        prev = self.scopes[self.scope_idx].previous_instruction

        old = self.current_instructions()
        new = old[: last.position]

        self.scopes[self.scope_idx].instructions = new
        self.scopes[self.scope_idx].last_instruction = prev

    def set_last_instruction(self, op: Opcode, pos: int):
        prev = self.scopes[self.scope_idx].previous_instruction
        last = EmittedInstruction(op, pos)

        self.scopes[self.scope_idx].previous_instruction = prev
        self.scopes[self.scope_idx].last_instruction = last

    def replace_instruction(self, pos: int, new_instruction: code.Instruction):
        ins = self.current_instructions()

        for i, byte in enumerate(new_instruction):
            ins[pos + i] = byte

    def change_operand(self, pos: int, *operand: int):
        op = Opcode(self.current_instructions()[pos])
        ins = code.make(op, *operand)
        self.replace_instruction(pos, ins)

    def enter_scope(self):
        scope = CompilationScope(
            instructions=[],
            last_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
            previous_instruction=EmittedInstruction(opcode=Opcode.NOP, position=-1),
        )

        self.scopes.append(scope)
        self.scope_idx += 1
        self.symbol_table = SymbolTable(outer=self.symbol_table)

    def leave_scope(self) -> code.Instructions:
        ins = self.current_instructions()

        self.scopes.pop()
        self.scope_idx -= 1
        self.symbol_table = self.symbol_table.outer

        return ins
