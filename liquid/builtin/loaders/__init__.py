from pathlib import Path
from typing import Iterable
from typing import List
from typing import Union

from .base_loader import BaseLoader
from .base_loader import DictLoader
from .base_loader import TemplateNamespace
from .base_loader import TemplateSource
from .base_loader import UpToDate

from .choice_loader import CachingChoiceLoader
from .choice_loader import ChoiceLoader

from .file_system_loader import FileExtensionLoader
from .file_system_loader import FileSystemLoader

from .caching_file_system_loader import CachingFileSystemLoader

from .package_loader import PackageLoader

__all__ = (
    "BaseLoader",
    "CachingChoiceLoader",
    "CachingFileSystemLoader",
    "ChoiceLoader",
    "DictLoader",
    "FileExtensionLoader",
    "FileSystemLoader",
    "make_choice_loader",
    "make_file_system_loader",
    "PackageLoader",
    "TemplateNamespace",
    "TemplateSource",
    "UpToDate",
)


def make_file_system_loader(
    search_path: Union[str, Path, Iterable[Union[str, Path]]],
    *,
    encoding: str = "utf-8",
    ext: str = ".liquid",
    auto_reload: bool = True,
    namespace_key: str = "",
    cache_size: int = 300,
) -> BaseLoader:
    """A _file system_ template loader factory.

    Returns one of `CachingFileSystemLoader`, `FileExtensionLoader` or
    `FileSystemLoader` depending in the given arguments.

    A `CachingFileSystemLoader` is returned if _cache_size_ is greater than 0.
    Otherwise a `FileExtensionLoader` is returned if _ext_ is not empty.
    Otherwise a `FileSystemLoader` is returned.

    _auto_reload_ and _namespace_key_ are ignored if _cache_key_ is less than 1.

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

    _New in version 1.12.0_
    """
    if cache_size > 0:
        return CachingFileSystemLoader(
            search_path=search_path,
            encoding=encoding,
            ext=ext,
            auto_reload=auto_reload,
            namespace_key=namespace_key,
            cache_size=cache_size,
        )

    if ext:
        return FileExtensionLoader(
            search_path=search_path,
            encoding=encoding,
            ext=ext,
        )

    return FileSystemLoader(search_path=search_path, encoding=encoding)


def make_choice_loader(
    loaders: List[BaseLoader],
    *,
    auto_reload: bool = True,
    namespace_key: str = "",
    cache_size: int = 300,
) -> BaseLoader:
    """A _choice loader_ factory.

    Returns one of `CachingChoiceLoader` or `ChoiceLoader` depending on the
    given arguments.

    A `CachingChoiceLoader` is returned if _cache_size_ > 0, otherwise a
    `ChoiceLoader` is returned.

    _auto_reload_ and _namespace_key_ are ignored if _cache_key_ is less than 1.

    Args:
        loaders: A list of loaders implementing `liquid.loaders.BaseLoader`.
        auto_reload: If `True`, automatically reload a cached template if it
            has been updated.
        namespace_key: The name of a global render context variable or loader
            keyword argument that resolves to the current loader "namespace" or
            "scope".
        cache_size: The maximum number of templates to hold in the cache before
            removing the least recently used template.

    _New in version 1.12.0_
    """
    if cache_size > 0:
        return CachingChoiceLoader(
            loaders=loaders,
            auto_reload=auto_reload,
            namespace_key=namespace_key,
            cache_size=cache_size,
        )

    return ChoiceLoader(loaders=loaders)
