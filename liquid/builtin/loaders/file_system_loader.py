"""Built-in file system loader."""
from __future__ import annotations

import asyncio
import os
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Tuple
from typing import Union

from liquid.exceptions import TemplateNotFound

from .base_loader import BaseLoader
from .base_loader import TemplateSource

if TYPE_CHECKING:
    from liquid import Environment


class FileSystemLoader(BaseLoader):
    """A loader that loads templates from one or more directories on the file system.

    Args:
        search_path: One or more paths to search.
        encoding: Open template files with the given encoding.
    """

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        encoding: str = "utf-8",
    ):
        super().__init__()
        if not isinstance(search_path, Iterable) or isinstance(search_path, str):
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

    def get_source(  # noqa: D102
        self, _: Environment, template_name: str
    ) -> TemplateSource:
        source_path = self.resolve_path(template_name)
        source, mtime = self._read(source_path)
        return TemplateSource(
            source,
            str(source_path),
            partial(self._uptodate, source_path, mtime),
        )

    @staticmethod
    def _uptodate(source_path: Path, mtime: float) -> bool:
        return mtime == source_path.stat().st_mtime

    @staticmethod
    async def _uptodate_async(source_path: Path, mtime: float) -> bool:
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: mtime == source_path.stat().st_mtime
        )

    async def get_source_async(  # noqa: D102
        self, _: Environment, template_name: str
    ) -> TemplateSource:
        loop = asyncio.get_running_loop()
        source_path = await loop.run_in_executor(None, self.resolve_path, template_name)
        source, mtime = await loop.run_in_executor(None, self._read, source_path)
        return TemplateSource(
            source, str(source_path), partial(self._uptodate_async, source_path, mtime)
        )


class FileExtensionLoader(FileSystemLoader):
    """A file system loader that adds a file name extension if one is missing.

    Args:
        search_path: One or more paths to search.
        encoding: Open template files with the given encoding.
        ext: A default file extension. Should include a leading period.
    """

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        encoding: str = "utf-8",
        ext: str = ".liquid",
    ):
        super().__init__(search_path=search_path, encoding=encoding)
        self.ext = ext

    def resolve_path(self, template_name: str) -> Path:  # noqa: D102
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
