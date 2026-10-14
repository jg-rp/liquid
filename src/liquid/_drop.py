from __future__ import annotations

from abc import ABC
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypeGuard

if TYPE_CHECKING:
    from ._context import RenderContext
    from .drops import IterableDrop

type ContextHint = Literal["string", "data", "numeric", "boolean"]


class Drop(ABC, Mapping[object, object]):
    def __iter__(self) -> Iterator[object]:
        return iter([])

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string":
                return ""
            case "data":
                return None
            case "numeric":
                return 0
            case "boolean":
                return False

    def __len__(self) -> int:
        return 0

    def __getitem__(self, key: Any) -> object:
        raise KeyError

    def __str__(self) -> str:
        return ""

    def __bool__(self) -> bool:
        return False

    # Implementations of these methods should raise a LiquidTypeError if arguments
    # are not comparable.

    def __eq__(self, other: object) -> bool:
        return False

    def __lt__(self, other: object) -> bool:
        return False

    def __le__(self, other: object) -> bool:
        return False

    def __gt__(self, other: object) -> bool:
        return False

    def __ge__(self, other: object) -> bool:
        return False

    def __contains__(self, item: object) -> bool:
        return False


class LiquidDrop(Protocol):
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object: ...


# TODO: update all built-in drops
# TODO: Make sure all custom Mapping types implement __contains__.


def is_drop(obj: object) -> TypeGuard[Drop]:
    return isinstance(obj, Drop)


class LiquidHTMLSafe(Protocol):
    def __html__(self) -> str: ...


def has_html_safe_string(obj: object) -> TypeGuard[LiquidHTMLSafe]:
    return hasattr(obj, "__html__")


class LiquidIterable(Protocol):
    def __liquid_iter__(
        self, start: int, end: int | None, reversed_: bool
    ) -> IterableDrop[int]: ...


def is_iterable_drop(obj: object) -> TypeGuard[LiquidIterable]:
    return hasattr(obj, "__liquid_iter__")


class LiquidAsyncMap(Protocol):
    async def __getitem_async__(self, key: Any) -> object: ...


def is_async_map(obj: object) -> TypeGuard[LiquidAsyncMap]:
    return hasattr(obj, "__getitem_async__")
