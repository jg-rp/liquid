from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ._context import RenderContext

if TYPE_CHECKING:
    from .environment import LiquidEnvironment


class Template:
    def __init__(self, env: LiquidEnvironment, source: str, name: str) -> None:
        self.env = env
        self.source = source
        self.name = name

    def render_with_context(self, context: RenderContext, buffer: TextIO) -> None:
        # TODO:
        raise NotImplementedError

    async def render_with_context_async(
        self, context: RenderContext, buffer: TextIO
    ) -> None:
        # TODO:
        raise NotImplementedError
