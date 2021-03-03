"""Base class and file system implementation for loading template sources.

Modelled after Jinja2 template loaders.
See https://github.com/pallets/jinja/blob/master/src/jinja2/loaders.py
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from typing import NamedTuple
from typing import Callable
from typing import Mapping
from typing import Optional
from typing import TYPE_CHECKING

from liquid.template import Template
from liquid.exceptions import TemplateNotFound


if TYPE_CHECKING:
    from liquid import Environment


class TemplateSource(NamedTuple):
    source: str
    filename: str
    uptodate: Optional[Callable[[], bool]]


class BaseLoader(ABC):
    @abstractmethod
    def get_source(self, env: Environment, template_name: str) -> TemplateSource:
        """Get the template source, filename and reload helper for a template"""

    # pylint: disable=redefined-builtin
    def load(
        self,
        env: Environment,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> Template:
        """"""
        try:
            source, filename, uptodate = self.get_source(env, name)
        except Exception as err:
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source, globals=globals, name=name, path=Path(filename)
        )
        template.uptodate = uptodate
        return template


class FileSystemLoader(BaseLoader):
    def __init__(self, search_path: str):
        self.search_path = Path(search_path)

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        source_path = self.search_path.joinpath(template_name)

        if not source_path.exists():
            raise TemplateNotFound(str(source_path))

        with source_path.open() as fd:
            source = fd.read()

        mtime = source_path.stat().st_mtime

        return TemplateSource(
            source, str(source_path), lambda: mtime == source_path.stat().st_mtime
        )


class DictLoader(BaseLoader):
    def __init__(self, templates: Mapping[str, str]):
        self.templates = templates

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFound(template_name) from err

        return TemplateSource(source, template_name, None)
