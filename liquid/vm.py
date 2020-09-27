from collections import abc
from io import StringIO
from itertools import islice
from operator import getitem
from typing import Any, Iterator, List, Dict

from liquid.context import Context, ReadOnlyChainMap
from liquid import code
from liquid.code import Opcode
from liquid import compiler
from liquid.exceptions import StackOverflow, LiquidTypeError
from liquid.expression import compare, is_truthy

from liquid.builtin.drops import IterableDrop
from liquid.builtin.tags.for_tag import ForLoopDrop
from liquid.builtin.tags.tablerow_tag import TableRowDrop


from liquid.object import Empty, Nop, CompiledBlock
from liquid.block import Block


STACK_SIZE = 2048


class LoopIter(abc.Iterator):
    __slots__ = ("it", "drop")

    def __init__(
        self,
        it: Iterator,
        drop: IterableDrop,
    ):
        self.it = it
        self.drop = drop

    def __next__(self):
        val = next(self.it)
        self.drop.step(val)
        return val

    def __repr__(self):
        return "LoopIter(..)"

    def step(self, buffer):
        val = next(self.it)
        self.drop.step_write(val, buffer)
        return val

    def empty_exit_buffer(self, buffer):
        self.drop.empty_exit_buffer(buffer)


class VM:
    def __init__(self, env, bytecode: compiler.Bytecode, context: Context = None):

        self.blocks: Dict[int, Block] = {
            0: Block(CompiledBlock(instructions=bytecode.instructions), 0)
        }
        self.blocks_idx: int = 1

        # self.instructions: code.Instructions = bytecode.instructions
        self.constants = bytecode.constants

        self.stack: List[Any] = [None] * STACK_SIZE
        self.sp = 0  # Stack pointer

        # Stack of file-like objects for rendering to. The only built-in tag
        # that uses anything other than the main buffer is the `capture` tag.
        self.buffers = [StringIO()]

        self.context = context or Context(filters=env.filters)

        self.locals = ReadOnlyChainMap(self.context.locals)
        self.globals = ReadOnlyChainMap(self.context.globals, self.context._builtin)

    def last_popped_stack_elem(self) -> Any:
        """Helper method used for testing only."""
        return self.stack[self.sp]

    # pylint: disable=too-many-branches too-many-statements
    def run(self):
        """Execute instructions"""
        while self.current_block.ip < len(self.current_block.instructions) - 1:
            self.current_block.ip += 1

            instructions = self.current_block.instructions
            op = Opcode(instructions[self.current_block.ip])

            # print(
            #     f"{self.current_block.ip:04d}: stack: {self.stack[: self.sp]} {str(op)} {self.context.locals}"
            # )

            if op == Opcode.CONSTANT:
                const_idx = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                self.push(self.constants[const_idx])

            elif op == Opcode.POP:
                self.current_buffer.write(to_string(self.pop()))

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
                operator = code.INFIX_OPERATORS[op]

                self.push(compare(left, operator, right))

            elif op == Opcode.NEG:
                operand = self.pop()

                if not isinstance(operand, (int, float)):
                    raise LiquidTypeError(f"unknown operator {op} ({operand})")

                self.push(-operand)

            elif op == Opcode.JMP:
                pos = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip = pos - 1

            elif op == Opcode.JIF:
                pos = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                condition = self.pop()
                if is_truthy(condition):
                    self.current_block.ip = pos - 1

            elif op == Opcode.JIN:
                pos = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                condition = self.pop()
                if not is_truthy(condition):
                    self.current_block.ip = pos - 1

            elif op == Opcode.JIE:
                pos = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                if self.pop() == Empty:
                    self.current_block.ip = pos - 1

            elif op == Opcode.NOP:
                self.push(Nop)

            elif op == Opcode.SLO:
                idx = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                self.context.locals[idx] = self.pop()

            elif op == Opcode.GLO:
                idx = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                self.push(self.locals.get(idx))

            elif op == Opcode.GBL:
                idx = code.read_uint8(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                self.push(self.stack[self.current_block.base_pointer + idx])

            elif op == Opcode.GFR:
                idx = code.read_uint8(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                self.push(self.current_block.free[idx])

            elif op == Opcode.CAPTURE:
                self.push_buffer()

            elif op == Opcode.SETCAPTURE:
                value = self.pop_buffer()

                idx = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

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
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                self.push(self.context.decrement(idx))

            elif op == Opcode.INC:
                idx = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                self.push(self.context.increment(idx))

            elif op == Opcode.CYC:
                num_args = code.read_uint8(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                group = self.pop()
                args = [self.pop() for _ in range(num_args)]

                self.push(next(self.context.cycle(group, args)))

            elif op == Opcode.FOR:
                num_block_vars = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                num_free_vars = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                self._exec_forloop(num_block_vars, num_free_vars)

            elif op == Opcode.TAB:
                num_block_vars = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                num_free_vars = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                self._exec_tablerow(num_block_vars, num_free_vars)

            elif op == Opcode.STE:
                idx = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                it = self.stack[self.sp - 1]
                assert isinstance(it, LoopIter), f"expected LoopIter, found {repr(it)}"

                # TODO: Test shopify for tablerow inside forloop

                try:
                    val = it.step(self.current_buffer)
                    self.stack[self.current_block.base_pointer + idx] = val
                except StopIteration:
                    it.empty_exit_buffer(self.current_buffer)
                    self._stop_iteration()

            elif op == Opcode.BRK:
                block = self.pop_block()
                self.sp = block.base_pointer - 1

                # Keep popping blocks off the stack until we find a for loop.
                # For loops are the only blocks that respond to a break.
                while not block.forloop:
                    block = self.pop_block()
                    self.sp = block.base_pointer - 1

            elif op == Opcode.STO:
                self._stop_iteration()

            elif op == Opcode.CON:
                # FIXME: What if the current block is not a for loop?
                it = self.stack[self.sp - 1]
                assert isinstance(it, LoopIter)

                try:
                    val = next(it)
                    # Loop var is always at index 0 (from base_pointer)
                    self.stack[self.current_block.base_pointer] = val
                    # First block instruction is always at instruction 3
                    self.current_block.ip = 2
                except StopIteration:
                    self._stop_iteration()

            elif op == Opcode.FIL:
                fltr_id = code.read_uint16(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 3]
                )
                self.current_block.ip += 2

                num_args = code.read_uint8(
                    instructions[self.current_block.ip + 1 : self.current_block.ip + 2]
                )
                self.current_block.ip += 1

                args = [self.pop() for _ in range(num_args)]
                val = self.pop()

                func = self.context.resolve_filter(fltr_id)
                res = func(val, *args)

                self.push(res)

    def _exec_forloop(self, num_block_vars, num_free_vars):
        # Need to know the length of the sequence
        items = list(self._make_iter())
        it = iter(items)

        free_vars = [self.pop() for _ in range(num_free_vars)]

        compiled_block = self.stack[self.sp - 1]
        assert isinstance(compiled_block, CompiledBlock)

        block = Block(
            block=compiled_block,
            base_pointer=self.sp,
            free=free_vars,
            forloop=True,
        )
        self.push_block(block)
        self.sp = block.base_pointer + compiled_block.num_locals

        if not items:
            self.push(Empty)
        else:
            drop = ForLoopDrop(0, len(items))
            for_it = LoopIter(it, drop)

            # Initialise drop with first step
            val = next(for_it)

            self.stack[self.current_block.base_pointer + 0] = val
            self.stack[self.current_block.base_pointer + 1] = drop.forloop

            self.push(for_it)
            self.push(Nop)

    def _exec_tablerow(self, num_block_vars, num_free_vars):
        items = list(self._make_iter())

        cols = self.pop()
        if not cols:
            cols = len(items)

        free_vars = [self.pop() for _ in range(num_free_vars)]

        compiled_block = self.stack[self.sp - 1]
        assert isinstance(compiled_block, CompiledBlock)

        block = Block(
            block=compiled_block,
            base_pointer=self.sp,
            free=free_vars,
            forloop=False,
        )
        self.push_block(block)
        self.sp = block.base_pointer + compiled_block.num_locals

        # TODO: Test shopify for empty tablerow

        drop = TableRowDrop("", len(items), cols)
        for_it = LoopIter(iter(items), drop)

        # Initialise drop with first step
        val = for_it.step(self.current_buffer)

        self.stack[self.current_block.base_pointer + 0] = val
        self.stack[self.current_block.base_pointer + 1] = drop.tablerow

        self.push(for_it)

    def _make_iter(self) -> Iterator:
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

        return it

    def _stop_iteration(self):
        block = self.pop_block()
        self.sp = block.base_pointer - 1

    def push(self, obj: Any):
        """Push the given object on to the top of the stack."""
        if self.sp >= STACK_SIZE:
            raise StackOverflow()

        self.stack[self.sp] = obj
        self.sp += 1

    def pop(self) -> Any:
        """Pop an object off the top of the stack."""
        obj = self.stack[self.sp - 1]
        self.sp -= 1
        return obj

    @property
    def current_block(self) -> Block:
        return self.blocks[self.blocks_idx - 1]

    def push_block(self, block: Block):
        self.blocks[self.blocks_idx] = block
        self.blocks_idx += 1

    def pop_block(self) -> Block:
        self.blocks_idx -= 1
        block = self.blocks[self.blocks_idx]
        del self.blocks[self.blocks_idx]
        return block

    @property
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
