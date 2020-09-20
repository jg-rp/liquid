from collections import OrderedDict
from collections import abc
from io import StringIO
from itertools import islice
from operator import getitem
from typing import Any, Mapping, NamedTuple, Iterator, Tuple, Iterable

from liquid.context import Context, ReadOnlyChainMap
from liquid import code
from liquid.code import Opcode
from liquid import compiler
from liquid.exceptions import StackOverflow, LiquidTypeError

from liquid.builtin.tags.for_tag import ForLoopDrop


STACK_SIZE = 2048

# TODO: Move these to liquid.object


class EmptyObj:
    __slots__ = ()

    def __repr__(self):
        return "Empty()"

    def __str__(self):
        return ""


Empty = EmptyObj()


class StopIterObj:
    __slots__ = ()

    def __repr__(self):
        return "StopIter()"

    def __str__(self):
        return ""


StopIter = StopIterObj()


class NoOp:
    __slots__ = ()

    def __repr__(self):
        return "NoOp()"

    def __str__(self):
        return ""


Nop = NoOp()


class ForIter(NamedTuple):
    it: Iterator
    drop: ForLoopDrop
    start_idx: int
    after_idx: int


class VM:
    # pylint: disable=redefined-builtin
    def __init__(self, env, bytecode: compiler.Bytecode, context: Context = None):
        self.instructions: code.Instructions = bytecode.instructions
        self.constants = bytecode.constants

        self.stack = [None] * STACK_SIZE
        self.stack_p = 0

        self.buffers = [StringIO()]
        self.context = context or Context(filters=env.filters)
        self.locals = ReadOnlyChainMap(self.context.locals)
        self.globals = ReadOnlyChainMap(self.context.globals, self.context._builtin)

        self.iters = OrderedDict()

    def last_popped_stack_elem(self) -> Any:
        return self.stack[self.stack_p]

    # pylint: disable=too-many-branches too-many-statements
    def run(self):
        """Execute instructions"""
        ip = 0  # Instruction pointer
        while ip < len(self.instructions):
            op = Opcode(self.instructions[ip])

            # print(
            #     f"{ip:04d}: stack: {self.stack[: self.stack_p]} {str(op)} {self.context.locals}"
            # )

            if op == Opcode.CONSTANT:
                const_idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.push(self.constants[const_idx])

            elif op == Opcode.POP:
                self.current_buffer().write(str(self.pop()))

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

            elif op == Opcode.JMP:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip = pos - 1

            elif op == Opcode.JIF:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                condition = self.pop()
                if is_truthy(condition):
                    ip = pos - 1

            elif op == Opcode.JIN:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                condition = self.pop()
                if not is_truthy(condition):
                    ip = pos - 1

            elif op == Opcode.NOP:
                self.push(Nop)

            elif op == Opcode.SETLOCAL:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.context.locals[idx] = self.pop()

            elif op == Opcode.GETLOCAL:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.push(self.locals[idx])

            elif op == Opcode.CAPTURE:
                self.push_buffer()

            elif op == Opcode.SETCAPTURE:
                value = self.pop_buffer()

                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.context.locals[idx] = value

            elif op == Opcode.RESOLVE:
                name = self.pop()
                obj = self.globals.get(name)
                self.push(obj)

            elif op == Opcode.GETITEM:
                item = self.pop()
                obj = self.pop()
                try:
                    self.push(getitem(obj, item))
                except (KeyError, IndexError, TypeError):
                    self.push(None)

            elif op == Opcode.DEC:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.push(self.context.decrement(idx))

            elif op == Opcode.INC:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.push(self.context.increment(idx))

            elif op == Opcode.CYC:
                num_args = code.read_uint8(self.instructions[ip + 1 : ip + 2])
                ip += 1

                group = self.pop()

                args = [self.pop() for _ in range(num_args)]

                self.push(next(self.context.cycle(group, args)))

            elif op == Opcode.FOR:
                # Index of loop variable
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                # Start of loop position
                start_loop_idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                # End of loop position
                after_loop_idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                # Range start or collection to iterate
                start = self.pop()
                # Range stop. Will be None if start is a collection.
                stop = self.pop()

                if isinstance(start, int):
                    assert isinstance(stop, int)
                    it = range(start, stop + 1)
                elif isinstance(start, abc.Sequence):
                    it = iter(start)
                elif isinstance(start, abc.Mapping):
                    it = iter(start.items())
                else:
                    raise LiquidTypeError(f"can't iterate object '{start}'")

                limit = self.pop()
                offset = self.pop()
                reverse = self.pop()

                it = islice(it, offset, limit)

                if reverse:
                    it = reversed(list(it))

                items = list(it)

                if not items:
                    self.context.locals[idx] = Empty
                else:
                    drop = ForLoopDrop(idx, len(items))
                    self.iters[idx] = ForIter(
                        iter(items), drop, start_loop_idx, after_loop_idx
                    )

                    # Init drop with first step
                    next_val = next(self.iters[idx].it)
                    drop.step(next_val)

                    self.push_scope(drop, drop)  # XXX:

            elif op == Opcode.JIE:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                if self.locals[idx] == Empty:
                    ip = pos - 1

            elif op == Opcode.JSI:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                if self.locals[idx] == StopIter:
                    ip = pos - 1
                    del self.context.locals[idx]

            elif op == Opcode.STE:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                it, drop, _, _ = self.iters[idx]

                try:
                    next_val = next(it)
                    drop.step(next_val)
                except StopIteration:
                    self.pop_scope()
                    self.context.locals[idx] = StopIter
                    self.iters.popitem()

            elif op == Opcode.BRK:
                _, it = self.iters.popitem()
                self.pop_scope()
                ip = it.after_idx - 1

            elif op == Opcode.CON:
                idx, it = self.iters.popitem()

                try:
                    next_val = next(it.it)
                    it.drop.step(next_val)
                    ip = it.start_idx - 1
                    self.iters[idx] = it
                except StopIteration:
                    self.pop_scope()
                    self.context.locals[idx] = StopIter

            elif op == Opcode.FIL:
                fltr_id = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                num_args = code.read_uint8(self.instructions[ip + 1 : ip + 2])
                ip += 1

                args = [self.pop() for _ in range(num_args)]
                val = self.pop()

                func = self.context.resolve_filter(fltr_id)
                res = func(val, *args)

                self.push(res)

            ip += 1

    def _exec_comparison(self, op: Opcode):
        right = self.pop()
        left = self.pop()

        if isinstance(left, bool) and isinstance(right, bool):
            self._exec_bool_comparison(left, op, right)
        elif Empty in (left, right):
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
        """Push the given object on to the top of the stack."""
        if self.stack_p >= STACK_SIZE:
            raise StackOverflow()

        self.stack[self.stack_p] = obj
        self.stack_p += 1

    def pop(self) -> Any:
        """Pop an object off the top of the stack."""
        obj = self.stack[self.stack_p - 1]
        self.stack_p -= 1
        return obj

    def current_buffer(self) -> StringIO:
        """Return the current ouput buffer."""
        return self.buffers[-1]

    def push_buffer(self):
        """Start a new ouput buffer."""
        self.buffers.append(StringIO())

    def pop_buffer(self) -> Any:
        """Pop the current buffer of the buffer stack and return it."""
        buf = self.buffers.pop()
        return buf.getvalue()

    def push_scope(self, locals: Mapping[int, Any], globals: Mapping[int, Any]):
        self.locals.push(locals)
        self.globals.push(globals)

    def pop_scope(self) -> Tuple[Mapping[Any, Any], Mapping[Any, Any]]:
        return (self.locals.pop(), self.globals.pop())


def is_truthy(obj: Any) -> bool:
    """Return True if the given object is Liquid truthy."""
    if obj in (False, None):
        return False
    return True
