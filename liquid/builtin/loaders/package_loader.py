"""A template loader that reads templates from Python packages."""

from __future__ import annotations

import asyncio
import os
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import Union

from liquid.exceptions import TemplateNotFoundError
from liquid.loader import BaseLoader
from liquid.loader import TemplateSource

if TYPE_CHECKING:
    from importlib.abc import Traversable
    from types import ModuleType

    from liquid import Environment
    from liquid import RenderContext


class PackageLoader(BaseLoader):
    """A template loader that reads templates from Python packages.

    Args:
        package: Import name of a package containing Liquid templates.
        package_path: One or more directories in the package containing Liquid
            templates.
        encoding: Encoding of template files.
        ext: A default file extension to use if one is not provided. Should
            include a leading period.
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
            raise TemplateNotFoundError(template_name)

        # Add suffix self.ext if template name does not have a suffix.
        if not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        for path in self.paths:
            source_path = path.joinpath(str(template_path))
            if source_path.is_file():
                # MyPy seems to think source_path has `Any` type :(
                return source_path  # type: ignore

        raise TemplateNotFoundError(template_name)

    def get_source(
        self,
        env: Environment,  # noqa: ARG002
        template_name: str,
        *,
        context: Optional[RenderContext] = None,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> TemplateSource:
        """Get source information for a template."""
        source_path = self._resolve_path(template_name)
        return TemplateSource(
            text=source_path.read_text(self.encoding),
            name=str(source_path),
            uptodate=None,
        )

    async def get_source_async(
        self,
        env: Environment,  # noqa: ARG002
        template_name: str,
        *,
        context: Optional[RenderContext] = None,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> TemplateSource:
        """Get source information for a template."""
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
            text=source_text,
            name=str(source_path),
            uptodate=None,
        )
