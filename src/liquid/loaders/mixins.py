from __future__ import annotations

from abc import ABC
from collections.abc import Awaitable, Callable, Mapping
from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING, Protocol

from .._lru_cache import LRUCache, ThreadSafeLRUCache

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._template import Template
    from ..environment import Environment


class _CachingLoaderProtocol(Protocol):
    def load(  # pragma: no cover
        self,
        env: Environment,
        name: str,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template: ...

    async def load_async(  # pragma: no cover
        self,
        env: Environment,
        name: str,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template: ...


class CachingLoaderMixin(ABC, _CachingLoaderProtocol):
    """A mixin class that adds caching to a template loader."""

    caching_loader = True

    def __init__(
        self,
        *,
        auto_reload: bool = True,
        namespace_key: str = "",
        capacity: int = 300,
        thread_safe: bool = False,
    ):
        self.auto_reload = auto_reload
        self.cache = (
            ThreadSafeLRUCache[str, "Template"](capacity=capacity)
            if thread_safe
            else LRUCache[str, "Template"](capacity=capacity)
        )
        self.namespace_key = namespace_key

    def _check_cache(
        self,
        env: Environment,
        cache_key: str,
        globals: Mapping[str, object] | None,
        load_func: Callable[[], Template],
    ) -> Template:
        try:
            cached_template = self.cache[cache_key]
        except KeyError:
            template = load_func()
            self.cache[cache_key] = template
            return template

        if self.auto_reload and not cached_template.is_up_to_date():
            template = load_func()
            self.cache[cache_key] = template
            return template

        if globals:
            cached_template.globals = globals
        return cached_template

    async def _check_cache_async(
        self,
        env: Environment,
        cache_key: str,
        globals: Mapping[str, object] | None,
        load_func: Callable[[], Awaitable[Template]],
    ) -> Template:
        try:
            cached_template = self.cache[cache_key]
        except KeyError:
            template = await load_func()
            self.cache[cache_key] = template
            return template

        if self.auto_reload and not await cached_template.is_up_to_date_async():
            template = await load_func()
            self.cache[cache_key] = template
            return template

        if globals:
            cached_template.globals = globals
        return cached_template

    def load(
        self,
        env: Environment,
        name: str,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        cache_key = self.cache_key(name, context, kwargs)
        return self._check_cache(
            env,
            cache_key,
            globals,
            partial(
                super().load,  # type: ignore
                env,
                name,
                globals=globals,
                context=context,
                **kwargs,
            ),
        )

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        cache_key = self.cache_key(name, context, kwargs)
        return await self._check_cache_async(
            env,
            name,
            globals,
            partial(
                super().load_async,  # type: ignore
                env,
                cache_key,
                globals=globals,
                context=context,
                **kwargs,
            ),
        )

    def cache_key(
        self,
        name: str,
        context: RenderContext | None,
        args: Mapping[str, object],
    ) -> str:
        if not self.namespace_key:
            return name

        # Args take priority over context variables.
        with suppress(KeyError):
            return f"{args[self.namespace_key]}/{name}"

        if context is None:
            return name

        try:
            return f"{context.globals[self.namespace_key]}/{name}"
        except KeyError:
            return name
