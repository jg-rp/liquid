from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, TypeGuard

from .drops import IterableDrop

if TYPE_CHECKING:
    from ._context import RenderContext

type ContextHint = Literal["string", "data", "numeric", "boolean"]


class LiquidDrop(Protocol):
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object: ...


def is_drop(obj: object) -> TypeGuard[LiquidDrop]:
    return hasattr(obj, "__liquid__")


class LiquidIterable(Protocol):
    def __liquid_iter__(
        self, start: int, end: int | None, reversed_: bool
    ) -> IterableDrop[int]: ...


def is_iterable_drop(obj: object) -> TypeGuard[LiquidIterable]:
    return hasattr(obj, "__liquid_iter__")
