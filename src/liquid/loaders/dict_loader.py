from __future__ import annotations

from typing import TYPE_CHECKING

from .._loader import Loader, TemplateSource
from ..exceptions import TemplateNotFoundError

if TYPE_CHECKING:
    from .._context import RenderContext
    from ..environment import Environment


class DictLoader(Loader):
    def __init__(self, templates: dict[str, str]) -> None:
        super().__init__()
        self.templates = templates

    def get_source(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        if name not in self.templates:
            raise TemplateNotFoundError(name)
        return TemplateSource(name=name, text=self.templates[name])


# TODO: caching dict loader
