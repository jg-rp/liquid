"""Opcode definitions and helpers."""

from enum import IntEnum, auto
from itertools import chain
from typing import List, NamedTuple, Dict, Tuple

from liquid.exceptions import OpcodeError

# We're going to work with bytes in their decimal representation. We'll just
# have to write extra tests to ensure each byte is within bounds.
Instruction = List[int]


class Opcode(IntEnum):
    """Operation codes."""

    CONSTANT = 1

    POP = auto()

    TRUE = auto()
    FALSE = auto()
    NIL = auto()
    EMPTY = auto()

    EQ = auto()
    NE = auto()
    GT = auto()
    GE = auto()
    CONTAINS = auto()

    AND = auto()
    OR = auto()

    MINUS = auto()

    JUMPIFNOT = auto()
    JUMP = auto()
    NOP = auto()

    GETGLOBAL = auto()
    GETLOCAL = auto()
    SETLOCAL = auto()

    CALLFILTER = auto()
    GETFILTER = auto()


assert len(Opcode) <= 255


class Instructions(list):
    """A list on instructions that can pretty print themselves."""

    def __init__(self, *ins: Instruction) -> None:
        super().__init__(chain(*ins))

    def __str__(self):
        return _string(self)


class Definition(NamedTuple):
    """Opcode definition."""

    name: str
    operand_widths: Tuple[int, ...]


definitions: Dict[Opcode, Definition] = {
    Opcode.CONSTANT: Definition("OpConstant", (2,)),
    Opcode.POP: Definition("OpPop", ()),
    Opcode.POP: Definition("OpPop", ()),
    Opcode.TRUE: Definition("OpTrue", ()),
    Opcode.FALSE: Definition("OpFalse", ()),
    Opcode.NIL: Definition("OpNil", ()),
    Opcode.EMPTY: Definition("OpEmpty", ()),
    Opcode.EQ: Definition("OpEqual", ()),
    Opcode.NE: Definition("OpNotEqual", ()),
    Opcode.GT: Definition("OpGreaterThan", ()),
    Opcode.GE: Definition("OpGreaterThanEqual", ()),
    Opcode.CONTAINS: Definition("OpContains", ()),
    Opcode.AND: Definition("OpAnd", ()),
    Opcode.OR: Definition("OpOr", ()),
    Opcode.MINUS: Definition("OpMinus", ()),
    Opcode.JUMPIFNOT: Definition("OpJumpNotTruthy", (2,)),
    Opcode.JUMP: Definition("OpJump", (2,)),
    Opcode.NOP: Definition("OpNoop", ()),
    Opcode.GETGLOBAL: Definition("OpGetGlobal", (2,)),
    Opcode.GETLOCAL: Definition("OpGetLocal", (2,)),
    Opcode.SETLOCAL: Definition("OpSetLocal", (2,)),
    Opcode.CALLFILTER: Definition("OpCallFilter", (1,)),
    Opcode.GETFILTER: Definition("OpGetFilter", (2,)),
}


def lookup(op: Opcode) -> Definition:
    """Return the definition of the given opcode."""
    try:
        return definitions[op]
    except KeyError as err:
        raise OpcodeError(f"opcode {op} undefined") from err


def make(op: Opcode, *operands: int) -> Instruction:
    """Pack the given opcode and operands into an instruction."""
    _, widths = lookup(op)
    assert len(widths) == len(operands)

    instruction: List[int] = [op]

    for width, operand in zip(widths, operands):
        instruction.extend(list(operand.to_bytes(width, byteorder="big", signed=False)))

    return instruction


def _string(ins: Instructions) -> str:
    buf = []

    idx = 0
    while idx < len(ins):
        try:
            opdef = lookup(ins[idx])
        except OpcodeError as err:
            buf.append(f"error: {err}")
            continue

        operands, read = read_operands(opdef, ins[idx + 1 :])
        buf.append(f"{idx:04d} {_format_instruction(opdef, operands)}")

        idx += read + 1
    return "\n".join(buf)


def read_operands(opdef: Definition, ins: Instructions) -> Tuple[List[int], int]:
    operands = []
    idx = 0

    for width in opdef.operand_widths:
        if width == 1:
            operands.append(read_uint8(ins[idx : idx + width]))
        elif width == 2:
            operands.append(read_uint16(ins[idx : idx + width]))

        idx += width

    return operands, idx


def _format_instruction(opdef: Definition, operands: List[int]) -> str:
    operand_count = len(opdef.operand_widths)

    if len(operands) != operand_count:
        return f"error: expected {operand_count} operands, found {len(operands)}"

    if not operand_count:
        return opdef.name

    return f"{opdef.name} {' '.join(str(oper) for oper in operands)}"


def read_uint8(ins: Instructions) -> int:
    return int.from_bytes(ins[:1], byteorder="big", signed=False)


def read_uint16(ins: Instructions) -> int:
    return int.from_bytes(ins[:2], byteorder="big", signed=False)
