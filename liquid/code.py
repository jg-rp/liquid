"""Opcode definitions and helpers."""

from __future__ import annotations
from enum import IntEnum, auto
import itertools
from typing import List, NamedTuple, Dict, Tuple, MutableSequence

from liquid.exceptions import OpcodeError


class Opcode(IntEnum):
    """Operation codes."""

    CONSTANT = 1

    POP = auto()

    TRU = auto()  # True
    FAL = auto()  # False
    NIL = auto()  # Nil
    EMP = auto()  # Empty

    EQ = auto()  # Equals
    NE = auto()  # Not Equal
    GT = auto()  # Greater Than
    GE = auto()  # Greater than or equal to
    CONTAINS = auto()

    AND = auto()  # Logical and
    OR = auto()  # Logical or

    NEG = auto()  # Negative

    JIF = auto()  # Jump IF truthy
    JIN = auto()  # Jump If Not truthy
    JIE = auto()  # Jump If Empty
    JMP = auto()  # Jump

    NOP = auto()  # No Operation

    GLO = auto()  # Get LOcal (assigned and captured variables)
    SLO = auto()  # Set LOcal (assign and capture)
    RES = auto()  # RESolve names from context
    GIT = auto()  # Get ITem (sequence index or mapping key)
    GIS = auto()  # Get ItemS
    GBL = auto()  # Get BLock scope
    GFR = auto()  # Get FRee

    CAPTURE = auto()
    SETCAPTURE = auto()

    INC = auto()  # Increment
    DEC = auto()  # Decrement
    CYC = auto()  # Cycle

    EBL = auto()  # Enter BLock
    LBL = auto()  # Leave Block

    FOR = auto()  # For each loop
    TAB = auto()  # TABle row loop
    STE = auto()  # Step iterator
    BRK = auto()  # Break
    CON = auto()  # Continue
    STO = auto()  # Stop Iteration

    FIL = auto()  # Call FILter

    def __str__(self):
        return definitions[self].name


assert len(Opcode) <= 255


INFIX_OPERATORS = {
    Opcode.EQ: "==",
    Opcode.NE: "!=",
    Opcode.GT: ">",
    Opcode.GE: ">=",
    Opcode.CONTAINS: "contains",
    Opcode.AND: "and",
    Opcode.OR: "or",
}

# We're going to work with bytes in their decimal representation. We'll just
# have to write extra tests to ensure each byte is within bounds.
# Instruction = ArrayType
Instruction = MutableSequence[int]
Instructions = MutableSequence[int]


class Definition(NamedTuple):
    """Opcode definition."""

    name: str
    operand_widths: Tuple[int, ...]


definitions: Dict[int, Definition] = {
    Opcode.CONSTANT: Definition("OpConstant", (2,)),
    Opcode.POP: Definition("OpPop", ()),
    Opcode.POP: Definition("OpPop", ()),
    Opcode.TRU: Definition("OpTrue", ()),
    Opcode.FAL: Definition("OpFalse", ()),
    Opcode.NIL: Definition("OpNil", ()),
    Opcode.EMP: Definition("OpEmpty", ()),
    Opcode.EQ: Definition("OpEqual", ()),
    Opcode.NE: Definition("OpNotEqual", ()),
    Opcode.GT: Definition("OpGreaterThan", ()),
    Opcode.GE: Definition("OpGreaterThanEqual", ()),
    Opcode.CONTAINS: Definition("OpContains", ()),
    Opcode.AND: Definition("OpAnd", ()),
    Opcode.OR: Definition("OpOr", ()),
    Opcode.NEG: Definition("OpMinus", ()),
    Opcode.JIF: Definition("OpJumpIf", (2,)),  # instruction to jump to
    Opcode.JIN: Definition("OpJumpIfNot", (2,)),  # instruction to jump to
    Opcode.JIE: Definition(
        "OpJumpIfEmpty", (2,)
    ),  # jump to 1 if Empty is on the top of the stack
    Opcode.JMP: Definition("OpJump", (2,)),  # instruction to jump to
    Opcode.NOP: Definition("OpNoOp", ()),
    Opcode.GLO: Definition("OpGetLocal", (2,)),
    Opcode.SLO: Definition("OpSetLocal", (2,)),
    Opcode.RES: Definition("OpResolve", ()),
    Opcode.GIT: Definition("OpGetItem", ()),
    Opcode.GIS: Definition("OpGetItems", (1,)),
    Opcode.GBL: Definition("OpGetBlockVar", (1,)),
    Opcode.GFR: Definition("OpGetFreeVar", (1,)),
    Opcode.CAPTURE: Definition("OpCapture", ()),
    Opcode.SETCAPTURE: Definition("OpSetCapture", (2,)),
    Opcode.INC: Definition("OpIncrement", (1,)),
    Opcode.DEC: Definition("OpDecrement", (1,)),
    Opcode.CYC: Definition("OpCycle", (1,)),  # Number of expressions to cycle
    Opcode.EBL: Definition("OpEnterBlock", (1, 1)),
    Opcode.LBL: Definition("OpLeaveBlock", ()),
    Opcode.FOR: Definition(
        "OpFor", (1, 1)
    ),  # Number of block vars, number of free vars
    Opcode.TAB: Definition("OpTablerow", (1, 1)),
    Opcode.STE: Definition("OpStep", (2,)),
    Opcode.CON: Definition("OpContinue", ()),
    Opcode.BRK: Definition("OpBreak", ()),
    Opcode.STO: Definition("OpStopIteration", ()),
    Opcode.FIL: Definition("OpCallFilter", (2, 1)),  # filter id, num args
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
    assert len(widths) == len(operands), f"opcode: {Opcode(op)!r}"

    instruction: Instruction = [op]

    for width, operand in zip(widths, operands):
        instruction.extend(operand.to_bytes(width, byteorder="big", signed=False))

    return instruction


def chain(*instructions: Instruction) -> Instructions:
    return list(itertools.chain(*instructions))


def string(ins: Instructions) -> str:
    buf = []

    idx = 0
    while idx < len(ins):
        try:
            opdef = lookup(Opcode(ins[idx]))
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
            operands.append(read_uint8(ins[idx]))
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


def read_uint8(op: int) -> int:
    return op
    # return int.from_bytes(op, byteorder="big", signed=False)


def read_uint16(ops: Instruction) -> int:
    assert len(ops) == 2
    return int.from_bytes(ops, byteorder="big", signed=False)
