"""A file system loader that caches parsed templates in memory."""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING
from typing import Awaitable
from typing import Callable
from typing import Iterable
from typing import Mapping
from typing import Union

from liquid.utils import LRUCache

from .file_system_loader import FileExtensionLoader

if TYPE_CHECKING:
    from pathlib import Path

    from liquid import BoundTemplate
    from liquid import Context
    from liquid import Environment

    from .base_loader import TemplateNamespace
    from .base_loader import TemplateSource

# ruff: noqa: D102 D101


class CachingFileSystemLoader(FileExtensionLoader):
    """A file system loader that caches parsed templates in memory.

    Args:
        search_path: One or more paths to search.
        encoding: Open template files with the given encoding.
        ext: A default file extension. Should include a leading period.
        auto_reload: If `True`, automatically reload a cached template if it has been
            updated.
        namespace_key: The name of a global render context variable or loader keyword
            argument that resolves to the current loader "namespace" or "scope".

            If you're developing a multi-user application, a good namespace might be
            `uid`, where `uid` is a unique identifier for a user and templates are
            arranged in folders named for each `uid` inside the search path.
        cache_size: The maximum number of templates to hold in the cache before removing
            the least recently used template.
    """

    caching_loader = True

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        encoding: str = "utf-8",
        ext: str = ".liquid",
        *,
        auto_reload: bool = True,
        namespace_key: str = "",
        cache_size: int = 300,
    ):
        super().__init__(
            search_path=search_path,
            encoding=encoding,
            ext=ext,
        )
        self.auto_reload = auto_reload
        self.cache = LRUCache(capacity=cache_size)
        self.namespace_key = namespace_key

    def load(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        return self.check_cache(
            env,
            name,
            globals,
            partial(super().load, env, name, globals),
        )

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        return await self.check_cache_async(
            env,
            name,
            globals,
            partial(super().load_async, env, name, globals),
        )

    def load_with_args(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        cache_key = self.cache_key(name, kwargs)
        return self.check_cache(
            env,
            cache_key,
            globals,
            partial(super().load_with_args, env, cache_key, globals, **kwargs),
        )

    async def load_with_args_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        cache_key = self.cache_key(name, kwargs)
        return await self.check_cache_async(
            env,
            cache_key,
            globals,
            partial(super().load_with_args_async, env, cache_key, globals, **kwargs),
        )

    def load_with_context(
        self, context: Context, name: str, **kwargs: str
    ) -> BoundTemplate:
        cache_key = self.cache_key_with_context(name, context, **kwargs)
        return self.check_cache(
            context.env,
            cache_key,
            context.globals,
            partial(super().load_with_context, context=context, name=name, **kwargs),
        )

    async def load_with_context_async(
        self, context: Context, name: str, **kwargs: str
    ) -> BoundTemplate:
        cache_key = self.cache_key_with_context(name, context, **kwargs)
        return await self.check_cache_async(
            context.env,
            cache_key,
            context.globals,
            partial(super().load_with_context_async, context, name, **kwargs),
        )

    def check_cache(
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

    async def check_cache_async(
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

    def get_source_with_context(
        self, context: Context, template_name: str, **kwargs: str
    ) -> TemplateSource:
        # In this case, our cache key and real file name are the same.
        name = self.cache_key_with_context(template_name, context, **kwargs)
        return self.get_source(context.env, name)

    async def get_source_with_context_async(
        self, context: Context, template_name: str, **kwargs: str
    ) -> TemplateSource:
        # In this case, our cache key and real file name are the same.
        name = self.cache_key_with_context(template_name, context, **kwargs)
        return await self.get_source_async(context.env, name)
