from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, TypeGuard

if TYPE_CHECKING:
    from ._context import RenderContext
    from .drops import AsyncIterableDrop, IterableDrop

type ContextHint = Literal["string", "array", "data", "numeric", "boolean"]


class LiquidObject(Protocol):
    def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
        """Return whether a Liquid property with the given name exists.

        The context is available for property-existence checks that depend on
        the current render context. Implementations should distinguish between
        a missing property and an existing property whose value is None.
        """
        ...

    def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
        """Return the value of a Liquid property.

        The context is available for resolving values that depend on the
        current render context. Implementations should raise an AttributeError
        exception when a property cannot be resolved.

        This synchronous method is used during synchronous rendering.
        """
        ...


def liquid_object(obj: object) -> TypeGuard[LiquidObject]:
    return hasattr(obj, "__liquid_hasattr__") and hasattr(obj, "__liquid_getattr__")


class LiquidAsyncObject(Protocol):
    async def __liquid_hasattr_async__(self, name: str, context: RenderContext) -> bool:
        """Asynchronously determine whether a Liquid property exists.

        This method is used during asynchronous rendering. Implementations
        may override it when checking property existence requires asynchronous
        work.
        """
        ...

    async def __liquid_getattr_async__(
        self, name: str, context: RenderContext
    ) -> object:
        """Asynchronously resolve a Liquid property.

        This method is used during asynchronous rendering. Implementations may
        override it when resolving a property requires asynchronous work.
        """
        ...


def liquid_async_object(obj: object) -> TypeGuard[LiquidAsyncObject]:
    return hasattr(obj, "__liquid_hasattr_async__") and hasattr(
        obj, "__liquid_getattr_async__"
    )


class LiquidIterable(Protocol):
    def __liquid_iter__(
        self, offset: int, limit: int | None, reversed_: bool
    ) -> IterableDrop[object]:
        """Return a Liquid iterable."""
        ...


def liquid_iterable(obj: object) -> TypeGuard[LiquidIterable]:
    return hasattr(obj, "__liquid_iter__")


class LiquidAsyncIterable(Protocol):
    async def __liquid_iter_async__(
        self, offset: int, limit: int | None, reversed_: bool
    ) -> IterableDrop[object] | AsyncIterableDrop[object]:
        """Return a asynchronous Liquid iterable."""
        ...


def liquid_async_iterable(obj: object) -> TypeGuard[LiquidAsyncIterable]:
    return hasattr(obj, "__liquid_iter_async__")


class LiquidPrimitive(Protocol):
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        """Convert this Drop to a Liquid primitive type.

        The hint identifies the requested representation:
        """
        ...


def liquid_primitive(obj: object) -> TypeGuard[LiquidPrimitive]:
    return hasattr(obj, "__liquid__")


class LiquidHTMLSafe(Protocol):
    def __html__(self) -> str:
        """Return an HTML-safe string representation of this Drop."""
        ...


def liquid_html_safe(obj: object) -> TypeGuard[LiquidHTMLSafe]:
    return hasattr(obj, "__html__")
