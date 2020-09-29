import math
from collections import abc
from io import StringIO
from itertools import islice
from typing import Any, Iterator, List, Mapping

from liquid.context import Context, ReadOnlyChainMap, _getitem
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

# TODO: Move me
from tests.mocks.tags.paginate_tag import link, no_link


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


def execute(env, bytecode: compiler.Bytecode, context: Context = None) -> str:
    vm = VM(env, bytecode, context)
    vm.run()
    return vm.current_buffer.getvalue()


class VM:
    def __init__(self, env, bytecode: compiler.Bytecode, context: Context = None):
        self.current_block = Block(CompiledBlock(instructions=bytecode.instructions), 0)
        self.blocks: List[Block] = [self.current_block]

        # self.instructions: code.Instructions = bytecode.instructions
        self.constants = bytecode.constants

        self.stack: List[Any] = [None] * STACK_SIZE
        self.sp = 0  # Stack pointer

        # Stack of file-like objects for rendering to. The only built-in tag
        # that uses anything other than the main buffer is the `capture` tag.
        self.current_buffer = StringIO()
        self.buffers = [self.current_buffer]

        self.context = context or Context(filters=env.filters)

        self.locals = {}
        self.globals = ReadOnlyChainMap(self.context.globals, self.context._builtin)

    def last_popped_stack_elem(self) -> Any:
        """Helper method used for testing only."""
        return self.stack[self.sp]

    # pylint: disable=too-many-branches too-many-statements
    def run(self):
        """Execute instructions"""

        while self.current_block.ip < self.current_block.instruction_count - 1:
            current_block = self.current_block
            current_block.ip += 1

            ip = current_block.ip
            instructions = current_block.instructions

            op = instructions[ip]

            # TODO: setup logging
            # print(
            #     f"{self.current_block.ip:04d}: stack: {self.pprint_stack()} {str(op)} {self.context.locals}"
            # )

            if op == Opcode.CONSTANT:
                high, low = instructions[ip + 1 : ip + 3]
                const_idx = (high << 8) + low
                current_block.ip += 2

                self.push(self.constants[const_idx])

            elif op == Opcode.POP:
                self.current_buffer.write(to_string(self.pop()))

            elif op == Opcode.FIL:
                high, low = instructions[ip + 1 : ip + 3]
                fltr_id = (high << 8) + low

                num_args = instructions[ip + 3]
                current_block.ip += 3

                args = [self.pop() for _ in range(num_args)]
                val = self.pop()

                func = self.context.filter(fltr_id)
                res = func(val, *args)

                self.push(res)

            elif op == Opcode.GIT:
                item = self.pop()
                obj = self.pop()
                try:
                    self.push(_getitem(obj, item))
                except (KeyError, IndexError, TypeError):
                    self.push(None)

            elif op == Opcode.RES:
                name = self.pop()
                obj = self.globals.get(name)
                self.push(obj)

            elif op == Opcode.JMP:
                high, low = instructions[ip + 1 : ip + 3]
                pos = (high << 8) + low
                current_block.ip = pos - 1

            elif op == Opcode.JIF:
                high, low = instructions[ip + 1 : ip + 3]
                pos = (high << 8) + low
                current_block.ip += 2

                condition = self.pop()
                if is_truthy(condition):
                    current_block.ip = pos - 1

            elif op == Opcode.JIN:
                high, low = instructions[ip + 1 : ip + 3]
                pos = (high << 8) + low
                current_block.ip += 2

                condition = self.pop()
                if not is_truthy(condition):
                    current_block.ip = pos - 1

            elif op == Opcode.JIE:
                high, low = instructions[ip + 1 : ip + 3]
                pos = (high << 8) + low
                current_block.ip += 2

                if self.pop() == Empty:
                    current_block.ip = pos - 1

            elif op == Opcode.NOP:
                self.push(Nop)

            elif op == Opcode.SLO:
                high, low = instructions[ip + 1 : ip + 3]
                idx = (high << 8) + low
                current_block.ip += 2

                self.locals[idx] = self.pop()

            elif op == Opcode.GLO:
                high, low = instructions[ip + 1 : ip + 3]
                idx = (high << 8) + low
                current_block.ip += 2

                self.push(self.locals.get(idx))

            elif op == Opcode.GBL:
                idx = instructions[ip + 1]
                current_block.ip += 1

                self.push(self.stack[current_block.base_pointer + idx])

            elif op == Opcode.GFR:
                idx = instructions[ip + 1]
                current_block.ip += 1

                self.push(current_block.free[idx])

            elif op == Opcode.STE:
                high, low = instructions[ip + 1 : ip + 3]
                idx = (high << 8) + low
                current_block.ip += 2

                it = self.stack[self.sp - 1]
                assert isinstance(it, LoopIter), f"expected LoopIter, found {repr(it)}"

                try:
                    val = it.step(self.current_buffer)
                    self.stack[current_block.base_pointer + idx] = val
                except StopIteration:
                    it.empty_exit_buffer(self.current_buffer)
                    self._stop_iteration()

            elif op == Opcode.FOR:
                num_block_vars = instructions[ip + 1]
                num_free_vars = instructions[current_block.ip + 2]
                current_block.ip += 2

                self._exec_forloop(num_block_vars, num_free_vars)

            elif op == Opcode.STO:
                self._stop_iteration()

            elif op == Opcode.CAPTURE:
                self.push_buffer()

            elif op == Opcode.SETCAPTURE:
                value = self.pop_buffer()

                high, low = instructions[ip + 1 : ip + 3]
                idx = (high << 8) + low
                current_block.ip += 2

                self.locals[idx] = value

            elif op == Opcode.DEC:
                high, low = instructions[ip + 1 : ip + 3]
                idx = (high << 8) + low
                current_block.ip += 2

                self.push(self.context.decrement(idx))

            elif op == Opcode.INC:
                high, low = instructions[ip + 1 : ip + 3]
                idx = (high << 8) + low
                current_block.ip += 2

                self.push(self.context.increment(idx))

            elif op == Opcode.CYC:
                num_args = instructions[ip + 1]
                current_block.ip += 1

                group = self.pop()
                args = [self.pop() for _ in range(num_args)]

                self.push(next(self.context.cycle(group, args)))

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

            elif op == Opcode.TAB:
                num_block_vars = instructions[ip + 1]
                num_free_vars = instructions[ip + 2]
                current_block.ip += 2

                self._exec_tablerow(num_block_vars, num_free_vars)

            elif op == Opcode.BRK:
                block = self.pop_block()
                self.sp = block.base_pointer - 1

                # Keep popping blocks off the stack until we find a for loop.
                # For loops are the only blocks that respond to a break.
                while not block.forloop:
                    block = self.pop_block()
                    self.sp = block.base_pointer - 1

                val = self.pop_buffer()
                if not val.isspace():
                    self.current_buffer.write(val)

            elif op == Opcode.CON:
                # Keep popping blocks off the stack until we find a for loop.
                # For loops are the only blocks that respond to a continue.
                while not self.current_block.forloop:
                    block = self.pop_block()
                    self.sp = block.base_pointer - 1

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

            elif op == Opcode.EBL:
                num_args = instructions[ip + 1]
                num_free = instructions[ip + 2]
                current_block.ip += 1

                block_name = self.pop()
                args = [self.pop() for _ in range(num_args)]

                free_vars = [self.pop() for _ in range(num_free)]

                compiled_block = self.stack[self.sp - 1]
                assert isinstance(
                    compiled_block, CompiledBlock
                ), f"expected CompiledBlock, found {type(compiled_block)}"

                # self.push_buffer()

                block = Block(
                    block=compiled_block,
                    base_pointer=self.sp,
                    free=free_vars,
                )
                self.push_block(block)
                self.sp = block.base_pointer + compiled_block.num_locals

                exec_func = lookup_exec[block_name]
                exec_func(self, *args)

            elif op == Opcode.LBL:
                self.pop_block()

    def _exec_forloop(self, num_block_vars, num_free_vars):
        assert num_block_vars == 2

        # Need to know the length of the sequence
        items = list(self._make_iter())
        it = iter(items)

        free_vars = [self.pop() for _ in range(num_free_vars)]

        compiled_block = self.stack[self.sp - 1]
        assert isinstance(compiled_block, CompiledBlock)

        self.push_buffer()

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

            offset = self.current_block.base_pointer

            self.stack[offset] = val
            self.stack[offset + 1] = drop.forloop

            self.push(for_it)
            self.push(Nop)

    def _exec_tablerow(self, num_block_vars, num_free_vars):
        assert num_block_vars == 2
        items = list(self._make_iter())

        cols = self.pop()
        if not cols:
            cols = len(items)

        free_vars = [self.pop() for _ in range(num_free_vars)]

        compiled_block = self.stack[self.sp - 1]
        assert isinstance(compiled_block, CompiledBlock)

        self.push_buffer()

        block = Block(
            block=compiled_block,
            base_pointer=self.sp,
            free=free_vars,
            forloop=False,
        )
        self.push_block(block)
        self.sp = block.base_pointer + compiled_block.num_locals

        drop = TableRowDrop("", len(items), cols)
        for_it = LoopIter(iter(items), drop)

        # Initialise drop with first step
        val = for_it.step(self.current_buffer)

        offset = self.current_block.base_pointer

        self.stack[offset] = val
        self.stack[offset + 1] = drop.tablerow

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

        val = self.pop_buffer()
        if not val.isspace():
            self.current_buffer.write(val)

    def push(self, obj: Any):
        """Push the given object on to the top of the stack."""
        assert self.sp < STACK_SIZE
        self.stack[self.sp] = obj
        self.sp += 1

    def pop(self) -> Any:
        """Pop an object off the top of the stack."""
        obj = self.stack[self.sp - 1]
        self.sp -= 1
        return obj

    def push_block(self, block: Block):
        self.blocks.append(block)
        self.current_block = block

    def pop_block(self) -> Block:
        old_block = self.blocks.pop()
        self.current_block = self.blocks[-1]
        return old_block

    def push_buffer(self):
        """Start a new ouput buffer."""
        buf = StringIO()
        self.buffers.append(buf)
        self.current_buffer = buf

    def pop_buffer(self) -> str:
        """Pop the current buffer of the buffer stack and return it."""
        buf = self.buffers.pop()
        self.current_buffer = self.buffers[-1]
        return buf.getvalue()

    def pprint_stack(self):
        buf = []
        for itm in self.stack[: self.sp]:
            if isinstance(itm, dict):
                buf.append(f"Hash({list(itm.keys())})")
            else:
                buf.append(itm)
        return ", ".join([repr(itm) for itm in buf])


def to_string(val: Any) -> str:
    # Short cut condition. Strings are far more common than any other type.
    if isinstance(val, str):
        res = val
    elif isinstance(val, (list, tuple)):
        res = "".join(str(v) for v in val)
    elif isinstance(val, bool):
        res = str(val).lower()
    elif val is None:
        res = ""
    else:
        res = str(val)

    return res


# TODO: Move me
def _exec_paginate(vm: VM, page_size: int, collection: abc.Collection):
    collection_size = len(collection)
    page_count = math.ceil(collection_size / page_size)
    current_page = vm.globals.get("current_page", default=1)

    pagination = {
        "page_size": page_size,
        "current_page": current_page,
        "current_offset": current_page * page_size,
        "items": collection_size,
        "pages": page_count,
        "parts": [],
        "previous": None,
        "next": None,
    }

    if current_page > 1:
        pagination["previous"] = link("&laquo; Previous", current_page - 1)

    if current_page < page_count:
        pagination["next"] = link("Next &raquo;", current_page + 1)

    if page_count > 1:
        for page in range(1, page_count + 1):
            if current_page == page:
                pagination["parts"].append(no_link(page))
            else:
                pagination["parts"].append(link(page, page))

    vm.stack[vm.current_block.base_pointer] = pagination


# TODO: Move me
def _exec_form(vm: VM, article: Mapping):
    form = {
        "posted_successfully?": vm.context.get("posted_successfully", True),
        "errors": vm.context.get(["comment", "errors"], []),
        "author": vm.context.get(["comment", "author"]),
        "email": vm.context.get(["comment", "email"]),
        "body": vm.context.get(["comment", "body"]),
    }

    vm.stack[vm.current_block.base_pointer] = form

    vm.current_buffer.write(
        f'<form id="article-{article["id"]}-comment-form" '
        'class="comment-form" method="post" action="">\n'
    )

    # TODO: close form. Write "\n</form>"


# TODO: Register me
lookup_exec = {
    "paginate": _exec_paginate,
    "form": _exec_form,
}
