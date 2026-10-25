# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false

from __future__ import annotations

import inspect
import math
from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from typing import TYPE_CHECKING, TypeGuard, cast

from ._chain_map import ReadOnlyChainMap
from ._drop import (
    liquid_async_object,
    liquid_awaitable,
    liquid_callable,
    liquid_object,
    liquid_primitive,
)
from ._nothing import NOTHING
from .exceptions import ResourceLimitError
from .expressions import IntegerLiteral, Name

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
        context_depth: int = 1,
        assign_score_carry: int = 0,
        render_score_carry: int = 0,
        loop_iteration_carry: int = 1,
    ) -> None:
        self.template = template
        self.env = template.env
        self.limits = self.env.resource_limits

        self.globals = globals or {}
        self.locals: dict[str, object] = {}
        self.counters: dict[str, int] = {}
        self.scope = ReadOnlyChainMap(self.locals, self.counters, self.globals)

        self.registers: dict[str, object] = {}

        self.loops: list[ForLoop | TableRowLoop] = []
        self.interrupts: list[str] = []
        self.disabled_tags = disabled_tags

        self.context_depth = context_depth
        self.assign_score = 0
        self.render_score = 0
        self.assign_score_cumulative = assign_score_carry
        self.render_score_cumulative = render_score_carry
        self.loop_iteration_carry = loop_iteration_carry

    def assign(self, name: str, value: object) -> None:
        if self.limits.max_assign_score or self.limits.max_assign_score_cumulative:
            score = assign_score_of(value)
            self.assign_score += score
            self.assign_score_cumulative += score

            if (
                self.limits.max_assign_score
                and self.assign_score > self.limits.max_assign_score
            ) or (
                self.limits.max_assign_score_cumulative
                and self.assign_score_cumulative
                > self.limits.max_assign_score_cumulative
            ):
                raise ResourceLimitError("memory limit exceeded")

        self.locals[name] = value

    def resolve(self, name: object) -> object:
        """Lookup `name` in the current scope.

        Returns
        -------
        The special value `NOTHING` is `name` can not be resolved.
        """
        if not isinstance(name, str):
            return NOTHING

        return self.scope[name]

    def resolve_path(self, obj: object, selectors: list[object]) -> tuple[object, int]:
        index: int = -1
        dotted: bool

        for selector in selectors:
            index += 1

            if isinstance(selector, (Name, IntegerLiteral)):
                selector = selector.value
                dotted = True
            else:
                dotted = False

            if liquid_object(obj):
                if liquid_primitive(selector):
                    selector = selector.__liquid__("string", self)

                if isinstance(selector, str) and obj.__liquid_hasattr__(selector, self):
                    val = obj.__liquid_getattr__(selector, self)

                    if callable(val):
                        if liquid_callable(obj) and obj.__liquid_callable__(selector):
                            try:
                                val = val()
                            except Exception:  # noqa: BLE001
                                val = NOTHING

                        else:
                            val = NOTHING

                    obj = val
                else:
                    obj = NOTHING

            elif isinstance(obj, str):
                if self.env.iterable_strings:
                    obj = resolve_sequence_selector(obj, selector, dotted)
                else:
                    obj = resolve_string_selector(obj, selector)

            elif isinstance(obj, Sequence):
                if liquid_primitive(selector):
                    selector = selector.__liquid__("numeric", self)

                obj = resolve_sequence_selector(obj, selector, dotted)

            elif isinstance(obj, Mapping):
                if liquid_primitive(selector):
                    selector = selector.__liquid__("data", self)
                obj = resolve_mapping_selector(obj, selector, dotted)

            else:
                obj = resolve_unknown_selector(obj, selector)

            if obj is NOTHING:
                return (NOTHING, index)

        return (obj, index)

    async def resolve_path_async(
        self, obj: object, selectors: list[object]
    ) -> tuple[object, int]:
        index: int = -1
        dotted: bool

        for selector in selectors:
            index += 1

            if isinstance(selector, (Name, IntegerLiteral)):
                selector = selector.value
                dotted = True
            else:
                dotted = False

            if liquid_async_object(obj):
                if liquid_primitive(selector):
                    selector = selector.__liquid__("string", self)

                if isinstance(selector, str) and await obj.__liquid_hasattr_async__(
                    selector, self
                ):
                    val = await obj.__liquid_getattr_async__(selector, self)

                    if callable(val):
                        if liquid_awaitable(obj) and obj.__liquid_awaitable__(selector):
                            try:
                                val = val()
                                if inspect.isawaitable(val):
                                    val = await val
                            except Exception:  # noqa: BLE001
                                val = NOTHING
                        elif liquid_callable(obj) and obj.__liquid_callable__(selector):
                            try:
                                val = val()
                            except Exception:  # noqa: BLE001
                                val = NOTHING

                        else:
                            val = NOTHING

                    obj = val
                else:
                    obj = NOTHING

            elif liquid_object(obj):
                if liquid_primitive(selector):
                    selector = selector.__liquid__("string", self)

                if isinstance(selector, str) and obj.__liquid_hasattr__(selector, self):
                    val = obj.__liquid_getattr__(selector, self)

                    if callable(val):
                        if liquid_awaitable(obj) and obj.__liquid_awaitable__(selector):
                            try:
                                val = val()
                                if inspect.isawaitable(val):
                                    val = await val
                            except Exception:  # noqa: BLE001
                                val = NOTHING
                        elif liquid_callable(obj) and obj.__liquid_callable__(selector):
                            try:
                                val = val()
                            except Exception:  # noqa: BLE001
                                val = NOTHING

                        else:
                            val = NOTHING

                    obj = val
                else:
                    obj = NOTHING

            elif isinstance(obj, str):
                obj = resolve_string_selector(obj, selector)

            elif isinstance(obj, Sequence):
                if liquid_primitive(selector):
                    selector = selector.__liquid__("numeric", self)
                obj = resolve_sequence_selector(obj, selector, dotted)

            elif isinstance(obj, Mapping):
                if liquid_primitive(selector):
                    selector = selector.__liquid__("data", self)
                obj = resolve_mapping_selector(obj, selector, dotted)

            else:
                obj = resolve_unknown_selector(obj, selector)

            if obj is NOTHING:
                return (NOTHING, index)

        return (obj, index)

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
        carry_loop_iterations: bool = False,
        block_scope: bool = False,
    ) -> RenderContext:
        self.raise_for_context_depth()

        if carry_loop_iterations:
            loop_iteration_carry = (
                math.prod(loop.length for loop in self.loops)
                * self.loop_iteration_carry
            )

        else:
            loop_iteration_carry = 1

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
            loop_iteration_carry=loop_iteration_carry,
        )

        for register in self.env.persistent_registers:
            if register in self.registers:
                ctx.registers[register] = self.registers[register]

        return ctx

    @contextmanager
    def extend(
        self, namespace: Mapping[str, object], template: Template | None = None
    ) -> Generator[RenderContext]:
        self.raise_for_context_depth()

        restore_assign_score = self.assign_score
        restore_render_score = self.render_score
        restore_template = self.template

        if template:
            self.template = template

        self.scope.push(namespace)
        self.context_depth += 1
        self.assign_score = 0
        self.render_score = 0

        try:
            yield self
        finally:
            if template:
                self.template = restore_template
            self.scope.pop()
            self.context_depth -= 1
            self.assign_score = restore_assign_score
            self.render_score = restore_render_score

    @contextmanager
    def loop(
        self, namespace: Mapping[str, object], loop: ForLoop | TableRowLoop
    ) -> Generator[RenderContext]:
        self.raise_for_loop_limit(loop.length)
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

    def raise_for_context_depth(self) -> None:
        if self.context_depth + 1 > self.limits.max_context_depth:
            raise ResourceLimitError(
                "maximum context depth reached, possible recursive render"
            )

    def raise_for_loop_limit(self, length: int) -> None:
        if (
            self.limits.max_loop_iterations
            and math.prod(loop.length for loop in self.loops)
            * (length * self.loop_iteration_carry)
            > self.limits.max_loop_iterations
        ):
            raise ResourceLimitError("loop iteration limit reached")


def is_forloop(loop: ForLoop | TableRowLoop) -> TypeGuard[ForLoop]:
    return hasattr(loop, "parent_loop")


def assign_score_of(obj: object, max_nodes: int = 1_000_000) -> int:
    stack: list[object] = [obj]
    seen: set[int] = set()
    count = 0

    score = 0

    while stack:
        if count > max_nodes:
            raise ResourceLimitError("maximum data depth reached")

        node = stack.pop()
        count += 1

        if isinstance(node, str):
            score += len(node)

        elif isinstance(node, Sequence):
            id_ = id(node)
            if id_ in seen:
                continue

            seen.add(id_)
            score += 1
            stack.extend(node)

        elif isinstance(node, Mapping):
            id_ = id(node)
            if id_ in seen:
                continue

            seen.add(id_)
            score += 1
            stack.extend(node.keys())
            stack.extend(node.values())

        else:
            score += 1

    return score


def resolve_string_selector(obj: str, selector: object) -> object:
    if selector == "size":
        return len(obj)

    if not obj:
        return NOTHING

    if selector == "first":
        return obj[0]

    if selector == "last":
        return obj[-1]

    return NOTHING


def resolve_sequence_selector(
    obj: Sequence[object], selector: object, dotted: bool
) -> object:
    if not obj:
        return 0 if selector == "size" else NOTHING

    if isinstance(selector, int):
        if selector < 0:
            if len(obj) >= abs(selector):
                return obj[selector]
            return NOTHING

        return obj[selector] if len(obj) > selector else NOTHING

    # Only dotted path syntax "calls" "commands", like `.first` and `.size`.
    if not dotted:
        return NOTHING

    if selector == "first":
        return obj[0]

    if selector == "last":
        return obj[-1]

    if selector == "size":
        return len(obj)

    return NOTHING


def resolve_mapping_selector(
    obj: Mapping[object, object], selector: object, dotted: bool
) -> object:
    try:
        if selector in obj:
            return obj[selector]
    except TypeError:
        return NOTHING

    # Only dotted path syntax "calls" "commands", like `.first` and `.size`.
    if not dotted:
        return NOTHING

    if selector == "first":
        return next(iter(obj.items()), NOTHING)

    if selector == "size":
        return len(obj)

    return NOTHING


def resolve_unknown_selector(obj: object, selector: object) -> object:
    if selector == "size":
        if isinstance(obj, bool):
            return 0

        # Close enough, most of the time.
        return 8 if isinstance(obj, int) else NOTHING
    return NOTHING
