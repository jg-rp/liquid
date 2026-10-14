from __future__ import annotations

import asyncio
import importlib.resources
import os
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from .._loader import Loader, TemplateSource
from ..exceptions import TemplateNotFoundError

if TYPE_CHECKING:
    from types import ModuleType

    from .._context import RenderContext
    from ..environment import Environment


class PackageLoader(Loader):
    """A template loader that reads templates from Python packages.

    Parameters
    ----------
    package
        Import name of a package containing Liquid templates.
    package_path
        One or more directories in the package containing Liquid templates.
    encoding
        Encoding of template files.
    ext
        A default file extension to use if one is not provided. Should include
        a leading period.
    """

    def __init__(
        self,
        package: str | ModuleType,
        *,
        package_path: str | Iterable[str] = "templates",
        encoding: str = "utf-8",
        ext: str = ".liquid",
    ) -> None:
        if isinstance(package_path, str):
            self.paths = [importlib.resources.files(package).joinpath(package_path)]
        else:
            _package = importlib.resources.files(package)
            self.paths = [_package.joinpath(path) for path in package_path]

        self.encoding = encoding
        self.ext = ext

    def _resolve_path(self, name: str) -> Path:
        template_path = Path(name)

        if not template_path.name:
            raise TemplateNotFoundError(name)

        # Add suffix self.ext if template name does not have a suffix.
        if not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        if os.path.pardir in template_path.parts or template_path.is_absolute():
            raise TemplateNotFoundError(name)

        for path in self.paths:
            with importlib.resources.as_file(path) as base:
                source_path: Path = base.joinpath(template_path)

                try:
                    if not source_path.exists() or not source_path.is_file():
                        continue
                except OSError:
                    # "File name too long", for example
                    continue

                resolved = source_path.resolve(strict=False)
                base_resolved = base.resolve(strict=False)

                if not resolved.is_relative_to(base_resolved):
                    continue

                return source_path

        raise TemplateNotFoundError(name)

    def get_source(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        source_path = self._resolve_path(name)
        return TemplateSource(
            text=source_path.read_text(self.encoding),
            name=str(source_path),
        )

    async def get_source_async(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        loop = asyncio.get_running_loop()

        source_path = await loop.run_in_executor(
            None,
            self._resolve_path,
            name,
        )

        source_text = await loop.run_in_executor(
            None,
            source_path.read_text,
            self.encoding,
        )

        return TemplateSource(
            text=source_text,
            name=str(source_path),
        )
