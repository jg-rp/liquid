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


class StopIterObj:
    """Stop Iteration"""

    __slots__ = ()

    def __repr__(self):
        return "StopIter()"

    def __str__(self):
        return ""


StopIter = StopIterObj()


class NoOp:
    """No Operation"""

    __slots__ = ()

    def __repr__(self):
        return "NoOp()"

    def __str__(self):
        return ""


Nop = NoOp()


class CompiledBlock(NamedTuple):
    instructions: code.Instructions
    num_locals: int = 0
    num_parameters: int = 0
    loop: bool = False
