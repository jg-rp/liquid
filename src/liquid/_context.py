from __future__ import annotations

from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from typing import TYPE_CHECKING, cast

from ._nothing import NOTHING

if TYPE_CHECKING:
    from ._template import Template
    from .drops import ForLoop


class RenderContext:
    def __init__(self, template: Template) -> None:
        self.template = template
        self.env = template.env

        self.counters: dict[str, int] = {}
        self.registers: dict[str, object] = {}

        self.loops: list[ForLoop] = []
        self.interrupts: list[str] = []

    def assign(self, name: str, value: object) -> None:
        # TODO
        raise NotImplementedError

    def resolve(self, selector: object) -> object:
        if not isinstance(selector, str):
            return NOTHING

        # TODO
        raise NotImplementedError

    def resolve_path(self, root: object, selectors: list[object]) -> tuple[object, int]:
        # TODO
        raise NotImplementedError

    async def resolve_path_async(
        self, root: object, selectors: list[object]
    ) -> tuple[object, int]:
        # TODO
        raise NotImplementedError

    def get_register[T](self, key: str, default: Callable[[], T]) -> T:
        if key not in self.registers:
            self.registers[key] = default()

        return cast(T, self.registers[key])

    def decrement(self, name: str) -> int:
        i = self.counters.get(name, 0)
        i -= 1
        self.counters[name] = i
        return i

    def increment(self, name: str) -> int:
        i = self.counters.get(name, 0)
        self.counters[name] = i + 1
        return i

    @contextmanager
    def extend(
        self, namespace: Mapping[str, object], template: Template | None = None
    ) -> Generator[RenderContext]:
        # TODO:
        yield self
        raise NotImplementedError

    @contextmanager
    def loop(
        self, namespace: Mapping[str, object], loop: ForLoop
    ) -> Generator[RenderContext]:
        # TODO: raise for loop limit
        self.loops.append(loop)
        with self.extend(namespace) as context:
            try:
                yield context
            finally:
                self.loops.pop()

    def parent_loop(self) -> ForLoop | None:
        for loop in reversed(self.loops):
            if hasattr(loop, "parent_loop"):
                return loop
        return None
