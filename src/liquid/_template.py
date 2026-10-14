from __future__ import annotations

import re
from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING

from ._chain_map import ReadOnlyChainMap
from ._context import RenderContext
from ._io import StringBuffer
from ._markup import render_block, render_block_async
from .exceptions import LiquidError

if TYPE_CHECKING:
    from ._markup import Block
    from .environment import Environment


class Template:
    def __init__(
        self,
        env: Environment,
        source: str,
        name: str,
        nodes: Block,
        globals: Mapping[str, object] | None,
        matter: Mapping[str, object] | None,
        up_to_date: Callable[[], bool | Awaitable[bool]] | None = None,
    ) -> None:
        self.env = env
        self.source = source
        self.name = name
        self.nodes = nodes
        self.globals = globals
        self.matter = matter
        self.up_to_date = up_to_date

        self._lines: list[str] | None = None

    @property
    def lines(self) -> list[str]:
        if self._lines is None:
            lines = re.split(r"(?<=\n)", self.source)
            if lines[-1] == "":
                lines.pop()
            self._lines = lines

        return self._lines

    def render(self, data: Mapping[str, object] | None = None) -> str:
        buffer = StringBuffer()
        context = RenderContext(self, globals=self.make_globals(data))
        self.render_with_context(context, buffer)
        return buffer.getvalue()

    async def render_async(self, data: Mapping[str, object] | None = None) -> str:
        buffer = StringBuffer()
        context = RenderContext(self, globals=self.make_globals(data))
        await self.render_with_context_async(context, buffer)
        return buffer.getvalue()

    def render_with_context(self, context: RenderContext, buffer: StringBuffer) -> None:
        render_block(self.nodes, context, buffer)

    async def render_with_context_async(
        self, context: RenderContext, buffer: StringBuffer
    ) -> None:
        await render_block_async(self.nodes, context, buffer)

    def make_globals(
        self, data: Mapping[str, object] | None
    ) -> Mapping[str, object] | None:
        if not (data or self.matter or self.globals):
            return None

        chain = ReadOnlyChainMap()

        if self.globals:
            chain.push(self.globals)

        if self.matter:
            chain.push(self.matter)

        if data:
            chain.push(data)

        return chain

    def is_up_to_date(self) -> bool:
        """Return ``False`` if the template has bee modified, ``True`` otherwise."""
        if not self.up_to_date:
            return True

        uptodate = self.up_to_date()
        if not isinstance(uptodate, bool):
            raise LiquidError(
                f"expected a boolean from uptodate, found {type(uptodate).__name__}",
            )
        return uptodate

    async def is_up_to_date_async(self) -> bool:
        """An async version of `is_up_to_date`.

        If `template.up_to_date` is a coroutine, it wil be awaited. Otherwise it will be
        called just like `is_up_to_date`
        """
        if not self.up_to_date:
            return True

        uptodate = self.up_to_date()
        if isinstance(uptodate, Awaitable):
            return await uptodate
        return uptodate

    # TODO: static analysis methods
