"""A file system loader that caches parsed templates in memory."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import Union

from .file_system_loader import FileSystemLoader
from .mixins import CachingLoaderMixin

if TYPE_CHECKING:
    from pathlib import Path


class CachingFileSystemLoader(CachingLoaderMixin, FileSystemLoader):
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
        capacity: The maximum number of templates to hold in the cache before removing
            the least recently used template.
    """

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        encoding: str = "utf-8",
        ext: Optional[str] = None,
        *,
        auto_reload: bool = True,
        namespace_key: str = "",
        capacity: int = 300,
    ):
        super().__init__(
            auto_reload=auto_reload,
            namespace_key=namespace_key,
            capacity=capacity,
        )

        FileSystemLoader.__init__(
            self,
            search_path=search_path,
            encoding=encoding,
            ext=ext,
        )
