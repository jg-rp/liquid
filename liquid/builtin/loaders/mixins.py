"""Mixin classes that can be used to add common functions to a template loader."""
from __future__ import annotations

from abc import ABC
from functools import partial
from typing import TYPE_CHECKING
from typing import Awaitable
from typing import Callable
from typing import Mapping

from typing_extensions import Protocol

from liquid.utils import LRUCache

if TYPE_CHECKING:
    from liquid import BoundTemplate
    from liquid import Context
    from liquid import Environment

    from .base_loader import TemplateNamespace

# ruff: noqa: D102

# ignoring "safe-super" type errors due to https://github.com/python/mypy/issues/14757


class _CachingLoaderProtocol(Protocol):
    def load(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        ...

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        ...

    def load_with_args(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        ...

    async def load_with_args_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        ...

    def load_with_context(
        self,
        context: Context,
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        ...

    async def load_with_context_async(
        self,
        context: Context,
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        ...


class CachingLoaderMixin(ABC, _CachingLoaderProtocol):
    """A mixin class that adds caching to a template loader."""

    caching_loader = True

    def __init__(
        self,
        *,
        auto_reload: bool = True,
        namespace_key: str = "",
        cache_size: int = 300,
    ):
        self.auto_reload = auto_reload
        self.cache = LRUCache(capacity=cache_size)
        self.namespace_key = namespace_key

    def _check_cache(
        self,
        env: Environment,  # noqa: ARG002
        cache_key: str,
        globals: TemplateNamespace,  # noqa: A002
        load_func: Callable[[], BoundTemplate],
    ) -> BoundTemplate:
        try:
            cached_template: BoundTemplate = self.cache[cache_key]
        except KeyError:
            template = load_func()
            self.cache[cache_key] = template
            return template

        if self.auto_reload and not cached_template.is_up_to_date:
            template = load_func()
            self.cache[cache_key] = template
            return template

        if globals:
            cached_template.globals.update(globals)
        return cached_template

    async def _check_cache_async(
        self,
        env: Environment,  # noqa: ARG002
        cache_key: str,
        globals: TemplateNamespace,  # noqa: A002
        load_func: Callable[[], Awaitable[BoundTemplate]],
    ) -> BoundTemplate:
        try:
            cached_template: BoundTemplate = self.cache[cache_key]
        except KeyError:
            template = await load_func()
            self.cache[cache_key] = template
            return template

        if self.auto_reload and not await cached_template.is_up_to_date_async():
            template = await load_func()
            self.cache[cache_key] = template
            return template

        if globals:
            cached_template.globals.update(globals)
        return cached_template

    def load(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        return self._check_cache(
            env,
            name,
            globals,
            partial(super().load, env, name, globals),  # type: ignore
        )

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        return await self._check_cache_async(
            env,
            name,
            globals,
            partial(super().load_async, env, name, globals),  # type: ignore
        )

    def load_with_args(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        cache_key = self.cache_key(name, kwargs)
        return self._check_cache(
            env,
            cache_key,
            globals,
            partial(super().load_with_args, env, cache_key, globals, **kwargs),  # type: ignore
        )

    async def load_with_args_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        cache_key = self.cache_key(name, kwargs)
        return await self._check_cache_async(
            env,
            cache_key,
            globals,
            partial(super().load_with_args_async, env, cache_key, globals, **kwargs),  # type: ignore
        )

    def load_with_context(
        self, context: Context, name: str, **kwargs: str
    ) -> BoundTemplate:
        cache_key = self.cache_key_with_context(name, context, **kwargs)
        return self._check_cache(
            context.env,
            cache_key,
            context.globals,
            partial(super().load_with_context, context=context, name=name, **kwargs),  # type: ignore
        )

    async def load_with_context_async(
        self, context: Context, name: str, **kwargs: str
    ) -> BoundTemplate:
        cache_key = self.cache_key_with_context(name, context, **kwargs)
        return await self._check_cache_async(
            context.env,
            cache_key,
            context.globals,
            partial(super().load_with_context_async, context, name, **kwargs),  # type: ignore
        )

    def cache_key(self, name: str, args: Mapping[str, object]) -> str:
        if not self.namespace_key:
            return name

        try:
            return f"{args[self.namespace_key]}/{name}"
        except KeyError:
            return name

    def cache_key_with_context(
        self,
        name: str,
        context: Context,
        **kwargs: str,  # noqa: ARG002
    ) -> str:
        if not self.namespace_key:
            return name

        try:
            return f"{context.globals[self.namespace_key]}/{name}"
        except KeyError:
            return name
