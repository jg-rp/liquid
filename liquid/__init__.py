from pathlib import Path
from typing import Iterable
from typing import Union

from markupsafe import Markup
from markupsafe import escape
from markupsafe import soft_str

from .mode import Mode
from .token import Token
from .expression import Expression

from .context import RenderContext
from .context import FutureContext
from .undefined import DebugUndefined
from .undefined import is_undefined
from .undefined import FalsyStrictUndefined
from .undefined import StrictDefaultUndefined
from .undefined import StrictUndefined
from .undefined import Undefined

from .environment import Environment
from .environment import Template

from .template import AwareBoundTemplate
from .template import BoundTemplate
from .template import FutureAwareBoundTemplate
from .template import FutureBoundTemplate

from .builtin import CachingDictLoader
from .builtin import DictLoader
from .builtin import ChoiceLoader
from .builtin import CachingChoiceLoader
from .builtin import CachingFileSystemLoader
from .builtin import FileSystemLoader
from .builtin import PackageLoader
from .builtin import CachingLoaderMixin
from .loader import BaseLoader

from .ast import Node
from .ast import BlockNode
from .ast import ConditionalBlockNode

from .analyze_tags import TagAnalysis
from .analyze_tags import DEFAULT_INNER_TAG_MAP


from .stream import TokenStream
from .tag import Tag

from . import future

__version__ = "2.0.0"

__all__ = (
    "AwareBoundTemplate",
    "BoundTemplate",
    "CachingChoiceLoader",
    "CachingFileSystemLoader",
    "ChoiceLoader",
    "RenderContext",
    "DebugUndefined",
    "DEFAULT_INNER_TAG_MAP",
    "DictLoader",
    "Environment",
    "escape",
    "Expression",
    "CachingDictLoader",
    "FileSystemLoader",
    "future",
    "FutureAwareBoundTemplate",
    "FutureBoundTemplate",
    "FutureContext",
    "is_undefined",
    "make_choice_loader",
    "make_file_system_loader",
    "CachingLoaderMixin",
    "Markup",
    "Mode",
    "PackageLoader",
    "soft_str",
    "StrictDefaultUndefined",
    "StrictUndefined",
    "TagAnalysis",
    "Template",
    "Token",
    "Undefined",
    "TokenStream",
    "parse",
    "render",
    "render_async",
    "Node",
    "BlockNode",
    "ConditionalBlockNode",
    "Tag",
    "FalsyStrictUndefined",
)

DEFAULT_ENVIRONMENT = Environment()


def parse(source: str) -> BoundTemplate:
    """Parse template source text using the default environment."""
    return DEFAULT_ENVIRONMENT.from_string(source)


def render(source: str, **data: object) -> str:
    """Parse and render source text using the default environment."""
    return DEFAULT_ENVIRONMENT.render(source, **data)


async def render_async(source: str, **data: object) -> str:
    """Parse and render source text using the default environment."""
    return await DEFAULT_ENVIRONMENT.render_async(source, **data)


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

    Returns one of `CachingFileSystemLoader` or `FileSystemLoader` depending in
    the given arguments.

    A `CachingFileSystemLoader` is returned if _cache_size_ is greater than 0.
    Otherwise a `FileExtensionLoader` is returned if _ext_ is not empty.
    If _ext_ is empty, a `FileSystemLoader` is returned.

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
            capacity=cache_size,
        )

    return FileSystemLoader(search_path=search_path, encoding=encoding, ext=ext)


def make_choice_loader(
    loaders: list[BaseLoader],
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
            capacity=cache_size,
        )

    return ChoiceLoader(loaders=loaders)
