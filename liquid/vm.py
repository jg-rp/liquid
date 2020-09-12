from typing import Any, List


from liquid import code
from liquid.code import Opcode
from liquid import compiler
from liquid.exceptions import StackOverflow, LiquidTypeError


STACK_SIZE = 2048
GLOBALS_SIZE = 65536
LOCALS_SIZE = 65536

Empty = object()
Noop = object()


class VM:
    def __init__(self, bytecode: compiler.Bytecode, locals: List[Any] = None):
        self.instructions: code.Instructions = bytecode.instructions
        self.constants = bytecode.constants

        self.stack = [None] * STACK_SIZE
        self.sp = 0

        self.locals = locals or [None] * LOCALS_SIZE

    def last_popped_stack_elem(self) -> Any:
        return self.stack[self.sp]

    def run(self):
        ip = 0  # Instruction pointer
        while ip < len(self.instructions):
            op = Opcode(self.instructions[ip])

            if op == Opcode.CONSTANT:
                const_idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.push(self.constants[const_idx])

            elif op == Opcode.POP:
                self.pop()

            elif op == Opcode.TRUE:
                self.push(True)

            elif op == Opcode.FALSE:
                self.push(False)

            elif op == Opcode.NIL:
                self.push(None)

            elif op == Opcode.EMPTY:
                self.push(Empty)

            elif op in (
                Opcode.EQ,
                Opcode.NE,
                Opcode.GT,
                Opcode.GE,
                Opcode.CONTAINS,
                Opcode.AND,
                Opcode.OR,
            ):
                self._exec_comparison(op)

            elif op == Opcode.MINUS:
                operand = self.pop()

                if not isinstance(operand, (int, float)):
                    raise LiquidTypeError(f"unknown operator {op} ({operand})")

                self.push(-operand)

            elif op == Opcode.JUMP:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip = pos - 1

            elif op == Opcode.JUMPIFNOT:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                condition = self.pop()
                if not is_truthy(condition):
                    ip = pos - 1

            elif op == Opcode.NOP:
                self.push(Noop)

            elif op == Opcode.SETLOCAL:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.locals[idx] = self.pop()

            elif op == Opcode.GETLOCAL:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.push(self.locals[idx])

            ip += 1

    def _exec_comparison(self, op: Opcode):
        right = self.pop()
        left = self.pop()

        # XXX: Hmmm? might want an object repr after all.

        if isinstance(left, bool) and isinstance(right, bool):
            self._exec_bool_comparison(left, op, right)
        elif left == Empty or right == Empty:
            self._exec_empty_comparison(left, op, right)
        elif type(left) in (int, float) and type(right) in (int, float):
            self._exec_number_comparison(left, op, right)
        elif isinstance(left, str) and isinstance(right, str):
            self._exec_string_comparison(left, op, right)
        else:
            if op == Opcode.CONTAINS:
                if isinstance(left, str):
                    self.push(str(right) in left)
                if isinstance(left, (list, dict)):
                    self.push(right in left)
            if op == Opcode.EQ:
                self.push(left == right)
            if op == Opcode.NE:
                self.push(left != right)
            else:
                raise LiquidTypeError(f"unknown operator {op} ({left}, {right})")

    def _exec_bool_comparison(self, left, op, right):
        if op == Opcode.EQ:
            self.push(left == right)
        elif op == Opcode.NE:
            self.push(left != right)
        elif op == Opcode.AND:
            self.push(left and right)
        elif op == Opcode.OR:
            self.push(left or right)
        else:
            raise LiquidTypeError(f"unknown operator {op} ({left}, {right})")

    def _exec_empty_comparison(self, left, op, right):
        if not left == Empty:
            left, right = right, left

        is_equal = False

        if right == Empty:
            is_equal = True
        elif isinstance(right, (list, dict, str)) and not right:
            is_equal = True

        if op == Opcode.EQ:
            self.push(is_equal)
        elif op == Opcode.NE:
            self.push(not is_equal)
        else:
            raise LiquidTypeError(f"unknown operator {op} ({left}, {right})")

    def _exec_number_comparison(self, left, op, right):
        if op == Opcode.EQ:
            self.push(left == right)
        elif op == Opcode.GE:
            self.push(left <= right)
        elif op == Opcode.GT:
            self.push(left > right)
        elif op == Opcode.NE:
            self.push(left != right)
        else:
            raise LiquidTypeError(f"unknown operator {op} ({left}, {right})")

    def _exec_string_comparison(self, left, op, right):
        if op == Opcode.EQ:
            self.push(left == right)
        elif op == Opcode.NE:
            self.push(left != right)
        elif op == Opcode.CONTAINS:
            self.push(right in left)
        else:
            raise LiquidTypeError(f"unknown operator {op} ({left}, {right})")

    def push(self, obj: Any):
        if self.sp >= STACK_SIZE:
            raise StackOverflow()

        self.stack[self.sp] = obj
        self.sp += 1

    def pop(self) -> Any:
        obj = self.stack[self.sp - 1]
        self.sp -= 1
        return obj


def is_truthy(obj: Any) -> bool:
    if obj in (False, None):
        return False
    return True
