from dataclasses import dataclass, field

from liquid import code
from liquid.object import CompiledBlock


@dataclass
class Frame:
    block: CompiledBlock
    base_pointer: int
    ip: int = field(default=-1)

    @property
    def instructions(self) -> code.Instructions:
        return self.block.instructions
