"""Built-in file system loader."""

from __future__ import annotations

import asyncio
import os
from functools import partial
from pathlib import Path
from pathlib import PurePath
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional
from typing import Union

from liquid.exceptions import TemplateNotFoundError
from liquid.loader import BaseLoader
from liquid.loader import TemplateSource

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext


class FileSystemLoader(BaseLoader):
    """A loader that loads templates from one or more directories on the file system.

    Args:
        search_path: One or more paths to search.
        encoding: Encoding to use when opening files.
        ext: A default file extension. Should include a leading period.
        reject_symlinks: When `True`, reject paths to symlinks that resolve to files
            outside the search path. Defaults to `False`.

    Raise:
        ValueError if `ext` is not a valid suffix.
    """

    def __init__(
        self,
        search_path: Union[str, Path, Iterable[Union[str, Path]]],
        *,
        encoding: str = "utf-8",
        ext: Optional[str] = None,
        reject_symlinks: bool = False,
    ):
        super().__init__()
        if not isinstance(search_path, Iterable) or isinstance(search_path, str):
            search_path = [search_path]

        self.search_path = [Path(path) for path in search_path]
        self.encoding = encoding
        self.ext = ext
        self.reject_symlinks = reject_symlinks

        # Raise a ValueError early if `ext` is invalid.
        if ext:
            Path("x").with_suffix(ext)

    def resolve_path(self, template_name: str) -> Path:
        """Return a path to the template identified by _template_name_.

        If the search path is a list of paths, returns the first path where
        _template_name_ exists. If none of the search paths contain _template_name_, a
        _TemplateNotFound_ exception is raised.
        """
        template_path = PurePath(template_name)
        if template_path.anchor:
            template_path = PurePath(*template_path.parts[1:])

        if not template_path.name:
            raise TemplateNotFoundError(template_name)

        if self.ext and not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        if os.path.pardir in template_path.parts or template_path.is_absolute():
            raise TemplateNotFoundError(template_name)

        for base in self.search_path:
            base_resolved = base.resolve()
            source_path = (base_resolved / template_path).resolve()

            if not source_path.is_relative_to(base_resolved):
                continue

            if self.reject_symlinks:
                current = base_resolved
                for part in template_path.parts:
                    current /= part
                    if current.is_symlink():
                        continue

            if not source_path.is_file() or source_path.is_dir():
                continue

            # We don't want to expose a fully qualified path in error messages.
            return base / template_path

        raise TemplateNotFoundError(template_name)

    def _read(self, source_path: Path) -> tuple[str, float]:
        with source_path.open(encoding=self.encoding) as fd:
            source = fd.read()
        return source, source_path.stat().st_mtime

    def get_source(
        self,
        env: Environment,  # noqa: ARG002
        template_name: str,
        *,
        context: Optional[RenderContext] = None,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> TemplateSource:
        """Get source information for a template."""
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
        source_path = await loop.run_in_executor(None, self.resolve_path, template_name)
        source, mtime = await loop.run_in_executor(None, self._read, source_path)
        return TemplateSource(
            source, str(source_path), partial(self._uptodate_async, source_path, mtime)
        )
