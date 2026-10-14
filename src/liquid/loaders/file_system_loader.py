from __future__ import annotations

import asyncio
import os
from collections.abc import Iterable
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from .._loader import Loader, TemplateSource
from ..exceptions import TemplateNotFoundError

if TYPE_CHECKING:
    from liquid import Environment, RenderContext


class FileSystemLoader(Loader):
    """A loader that loads templates from one or more directories on a file system.

    Parameters
    ----------
    search_path
        One or more paths to search.
    encoding
        Encoding to use when opening files.
    ext
        A default file extension. Should include a leading period.
    reject_symlinks
        When ``True``, reject paths to symlinks that resolve to files outside the
        search path. Defaults to `False`.

    Raises
    ------
    ValueError
        If `ext` is not a valid suffix.
    """

    def __init__(
        self,
        search_path: str | Path | Iterable[str | Path],
        *,
        encoding: str = "utf-8",
        ext: str | None = None,
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

    def resolve_path(self, name: str) -> Path:
        template_path = Path(name)

        if not template_path.name:
            raise TemplateNotFoundError(name)

        if self.ext and not template_path.suffix:
            template_path = template_path.with_suffix(self.ext)

        if os.path.pardir in template_path.parts or template_path.is_absolute():
            raise TemplateNotFoundError(name)

        for base in self.search_path:
            source_path = base.joinpath(template_path)

            try:
                if not source_path.exists() or not source_path.is_file():
                    continue
            except OSError:
                # "File name too long", for example
                continue

            if self.reject_symlinks:
                try:
                    resolved = source_path.resolve(strict=False)
                    base_resolved = base.resolve(strict=False)
                except OSError:
                    continue

                if not resolved.is_relative_to(base_resolved):
                    continue

            return source_path

        raise TemplateNotFoundError(name)

    def _read(self, source_path: Path) -> tuple[str, float]:
        with source_path.open(encoding=self.encoding) as fd:
            source = fd.read()
        return source, source_path.stat().st_mtime

    def get_source(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source information for a template."""
        source_path = self.resolve_path(name)
        source, mtime = self._read(source_path)
        return TemplateSource(
            text=source,
            name=str(source_path),
            up_to_date=partial(self._uptodate, source_path, mtime),
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
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source information for a template."""
        loop = asyncio.get_running_loop()
        source_path = await loop.run_in_executor(None, self.resolve_path, name)
        source, mtime = await loop.run_in_executor(None, self._read, source_path)
        return TemplateSource(
            text=source,
            name=str(source_path),
            up_to_date=partial(self._uptodate_async, source_path, mtime),
        )
