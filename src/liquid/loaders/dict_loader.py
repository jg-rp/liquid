from __future__ import annotations

from typing import TYPE_CHECKING

from .._loader import Loader, TemplateSource
from ..exceptions import TemplateNotFoundError
from .mixins import CachingLoaderMixin

if TYPE_CHECKING:
    from .._context import RenderContext
    from ..environment import Environment


class DictLoader(Loader):
    """A template loader that reads source text from a dictionary."""

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


class CachingDictLoader(CachingLoaderMixin, DictLoader):
    """A ``DictLoader`` that caches parsed templates in memory."""

    def __init__(
        self,
        templates: dict[str, str],
        *,
        auto_reload: bool = True,
        namespace_key: str = "",
        capacity: int = 300,
    ):
        super().__init__(
            auto_reload=auto_reload,
            namespace_key=namespace_key,
            capacity=capacity,
        )

        DictLoader.__init__(self, templates)
