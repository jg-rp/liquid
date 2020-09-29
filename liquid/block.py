from typing import List, Any

from liquid.object import CompiledBlock


class Block:

    __slots__ = (
        "block",
        "base_pointer",
        "ip",
        "free",
        "forloop",
        "instructions",
        "instruction_count",
    )

    def __init__(
        self,
        block: CompiledBlock,
        base_pointer: int,
        ip: int = -1,
        free: List[Any] = None,
        forloop: bool = False,
    ):

        self.block = block
        self.base_pointer = base_pointer
        self.ip = ip
        self.free = free or []
        self.forloop = forloop

        self.instructions = self.block.instructions
        self.instruction_count = len(self.instructions)

    def __repr__(self):
        return f"Block(base_pointer={self.base_pointer}, ip={self.ip}, forloop={self.forloop})"
