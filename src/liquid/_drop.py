from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Literal, Protocol, TypeGuard

if TYPE_CHECKING:
    from ._context import RenderContext
    from .drops import AsyncIterableDrop, IterableDrop

type ContextHint = Literal["string", "data", "numeric", "boolean"]


# class _Drop(Protocol):
#     """Protocol for objects that participate in Liquid's evaluation model.

#     Drops can provide context-aware property resolution, expose methods for
#     automatic invocation, customize primitive conversion, and implement
#     Liquid-specific iteration.

#     Implementations need not inherit from a particular base class. The
#     renderer detects the supported interfaces at runtime.
#     """

#     def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
#         """Return whether a Liquid property with the given name exists.

#         The context is available for property-existence checks that depend on
#         the current render context. Implementations should distinguish between
#         a missing property and an existing property whose value is None.
#         """
#         ...

#     def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
#         """Return the value of a Liquid property.

#         The context is available for resolving values that depend on the
#         current render context. Implementations should raise an AttributeError
#         exception when a property cannot be resolved.

#         This synchronous method is used during synchronous rendering.
#         """
#         ...

#     async def __liquid_hasattr_async__(self, name: str, context: RenderContext) -> bool:
#         """Asynchronously determine whether a Liquid property exists.

#         This method is used during asynchronous rendering. Implementations
#         may override it when checking property existence requires asynchronous
#         work.
#         """
#         ...

#     async def __liquid_getattr_async__(
#         self, name: str, context: RenderContext
#     ) -> object:
#         """Asynchronously resolve a Liquid property.

#         This method is used during asynchronous rendering. Implementations may
#         override it when resolving a property requires asynchronous work.
#         """
#         ...

#     def __liquid_callable__(self, name: str) -> bool:
#         """Return whether a named property may be called automatically.

#         If `True` is returned, this drop must implement a zero-argument method
#         matching `name`.
#         """
#         ...

#     def __liquid_awaitable__(self, name: str) -> bool:
#         """Return whether a named property is asynchronously callable.

#         If `True` is returned, this drop must implement a zero-argument async
#         method matching `name`.

#         During asynchronous rendering, the renderer checks this method before
#         __liquid_callable__. If this method is not implemented, the renderer falls
#         back to __liquid_callable__.

#         During synchronous rendering, this method is ignored.
#         """
#         ...

#     def __liquid_iter__(
#         self, offset: int, limit: int | None, reversed_: bool
#     ) -> IterableDrop[object]:
#         """Return a Liquid iterable with the requested iteration options."""
#         ...

#     async def __liquid_iter_async__(
#         self, offset: int, limit: int | None, reversed_: bool
#     ) -> AsyncIterableDrop[object]:
#         """Asynchronously provide a Liquid iterable with the given options."""
#         ...

#     def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
#         """Convert this Drop to a Liquid primitive type.

#         The hint identifies the requested representation:
#         """
#         ...

#     def __html__(self) -> str:
#         """Return an HTML-safe string representation of this Drop."""
#         ...


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


class LiquidCallable(Protocol):
    def __liquid_callable__(self, name: str) -> bool:
        """Return whether a named property may be called automatically.

        If `True` is returned, this drop must implement a zero-argument method
        matching `name`.
        """
        ...


def liquid_callable(obj: object) -> TypeGuard[LiquidCallable]:
    return hasattr(obj, "__liquid_callable__")


class LiquidAwaitable(Protocol):
    def __liquid_awaitable__(self, name: str) -> bool:
        """Return whether a named property is asynchronously callable.

        If `True` is returned, this drop must implement a zero-argument async
        method matching `name`.

        During asynchronous rendering, the renderer checks this method before
        __liquid_callable__. If this method is not implemented, the renderer falls
        back to __liquid_callable__.

        During synchronous rendering, this method is ignored.
        """
        ...


def liquid_awaitable(obj: object) -> TypeGuard[LiquidCallable]:
    return hasattr(obj, "__liquid_awaitable__")


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
    ) -> AsyncIterableDrop[object]:
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


class AbstractDrop(ABC):
    def __liquid_hasattr__(self, name: str, context: RenderContext) -> bool:
        return False

    def __liquid_getattr__(self, name: str, context: RenderContext) -> object:
        raise AttributeError(f"{self.__class__.__name__!r} has no attribute {name!r}")

    def __liquid_callable__(self, name: str) -> bool:
        return False

    def __liquid_awaitable__(self, name: str) -> bool:
        return False

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

    def __str__(self) -> str:
        return ""

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return False

    def __lt__(self, other: object) -> bool:
        raise TypeError(
            "'<' not supported between instances of "
            f"'{self.__class__.__name__}' and {other.__class__.__name__}"
        )

    def __le__(self, other: object) -> bool:
        raise TypeError(
            "'<=' not supported between instances of "
            f"'{self.__class__.__name__}' and {other.__class__.__name__}"
        )

    def __gt__(self, other: object) -> bool:
        raise TypeError(
            "'>' not supported between instances of "
            f"'{self.__class__.__name__}' and {other.__class__.__name__}"
        )

    def __ge__(self, other: object) -> bool:
        raise TypeError(
            "'>=' not supported between instances of "
            f"'{self.__class__.__name__}' and {other.__class__.__name__}"
        )
