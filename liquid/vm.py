from collections import OrderedDict
from collections import abc
from io import StringIO
from itertools import islice
from operator import getitem
from typing import Any, Mapping, Iterator, List

from liquid.context import Context, ReadOnlyChainMap
from liquid import code
from liquid.code import Opcode
from liquid import compiler
from liquid.exceptions import StackOverflow, LiquidTypeError
from liquid.expression import compare, is_truthy

from liquid.builtin.tags.for_tag import ForLoopDrop
from liquid.object import Empty, StopIter, Nop
from liquid.frame import Frame
from liquid.object import CompiledBlock


STACK_SIZE = 2048
MAX_FRAMES = 1024


class ForIter(abc.Iterator):
    __slots__ = ("it", "drop", "before_idx", "after_idx")

    def __init__(
        self, it: Iterator, drop: ForLoopDrop, before_idx: int, after_idx: int
    ):
        self.it = it
        self.drop = drop
        self.before_idx = before_idx
        self.after_idx = after_idx

    def __next__(self):
        val = next(self.it)
        self.drop.step(val)
        return val


class VM:
    # pylint: disable=redefined-builtin
    def __init__(self, env, bytecode: compiler.Bytecode, context: Context = None):

        main_block = CompiledBlock(instructions=bytecode.instructions)
        main_frame = Frame(main_block, 0)

        self.frames: List[Frame] = [None] * MAX_FRAMES
        self.frames[0] = main_frame
        self.frames_idx: int = 1

        # self.instructions: code.Instructions = bytecode.instructions
        self.constants = bytecode.constants

        self.stack = [None] * STACK_SIZE
        self.stack_p = 0

        self.buffers = [StringIO()]

        self.context = context or Context(filters=env.filters)

        self.blocks = ReadOnlyChainMap()
        self.locals = ReadOnlyChainMap(self.blocks, self.context.locals)
        self.globals = ReadOnlyChainMap(
            self.blocks, self.context.globals, self.context._builtin
        )

        self.iters: "OrderedDict[int, ForIter]" = OrderedDict()

    def last_popped_stack_elem(self) -> Any:
        return self.stack[self.stack_p]

    # pylint: disable=too-many-branches too-many-statements
    def run(self):
        """Execute instructions"""
        while self.current_frame.ip < len(self.current_frame.instructions) - 1:
            self.current_frame.ip += 1

            instructions = self.current_frame.instructions
            op = Opcode(instructions[self.current_frame.ip])

            # print(
            #     f"{ip:04d}: stack: {self.stack[: self.stack_p]} {str(op)} {self.context.locals}"
            # )

            if op == Opcode.CONSTANT:
                const_idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

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
                pos = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip = pos - 1

            elif op == Opcode.JIF:
                pos = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                condition = self.pop()
                if is_truthy(condition):
                    self.current_frame.ip = pos - 1

            elif op == Opcode.JIN:
                pos = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                condition = self.pop()
                if not is_truthy(condition):
                    self.current_frame.ip = pos - 1

            elif op == Opcode.JIE:
                pos = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                if self.pop() == Empty:
                    self.current_frame.ip = pos - 1

            elif op == Opcode.JSI:
                pos = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                if self.pop() == StopIter:
                    self.current_frame.ip = pos - 1

            elif op == Opcode.NOP:
                self.push(Nop)

            elif op == Opcode.SLO:
                idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                self.context.locals[idx] = self.pop()

            elif op == Opcode.GLO:
                idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                self.push(self.locals.get(idx))

            elif op == Opcode.CAPTURE:
                self.push_buffer()

            elif op == Opcode.SETCAPTURE:
                value = self.pop_buffer()

                idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

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
                idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                self.push(self.context.decrement(idx))

            elif op == Opcode.INC:
                idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                self.push(self.context.increment(idx))

            elif op == Opcode.CYC:
                num_args = code.read_uint8(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 2]
                )
                self.current_frame.ip += 1

                group = self.pop()
                args = [self.pop() for _ in range(num_args)]

                self.push(next(self.context.cycle(group, args)))

            elif op == Opcode.BLK:
                block = self.stack[self.stack_p - 1]  # TODO: pop
                assert isinstance(block, CompiledBlock)

                frame = Frame(
                    block=block, base_pointer=self.stack_p
                )  # TODO: - num-args
                self.push_frame(frame)
                self.stack_p = frame.base_pointer + block.num_locals

            elif op == Opcode.FOR:
                idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                loop_start = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                loop_stop = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                self._exec_forloop(idx, loop_start, loop_stop)

            elif op == Opcode.STE:
                idx = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                it = self.iters[idx]

                try:
                    next(it)
                    self.push(Nop)
                except StopIteration:
                    self._stop_iteration()

            elif op == Opcode.BRK:
                _, it = self.iters.popitem()
                self.pop_block()
                self.current_frame.ip = it.after_idx - 1

            elif op == Opcode.CON:
                idx, it = self.iters.popitem()
                self.iters[idx] = it  # Need to put the iterator back

                try:
                    next(it)
                    self.push(Nop)
                    self.current_frame.ip = it.before_idx - 1
                except StopIteration:
                    self._stop_iteration()

            elif op == Opcode.FIL:
                fltr_id = code.read_uint16(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 3]
                )
                self.current_frame.ip += 2

                num_args = code.read_uint8(
                    instructions[self.current_frame.ip + 1 : self.current_frame.ip + 2]
                )
                self.current_frame.ip += 1

                args = [self.pop() for _ in range(num_args)]
                val = self.pop()

                func = self.context.resolve_filter(fltr_id)
                res = func(val, *args)

                self.push(res)

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
            it = start.items()
        else:
            raise LiquidTypeError(f"can't iterate object '{start}'")

        limit = self.pop()
        offset = self.pop()
        reverse = self.pop()

        it = islice(it, offset, limit)

        if reverse:
            it = reversed(list(it))

        # Need to know the length of the sequence
        items = list(it)
        it = iter(items)

        if not items:
            self.push(Empty)
        else:
            self.push(Nop)

            drop = ForLoopDrop(idx, len(items))
            self.push_block(drop)

            for_it = ForIter(it, drop, loop_start, loop_stop)
            self.iters[idx] = for_it

            # Init drop with first step
            next(for_it)

    def _stop_iteration(self):
        self.pop_block()
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

    @property
    def current_frame(self) -> Frame:
        return self.frames[self.frames_idx - 1]

    def push_frame(self, frame: Frame):
        self.frames[self.frames_idx] = frame
        self.frames_idx += 1

    def pop_frame(self) -> Frame:
        self.frames_idx -= 1
        return self.frames[self.frames_idx]

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

    def push_block(self, mapping: Mapping[int, Any]):
        self.blocks.push(mapping)

    def pop_block(self) -> Mapping[Any, Any]:
        return self.blocks.pop()

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
