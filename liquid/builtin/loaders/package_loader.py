"""A template loader that reads templates from Python packages."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Union

from importlib_resources import files

from liquid.exceptions import TemplateNotFound

from .base_loader import BaseLoader
from .base_loader import TemplateSource

if TYPE_CHECKING:
    from types import ModuleType

    from importlib_resources.abc import Traversable

    from liquid import Environment


class PackageLoader(BaseLoader):
    """A template loader that reads templates from Python packages.

    Args:
        package: Import name of a package containing Liquid templates.
        package_path: One or more directories in the package containing Liquid
            templates.
        encoding: Encoding of template files.
        ext: A default file extension to use if one is not provided. Should
            include a leading period.

    _New in version 1.11.0._
    """

    def __init__(
        self,
        package: Union[str, ModuleType],
        *,
        package_path: Union[str, Iterable[str]] = "templates",
        encoding: str = "utf-8",
        ext: str = ".liquid",
    ) -> None:
        if isinstance(package_path, str):
            self.paths = [files(package).joinpath(package_path)]
        else:
            _package = files(package)
            self.paths = [_package.joinpath(path) for path in package_path]

        self.encoding = encoding
        self.ext = ext

    def _resolve_path(self, template_name: str) -> Traversable:
        template_path = Path(template_name)

        # Don't build a path that escapes package/package_path.
        # Does ".." appear in template_name?
        if os.path.pardir in template_path.parts:
            raise TemplateNotFound(template_name)

        # Add suffix self.ext if template name does not have a suffix.
        if not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        for path in self.paths:
            source_path = path.joinpath(template_path)
            if source_path.is_file():
                # MyPy seems to think source_path has `Any` type :(
                return source_path  # type: ignore

        raise TemplateNotFound(template_name)

    def get_source(  # noqa: D102
        self,
        _: Environment,
        template_name: str,
    ) -> TemplateSource:
        source_path = self._resolve_path(template_name)
        return TemplateSource(
            source=source_path.read_text(self.encoding),
            filename=str(source_path),
            uptodate=None,
        )

    async def get_source_async(  # noqa: D102
        self, _: Environment, template_name: str
    ) -> TemplateSource:
        loop = asyncio.get_running_loop()

        source_path = await loop.run_in_executor(
            None,
            self._resolve_path,
            template_name,
        )

        source_text = await loop.run_in_executor(
            None,
            source_path.read_text,
            self.encoding,
        )

        return TemplateSource(
            source=source_text, filename=str(source_path), uptodate=None
        )
