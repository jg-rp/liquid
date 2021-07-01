"""Base class and file system implementation for loading template sources.

Modelled after Jinja2 template loaders.
See https://github.com/pallets/jinja/blob/master/src/jinja2/loaders.py
"""
from __future__ import annotations

import asyncio
import os

from abc import ABC
from abc import abstractmethod

from collections import abc
from pathlib import Path

from typing import NamedTuple
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Union
from typing import TYPE_CHECKING

from liquid.template import BoundTemplate
from liquid.exceptions import TemplateNotFound


if TYPE_CHECKING:
    from liquid import Environment


class TemplateSource(NamedTuple):
    """A Liquid template source as returned by the ``get_source`` method of a `loader`.

    :param source: The liquid template source code.
    :type source: str
    :param filename: The liquid template file name or other string identifying its
        origin.
    :type filename: str
    :param uptodate: Optional callable that will return ``True`` if the template is up
        to date, or ``False`` if it needs to be reloaded. Defaults to ``None``.
    :type uptodate: Optional[Callable[[], bool]]
    """

    source: str
    filename: str
    uptodate: Optional[Callable[[], bool]]


class BaseLoader(ABC):
    """Base template loader from which all template loaders are derived."""

    def get_source(self, env: Environment, template_name: str) -> TemplateSource:
        """Get the template source, filename and reload helper for a template"""
        raise NotImplementedError("template loaders must implement a get_source method")

    async def get_source_async(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        """ """
        return self.get_source(env, template_name)

    # pylint: disable=redefined-builtin
    def load(
        self,
        env: Environment,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        try:
            source, filename, uptodate = self.get_source(env, name)
        except Exception as err:
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source, globals=globals, name=name, path=Path(filename)
        )
        template.uptodate = uptodate
        return template

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        try:
            template_source = await self.get_source_async(env, name)
            source, filename, uptodate = template_source
        except Exception as err:
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source, globals=globals, name=name, path=Path(filename)
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

    def _resolve_path(self, template_name: str) -> Path:
        template_path = Path(template_name)

        if os.path.pardir in template_path.parts:
            raise TemplateNotFound(template_name)

        for path in self.search_path:
            source_path = path.joinpath(template_path)

            if not source_path.exists():
                continue
            return source_path
        raise TemplateNotFound(template_name)

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        source_path = self._resolve_path(template_name)

        with source_path.open(encoding=self.encoding) as fd:
            source = fd.read()

        mtime = source_path.stat().st_mtime

        return TemplateSource(
            source, str(source_path), lambda: mtime == source_path.stat().st_mtime
        )

    async def get_source_async(
        self, env: Environment, template_name: str
    ) -> TemplateSource:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.get_source, env, template_name)


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
