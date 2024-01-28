"""A file system loader that caches parsed templates in memory."""
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterable
from typing import Union

from .file_system_loader import FileExtensionLoader
from .mixins import CachingLoaderMixin

if TYPE_CHECKING:
    from pathlib import Path

    from liquid import Context

    from .base_loader import TemplateSource

# ruff: noqa: D102


class CachingFileSystemLoader(CachingLoaderMixin, FileExtensionLoader):
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
            auto_reload=auto_reload,
            namespace_key=namespace_key,
            cache_size=cache_size,
        )

        FileExtensionLoader.__init__(
            self,
            search_path=search_path,
            encoding=encoding,
            ext=ext,
        )

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
