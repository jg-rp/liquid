"""Base class and file system implementation for loading template sources.

Modelled after Jinja2 template loaders.
See https://github.com/pallets/jinja/blob/master/src/jinja2/loaders.py
"""
from __future__ import annotations

import asyncio
import os

from abc import ABC

from collections import abc
from functools import partial
from pathlib import Path

from typing import Awaitable
from typing import NamedTuple
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Tuple
from typing import Union
from typing import TYPE_CHECKING

from liquid.template import BoundTemplate
from liquid.exceptions import TemplateNotFound


if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid import Context

UpToDate = Union[Callable[[], bool], Callable[[], Awaitable[bool]], None]


class TemplateSource(NamedTuple):
    """A Liquid template source as returned by the ``get_source`` method of a `loader`.

    :param source: The liquid template source code.
    :type source: str
    :param filename: The liquid template file name or other string identifying its
        origin.
    :type filename: str
    :param uptodate: Optional callable that will return ``True`` if the template is up
        to date, or ``False`` if it needs to be reloaded. Defaults to ``None``.
    :type uptodate: Union[Callable[[], bool], Callable[[], Awaitable[bool]], None]
    :param matter: Optional mapping containing variables associated with the template.
        Could be "front matter" or other meta data.
    :type matter: Optional[Mapping[str, object]]
    """

    source: str
    filename: str
    uptodate: UpToDate
    matter: Optional[Mapping[str, object]] = None


# flake8: noqa
class BaseLoader(ABC):
    """Base template loader from which all template loaders are derived."""

    def get_source(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        """Get the template source, filename and reload helper for a template"""
        raise NotImplementedError("template loaders must implement a get_source method")

    async def get_source_async(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        """An async version of `get_source`. The default implementation delegates to
        `get_source()`."""
        return self.get_source(env, template_name)

    # pylint: disable=unused-argument
    def get_source_with_context(
        self,
        context: Context,
        template_name: str,
        **kwargs: str,
    ) -> TemplateSource:
        """Get a template's source, optionally referencing a render context."""
        return self.get_source(context.env, template_name)

    # pylint: disable=unused-argument
    async def get_source_with_context_async(
        self,
        context: Context,
        template_name: str,
        **kwargs: str,
    ) -> TemplateSource:
        """An async version of `get_source_with_context`."""
        return await self.get_source_async(context.env, template_name)

    # pylint: disable=redefined-builtin
    def load(
        self,
        env: Environment,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """Load and parse a template. Used internally by `Environment` to load a
        template source. Delegates to `get_source`.

        A custom loaders would typically implement `get_source` rather than overriding
        `load`.
        """
        try:
            source, filename, uptodate, matter = self.get_source(env, name)
        except Exception as err:
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source,
            globals=globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """An async version of `load`."""
        try:
            template_source = await self.get_source_async(env, name)
            source, filename, uptodate, matter = template_source
        except Exception as err:
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source,
            globals=globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    def load_with_context(
        self,
        context: Context,
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """Load and parse a template, optionally referencing a render context."""
        try:
            source, filename, uptodate, matter = self.get_source_with_context(
                context, name, **kwargs
            )
        except Exception as err:
            raise TemplateNotFound(name) from err

        template = context.env.from_string(
            source,
            globals=context.globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    async def load_with_context_async(
        self,
        context: Context,
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """An async version of `load_with_context`."""
        try:
            (
                source,
                filename,
                uptodate,
                matter,
            ) = await self.get_source_with_context_async(context, name, **kwargs)
        except Exception as err:
            raise TemplateNotFound(name) from err

        template = context.env.from_string(
            source,
            globals=context.globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template


class FileSystemLoader(BaseLoader):
    """A loader that loads templates from one or more directories on the file system.

    :param search_path: One or more paths to search.
    :type search_path: Union[str, Path, Iterable[Union[str, Path]]]
    :param encoding: Open template files with the given encoding. Defaults to
        ``"utf-8"``.
    :type encoding: str
    """

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        encoding: str = "utf-8",
    ):
        if not isinstance(search_path, abc.Iterable) or isinstance(search_path, str):
            search_path = [search_path]

        self.search_path = [Path(path) for path in search_path]
        self.encoding = encoding

    def resolve_path(self, template_name: str) -> Path:
        """Return a path to the template `template_name`.

        If the search path is a list of paths, returns the first path where
        `template_name` exists. If none of the search paths contain `template_name`, a
        `TemplateNotFound` exception is raised.
        """
        template_path = Path(template_name)

        if os.path.pardir in template_path.parts:
            raise TemplateNotFound(template_name)

        for path in self.search_path:
            source_path = path.joinpath(template_path)

            if not source_path.exists():
                continue
            return source_path
        raise TemplateNotFound(template_name)

    def _read(self, source_path: Path) -> Tuple[str, float]:
        with source_path.open(encoding=self.encoding) as fd:
            source = fd.read()
        return source, source_path.stat().st_mtime

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        source_path = self.resolve_path(template_name)
        source, mtime = self._read(source_path)

        return TemplateSource(
            source, str(source_path), lambda: mtime == source_path.stat().st_mtime
        )

    @staticmethod
    async def _uptodate(source_path: Path, mtime: float) -> bool:
        uptodate = await asyncio.get_running_loop().run_in_executor(
            None, lambda: mtime == source_path.stat().st_mtime
        )
        return uptodate

    async def get_source_async(
        self, env: Environment, template_name: str
    ) -> TemplateSource:
        loop = asyncio.get_running_loop()
        source_path = await loop.run_in_executor(None, self.resolve_path, template_name)
        source, mtime = await loop.run_in_executor(None, self._read, source_path)
        return TemplateSource(
            source, str(source_path), partial(self._uptodate, source_path, mtime)
        )


class FileExtensionLoader(FileSystemLoader):
    """A file system loader that adds a file name extension if one is missing.

    :param search_path: One or more paths to search.
    :type search_path: Union[str, Path, Iterable[Union[str, Path]]]
    :param encoding: Open template files with the given encoding. Defaults to
        ``"utf-8"``.
    :type encoding: str
    :param ext: A default file extension. Should include a leading period. Defaults to
        ``.liquid``.
    :type ext: str
    """

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        encoding: str = "utf-8",
        ext: str = ".liquid",
    ):
        super().__init__(search_path, encoding=encoding)
        self.ext = ext

    def resolve_path(self, template_name: str) -> Path:
        template_path = Path(template_name)

        if not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        # Don't allow "../" to escape the search path.
        if os.path.pardir in template_path.parts:
            raise TemplateNotFound(template_name)

        for path in self.search_path:
            source_path = path.joinpath(template_path)

            if not source_path.exists():
                continue
            return source_path
        raise TemplateNotFound(template_name)


class DictLoader(BaseLoader):
    """A loader that loads templates from a dictionary mapping template names to
    template source strings. If the given dictionary is empty,
    :meth:`liquid.Environment.get_template` will always raise a
    :class:`liquid.exceptions.TemplateNotFound` exception.

    :param templates: A dictionary mapping template names to template source strings.
    :type templates: Dict[str, str]
    """

    def __init__(self, templates: Dict[str, str]):
        super().__init__()
        self.templates = templates

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFound(template_name) from err

        return TemplateSource(source, template_name, None)


class ChoiceLoader(BaseLoader):
    """A template loader that will try each of a list of loaders until a template is
    found, or raise a :class:`liquid.exceptions.TemplateNotFound` exception if none of
    the loaders could find the template.

    :param loaders: A list of loaders implementing :class:`liquid.loaders.BaseLoader`.
    :type loaders: List[BaseLoader]
    """

    def __init__(self, loaders: List[BaseLoader]):
        super().__init__()
        self.loaders = loaders

    def get_source(self, env: Environment, template_name: str) -> TemplateSource:
        for loader in self.loaders:
            try:
                return loader.get_source(env, template_name)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)

    async def get_source_async(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        for loader in self.loaders:
            try:
                return await loader.get_source_async(env, template_name)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)
