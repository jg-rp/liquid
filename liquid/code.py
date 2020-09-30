"""Opcode definitions and helpers."""

from __future__ import annotations
from enum import IntEnum, auto
from typing import NamedTuple, Dict, MutableSequence

from liquid.exceptions import OpcodeError


class Instruction(NamedTuple):
    opcode: Opcode
    operands: MutableSequence[int]
    num_operands: int

    def string(self, index: int):
        try:
            opdef = lookup(self.opcode)
            if self.operands:
                operands = " ".join(str(op) for op in self.operands)
                return f"{index:04d} {opdef.name} {operands}"
            return f"{index:04d} {opdef.name}"
        except OpcodeError as err:
            return f"error: {err}"


Instructions = MutableSequence[Instruction]


class Opcode(IntEnum):
    """Operation codes."""

    CONSTANT = 1

    STJ = auto()  # STore Jump register
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


class Definition(NamedTuple):
    """Opcode definition."""

    name: str
    num_operand: int


definitions: Dict[int, Definition] = {
    Opcode.CONSTANT: Definition("OpConstant", 1),
    Opcode.POP: Definition("OpPop", 0),
    Opcode.STJ: Definition("OpStoreJump", 0),
    Opcode.TRU: Definition("OpTrue", 0),
    Opcode.FAL: Definition("OpFalse", 0),
    Opcode.NIL: Definition("OpNil", 0),
    Opcode.EMP: Definition("OpEmpty", 0),
    Opcode.EQ: Definition("OpEqual", 0),
    Opcode.NE: Definition("OpNotEqual", 0),
    Opcode.GT: Definition("OpGreaterThan", 0),
    Opcode.GE: Definition("OpGreaterThanEqual", 0),
    Opcode.CONTAINS: Definition("OpContains", 0),
    Opcode.AND: Definition("OpAnd", 0),
    Opcode.OR: Definition("OpOr", 0),
    Opcode.NEG: Definition("OpMinus", 0),
    Opcode.JIF: Definition("OpJumpIf", 1),  # instruction to jump to
    Opcode.JIN: Definition("OpJumpIfNot", 1),  # instruction to jump to
    Opcode.JIE: Definition(
        "OpJumpIfEmpty", 1
    ),  # jump to 1 if Empty is on the top of the stack
    Opcode.JMP: Definition("OpJump", 1),  # instruction to jump to
    Opcode.NOP: Definition("OpNoOp", 0),
    Opcode.GLO: Definition("OpGetLocal", 1),
    Opcode.SLO: Definition("OpSetLocal", 1),
    Opcode.RES: Definition("OpResolve", 0),
    Opcode.GIT: Definition("OpGetItem", 0),
    Opcode.GIS: Definition("OpGetItems", 1),
    Opcode.GBL: Definition("OpGetBlockVar", 1),
    Opcode.GFR: Definition("OpGetFreeVar", 1),
    Opcode.CAPTURE: Definition("OpCapture", 0),
    Opcode.SETCAPTURE: Definition("OpSetCapture", 1),
    Opcode.INC: Definition("OpIncrement", 1),
    Opcode.DEC: Definition("OpDecrement", 1),
    Opcode.CYC: Definition("OpCycle", 1),  # Number of expressions to cycle
    Opcode.EBL: Definition("OpEnterBlock", 2),
    Opcode.LBL: Definition("OpLeaveBlock", 0),
    Opcode.FOR: Definition("OpFor", 2),  # Number of block vars, number of free vars
    Opcode.TAB: Definition("OpTablerow", 2),
    Opcode.STE: Definition("OpStep", 1),
    Opcode.CON: Definition("OpContinue", 0),
    Opcode.BRK: Definition("OpBreak", 0),
    Opcode.STO: Definition("OpStopIteration", 0),
    Opcode.FIL: Definition("OpCallFilter", 2),  # filter id, num args
}


def lookup(op: Opcode) -> Definition:
    """Return the definition of the given opcode."""
    try:
        return definitions[op]
    except KeyError as err:
        raise OpcodeError(f"opcode {op} undefined") from err


def make(op: Opcode, *operands: int) -> Instruction:
    """Pack the given opcode and operands into an instruction."""
    _, num_operands = lookup(op)
    assert num_operands == len(operands), f"opcode: {Opcode(op)!r}"
    return Instruction(op, list(operands), len(operands))


def string(instructions: Instructions) -> str:
    """Return a pretty string representation of a list of instructions."""
    strings = [ins.string(i) for i, ins in enumerate(instructions)]
    return "\n".join(strings)
