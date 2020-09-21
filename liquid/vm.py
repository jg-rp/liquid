from collections import OrderedDict
from collections import abc
from io import StringIO
from itertools import islice
from operator import getitem
from typing import Any, Mapping, NamedTuple, Iterator

from liquid.context import Context, ReadOnlyChainMap
from liquid import code
from liquid.code import Opcode
from liquid import compiler
from liquid.exceptions import StackOverflow, LiquidTypeError
from liquid.expression import compare, is_truthy

from liquid.builtin.tags.for_tag import ForLoopDrop
from liquid.object import Empty, StopIter, Nop


STACK_SIZE = 2048


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
                self.current_buffer().write(to_string(self.pop()))

            elif op == Opcode.TRU:
                self.push(True)

            elif op == Opcode.FAL:
                self.push(False)

            elif op == Opcode.NIL:
                self.push(None)

            elif op == Opcode.EMP:
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
                right = self.pop()
                left = self.pop()
                operator = code.COMPARISON_OPERATORS[op]

                self.push(compare(left, operator, right))

            elif op == Opcode.MIN:
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

            elif op == Opcode.JIE:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                if self.pop() == Empty:
                    ip = pos - 1

            elif op == Opcode.JSI:
                pos = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                if self.pop() == StopIter:
                    ip = pos - 1

            elif op == Opcode.NOP:
                self.push(Nop)

            elif op == Opcode.SLO:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self.context.locals[idx] = self.pop()

            elif op == Opcode.GLO:
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

            elif op == Opcode.RES:
                name = self.pop()
                obj = self.globals.get(name)
                self.push(obj)

            elif op == Opcode.GIT:
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
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                loop_start = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                loop_stop = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                self._exec_forloop(idx, loop_start, loop_stop)

            elif op == Opcode.STE:
                idx = code.read_uint16(self.instructions[ip + 1 : ip + 3])
                ip += 2

                it, drop, _, _ = self.iters[idx]

                try:
                    next_val = next(it)
                    drop.step(next_val)

                    self.context.locals[idx] = next_val
                    self.push(Nop)
                except StopIteration:
                    self._stop_iteration()
                    del self.context.locals[idx]

            elif op == Opcode.BRK:
                idx, it = self.iters.popitem()
                del self.context.locals[idx]
                self.pop_globals()
                ip = it.after_idx - 1

            elif op == Opcode.CON:
                idx, it = self.iters.popitem()

                try:
                    next_val = next(it.it)
                    it.drop.step(next_val)

                    self.context.locals[idx] = next_val
                    self.push(Nop)

                    ip = it.start_idx - 1
                    self.iters[idx] = it
                except StopIteration:
                    self._stop_iteration()
                    del self.context.locals[idx]

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

    def _exec_forloop(self, idx, loop_start, loop_stop):
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
            self.push(Empty)
        else:
            self.push(Nop)
            drop = ForLoopDrop(idx, len(items))
            for_it = ForIter(iter(items), drop, loop_start, loop_stop)
            self.iters[idx] = for_it

            # Init drop with first step
            next_val = next(for_it.it)
            drop.step(next_val)
            self.context.locals[idx] = next_val

            self.push_globals(drop)

    def _stop_iteration(self):
        self.pop_globals()
        self.push(StopIter)
        self.iters.popitem()

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

    def push_globals(self, globals: Mapping[int, Any]):
        self.globals.push(globals)

    def pop_globals(self) -> Mapping[Any, Any]:
        return self.globals.pop()


def to_string(val: Any) -> str:
    if isinstance(val, (list, tuple)):
        res = "".join(str(v) for v in val)
    elif isinstance(val, bool):
        res = str(val).lower()
    elif val is None:
        res = ""
    else:
        res = str(val)

    return res
