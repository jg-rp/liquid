from dataclasses import dataclass, field
from typing import List, Any

from liquid import code
from liquid.object import CompiledBlock


@dataclass
class Block:
    block: CompiledBlock
    base_pointer: int
    ip: int = field(default=-1)
    free: List[Any] = field(default_factory=list)
    forloop: bool = False

    @property
    def instructions(self) -> code.Instructions:
        return self.block.instructions
