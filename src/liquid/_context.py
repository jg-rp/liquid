from __future__ import annotations

from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeGuard, cast

from ._chain_map import ReadOnlyChainMap
from ._nothing import NOTHING

if TYPE_CHECKING:
    from ._template import Template
    from .drops import ForLoop, TableRowLoop


class RenderContext:
    def __init__(
        self,
        template: Template,
        *,
        globals: Mapping[str, object] | None = None,
        disabled_tags: Sequence[str] | None = None,
        context_depth: int = 0,
        assign_score_carry: int = 0,
        render_score_carry: int = 0,
    ) -> None:
        self.template = template
        self.env = template.env

        self.globals = globals or {}
        self.locals: dict[str, object] = {}

        self.counters: dict[str, int] = {}
        self.registers: dict[str, object] = {}

        self.scope = ReadOnlyChainMap(self.locals, self.counters, self.globals)

        self.loops: list[ForLoop | TableRowLoop] = []
        self.interrupts: list[str] = []

        self.disabled_tags = disabled_tags

        self.context_depth = context_depth
        self.assign_score = 0
        self.render_score = 0
        self.assign_score_cumulative = assign_score_carry
        self.render_score_cumulative = render_score_carry

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

    def copy(
        self,
        namespace: Mapping[str, object],
        *,
        template: Template | None = None,
        disabled_tags: Sequence[str] | None = None,
        block_scope: bool = False,
    ) -> RenderContext:
        # TODO: raise for context depth
        globals_ = (
            ReadOnlyChainMap(namespace, self.scope)
            if block_scope
            else ReadOnlyChainMap(namespace, self.globals)
        )

        ctx = RenderContext(
            template or self.template,
            globals=globals_,
            disabled_tags=disabled_tags,
            context_depth=self.context_depth + 1,
            assign_score_carry=self.assign_score_cumulative,
            render_score_carry=self.render_score_cumulative,
        )

        for register in self.env.persistent_registers:
            if register in self.registers:
                ctx.registers[register] = self.registers[register]

        return ctx

    @contextmanager
    def extend(
        self, namespace: Mapping[str, object], template: Template | None = None
    ) -> Generator[RenderContext]:
        # TODO:
        yield self
        raise NotImplementedError

    @contextmanager
    def loop(
        self, namespace: Mapping[str, object], loop: ForLoop | TableRowLoop
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
            if is_forloop(loop):
                return loop
        return None


def is_forloop(loop: ForLoop | TableRowLoop) -> TypeGuard[ForLoop]:
    return hasattr(loop, "parent_loop")
