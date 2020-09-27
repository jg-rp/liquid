from typing import NamedTuple

from liquid import code


class EmptyObj:
    """Empty"""

    __slots__ = ()

    def __repr__(self):
        return "Empty()"

    def __str__(self):
        return ""


Empty = EmptyObj()


class NoOp:
    """No Operation"""

    __slots__ = ()

    def __repr__(self):
        return "NoOp()"

    def __str__(self):
        return ""


Nop = NoOp()


class CompiledBlock(NamedTuple):
    """A block of instructions."""

    instructions: code.Instructions
    num_locals: int = 0
    num_arguments: int = 0
    num_free: int = 0

    def __repr__(self):
        return "CompiledBlock(..)"
