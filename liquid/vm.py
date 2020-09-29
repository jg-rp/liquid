import math
from collections import abc
from functools import partial, reduce
from io import StringIO
from itertools import islice
from typing import Any, Iterator, List, Mapping, Dict, Callable, Union

from liquid.context import Context, ReadOnlyChainMap, _getitem
from liquid import code
from liquid.code import Opcode
from liquid import compiler
from liquid.exceptions import LiquidTypeError
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
        # This is a stack machine.
        self.stack: List[Any] = [None] * STACK_SIZE
        # Stack pointer
        self.sp = 0

        self.constants = bytecode.constants

        # Block scopes
        self.current_block = Block(CompiledBlock(instructions=bytecode.instructions), 0)
        self.blocks: List[Block] = [self.current_block]

        # Stack of file-like objects for rendering to. The only built-in tag
        # that uses anything other than the main buffer is the `capture` tag.
        self.current_buffer = StringIO()
        self.buffers = [self.current_buffer]

        # "assign" and "capture" scope
        self.locals = {}
        # "increment", "decrement" and "cycle" scope
        self.context = context or Context(filters=env.filters)
        # Environment and/or template global scope
        self.globals = ReadOnlyChainMap(self.context.globals, self.context._builtin)

    def last_popped_stack_elem(self) -> Any:
        """Helper method used for testing only."""
        return self.stack[self.sp]

    # pylint: disable=too-many-branches too-many-statements
    def run(self):
        """Execute instructions"""

        while self.current_block.ip < self.current_block.instruction_count - 1:
            self.current_block.ip += 1
            op = self.current_block.instructions[self.current_block.ip]

            # TODO: setup logging
            # print(
            #     f"{self.current_block.ip:04d}: stack: {self.pprint_stack()} {str(Opcode(op))} {self.context.locals}"
            # )

            opcodes[op](self)

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

    def read_uint16(self):
        high, low = self.current_block.instructions[
            self.current_block.ip + 1 : self.current_block.ip + 3
        ]
        self.current_block.ip += 2
        return (high << 8) + low

    def read_uint8(self):
        op = self.current_block.instructions[self.current_block.ip + 1]
        self.current_block.ip += 1
        return op


def _exec_constant(vm):
    const_idx = vm.read_uint16()
    vm.push(vm.constants[const_idx])


def _exec_pop(vm):
    vm.current_buffer.write(to_string(vm.pop()))


def _exec_push(vm, val):
    vm.push(val)


def _exec_filter(vm):
    fltr_id = vm.read_uint16()
    num_args = vm.read_uint8()

    args = [vm.pop() for _ in range(num_args)]
    val = vm.pop()

    func = vm.context.filter(fltr_id)
    res = func(val, *args)

    vm.push(res)


def _exec_getitem(vm):
    item = vm.pop()
    obj = vm.pop()
    try:
        vm.push(_getitem(obj, item))
    except (KeyError, IndexError, TypeError):
        vm.push(None)


def _exec_getitems(vm: VM):
    num_items = vm.read_uint8()
    items = [vm.pop() for _ in range(num_items)]

    obj = vm.pop()

    try:
        vm.push(nested_get(obj, items))
    except (KeyError, IndexError, TypeError):
        vm.push(None)


def _exec_resolve(vm):
    name = vm.pop()
    obj = vm.globals.get(name)
    vm.push(obj)


def _exec_jump(vm):
    pos = vm.read_uint16()
    vm.current_block.ip = pos - 1


def _exec_jump_if(vm):
    pos = vm.read_uint16()

    condition = vm.pop()
    if is_truthy(condition):
        vm.current_block.ip = pos - 1


def _exec_jump_if_not(vm):
    pos = vm.read_uint16()

    condition = vm.pop()
    if not is_truthy(condition):
        vm.current_block.ip = pos - 1


def _exec_jump_if_empty(vm):
    pos = vm.read_uint16()

    if vm.pop() == Empty:
        vm.current_block.ip = pos - 1


def _exec_nop(vm):
    vm.push(Nop)


def _exec_set_local(vm):
    idx = vm.read_uint16()
    vm.locals[idx] = vm.pop()


def _exec_get_local(vm):
    idx = vm.read_uint16()
    vm.push(vm.locals.get(idx))


def _exec_get_block_var(vm):
    idx = vm.read_uint8()
    vm.push(vm.stack[vm.current_block.base_pointer + idx])


def _exec_get_free(vm):
    idx = vm.read_uint8()
    vm.push(vm.current_block.free[idx])


def _exec_step(vm):
    idx = vm.read_uint16()
    it = vm.stack[vm.sp - 1]
    assert isinstance(it, LoopIter), f"expected LoopIter, found {repr(it)}"

    try:
        val = it.step(vm.current_buffer)
        vm.stack[vm.current_block.base_pointer + idx] = val
    except StopIteration:
        it.empty_exit_buffer(vm.current_buffer)
        _stop_iteration(vm)


def _exec_set_capture(vm):
    idx = vm.read_uint16()
    vm.locals[idx] = vm.pop_buffer()


def _exec_decrement(vm):
    idx = vm.read_uint8()
    vm.push(vm.context.decrement(idx))


def _exec_increment(vm):
    idx = vm.read_uint8()
    vm.push(vm.context.increment(idx))


def _exec_cycle(vm):
    num_args = vm.read_uint8()
    group = vm.pop()
    args = [vm.pop() for _ in range(num_args)]
    vm.push(next(vm.context.cycle(group, args)))


def _exec_infix(vm, op: Opcode):
    right = vm.pop()
    left = vm.pop()
    operator = code.INFIX_OPERATORS[op]
    vm.push(compare(left, operator, right))


def _exec_negative(vm):
    operand = vm.pop()
    vm.push(-operand)


def _exec_break(vm):
    block = vm.pop_block()
    vm.sp = block.base_pointer - 1

    # Keep popping blocks off the stack until we find a for loop.
    # For loops are the only blocks that respond to a break.
    while not block.forloop:
        block = vm.pop_block()
        vm.sp = block.base_pointer - 1

    val = vm.pop_buffer()
    if not val.isspace():
        vm.current_buffer.write(val)


def _exec_continue(vm):
    # Keep popping blocks off the stack until we find a for loop.
    # For loops are the only blocks that respond to a continue.
    while not vm.current_block.forloop:
        block = vm.pop_block()
        vm.sp = block.base_pointer - 1

    it = vm.stack[vm.sp - 1]
    assert isinstance(it, LoopIter)

    try:
        val = next(it)
        # Loop var is always at index 0 (from base_pointer)
        vm.stack[vm.current_block.base_pointer] = val
        # First block instruction is always at instruction 3
        vm.current_block.ip = 2
    except StopIteration:
        _stop_iteration(vm)


def _exec_enter_block(vm):
    num_args = vm.read_uint8()
    num_free = vm.read_uint8()

    block_name = vm.pop()
    args = [vm.pop() for _ in range(num_args)]

    free_vars = [vm.pop() for _ in range(num_free)]

    compiled_block = vm.stack[vm.sp - 1]
    assert isinstance(
        compiled_block, CompiledBlock
    ), f"expected CompiledBlock, found {type(compiled_block)}"

    block = Block(
        block=compiled_block,
        base_pointer=vm.sp,
        free=free_vars,
    )
    vm.push_block(block)
    vm.sp = block.base_pointer + compiled_block.num_locals

    exec_func = lookup_exec[block_name]
    exec_func(vm, *args)


def _exec_leave_block(vm):
    vm.pop_block()


def _exec_capture(vm):
    vm.push_buffer()


def _exec_forloop(vm):
    num_block_vars = vm.read_uint8()
    num_free_vars = vm.read_uint8()
    assert num_block_vars == 2

    # Need to know the length of the sequence
    items = list(_make_iter(vm))
    it = iter(items)

    free_vars = [vm.pop() for _ in range(num_free_vars)]

    compiled_block = vm.stack[vm.sp - 1]
    assert isinstance(compiled_block, CompiledBlock)

    vm.push_buffer()

    block = Block(
        block=compiled_block,
        base_pointer=vm.sp,
        free=free_vars,
        forloop=True,
    )
    vm.push_block(block)
    vm.sp = block.base_pointer + compiled_block.num_locals

    if not items:
        vm.push(Empty)
    else:
        drop = ForLoopDrop(0, len(items))
        for_it = LoopIter(it, drop)

        # Initialise drop with first step
        val = next(for_it)

        offset = vm.current_block.base_pointer

        vm.stack[offset] = val
        vm.stack[offset + 1] = drop.forloop

        vm.push(for_it)
        vm.push(Nop)


def _exec_tablerow(vm):
    num_block_vars = vm.read_uint8()
    num_free_vars = vm.read_uint8()
    assert num_block_vars == 2
    items = list(_make_iter(vm))

    cols = vm.pop()
    if not cols:
        cols = len(items)

    free_vars = [vm.pop() for _ in range(num_free_vars)]

    compiled_block = vm.stack[vm.sp - 1]
    assert isinstance(compiled_block, CompiledBlock)

    vm.push_buffer()

    block = Block(
        block=compiled_block,
        base_pointer=vm.sp,
        free=free_vars,
        forloop=False,
    )
    vm.push_block(block)
    vm.sp = block.base_pointer + compiled_block.num_locals

    drop = TableRowDrop("", len(items), cols)
    for_it = LoopIter(iter(items), drop)

    # Initialise drop with first step
    val = for_it.step(vm.current_buffer)

    offset = vm.current_block.base_pointer

    vm.stack[offset] = val
    vm.stack[offset + 1] = drop.tablerow

    vm.push(for_it)


def _make_iter(vm) -> Iterator:
    # Range start or collection to iterate
    start = vm.pop()
    # Range stop. Will be None if start is a collection.
    stop = vm.pop()

    if isinstance(start, abc.Sequence):
        it = iter(start)
    elif isinstance(start, abc.Mapping):
        it = start.items()
    elif isinstance(start, int):
        assert isinstance(stop, int)
        it = range(start, stop + 1)
    else:
        raise LiquidTypeError(f"can't iterate object '{start}'")

    limit = vm.pop()
    offset = vm.pop()
    reverse = vm.pop()

    it = islice(it, offset, limit)

    if reverse:
        it = reversed(list(it))

    return it


def _stop_iteration(vm):
    block = vm.pop_block()
    vm.sp = block.base_pointer - 1

    val = vm.pop_buffer()
    if not val.isspace():
        vm.current_buffer.write(val)


opcodes: Dict[int, Callable] = {
    Opcode.CONSTANT: _exec_constant,
    Opcode.POP: _exec_pop,
    Opcode.FIL: _exec_filter,
    Opcode.GIT: _exec_getitem,
    Opcode.GIS: _exec_getitems,
    Opcode.RES: _exec_resolve,
    Opcode.JMP: _exec_jump,
    Opcode.JIF: _exec_jump_if,
    Opcode.JIN: _exec_jump_if_not,
    Opcode.JIE: _exec_jump_if_empty,
    Opcode.NOP: _exec_nop,
    Opcode.SLO: _exec_set_local,
    Opcode.GLO: _exec_get_local,
    Opcode.GBL: _exec_get_block_var,
    Opcode.GFR: _exec_get_free,
    Opcode.STE: _exec_step,
    Opcode.FOR: _exec_forloop,
    Opcode.STO: _stop_iteration,
    Opcode.CAPTURE: _exec_capture,
    Opcode.SETCAPTURE: _exec_set_capture,
    Opcode.DEC: _exec_decrement,
    Opcode.INC: _exec_increment,
    Opcode.CYC: _exec_cycle,
    Opcode.TRU: partial(_exec_push, val=True),
    Opcode.FAL: partial(_exec_push, val=False),
    Opcode.NIL: partial(_exec_push, val=None),
    Opcode.EMP: partial(_exec_push, val=Empty),
    Opcode.EQ: partial(_exec_infix, op=Opcode.EQ),
    Opcode.NE: partial(_exec_infix, op=Opcode.NE),
    Opcode.GT: partial(_exec_infix, op=Opcode.GT),
    Opcode.GE: partial(_exec_infix, op=Opcode.GE),
    Opcode.CONTAINS: partial(_exec_infix, op=Opcode.CONTAINS),
    Opcode.AND: partial(_exec_infix, op=Opcode.AND),
    Opcode.OR: partial(_exec_infix, op=Opcode.OR),
    Opcode.NEG: _exec_negative,
    Opcode.TAB: _exec_tablerow,
    Opcode.BRK: _exec_break,
    Opcode.CON: _exec_continue,
    Opcode.EBL: _exec_enter_block,
    Opcode.LBL: _exec_leave_block,
}


def decode(instructions: code.Instructions) -> List[Callable]:
    decoded = []
    idx = 0
    n = len(instructions)

    while idx < n:
        opcode = instructions[idx]
        idx += 1

        func = opcodes[opcode]
        widths = code.definitions[opcode].operand_widths

        operands = []

        for width in widths:
            if width == 1:
                operands.append(instructions[idx])
                idx += 1
            elif width == 2:
                high, low = instructions[idx : idx + 3]
                operands.append((high << 8) + low)
                idx += 2

        decoded.append(partial(func, *operands))

    return decoded


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


def nested_get(obj, keys: List[Union[str, int]]) -> Any:
    try:
        return reduce(_getitem, keys, obj)
    except (KeyError, IndexError, TypeError):
        return None


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
