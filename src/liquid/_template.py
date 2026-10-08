from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .environment import LiquidEnvironment


class Template:
    def __init__(self, env: LiquidEnvironment, source: str, name: str) -> None:
        self.env = env
        self.source = source
        self.name = name
