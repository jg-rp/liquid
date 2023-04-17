"""A template loader that delegates to other template loaders."""
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import List

from liquid.exceptions import TemplateNotFound

from .base_loader import BaseLoader
from .base_loader import TemplateSource

if TYPE_CHECKING:
    from liquid import Environment


class ChoiceLoader(BaseLoader):
    """A template loader that will try each of a list of loaders in turn.

    Args:
        loaders: A list of loaders implementing `liquid.loaders.BaseLoader`.
    """

    def __init__(self, loaders: List[BaseLoader]):
        super().__init__()
        self.loaders = loaders

    def get_source(  # noqa: D102
        self, env: Environment, template_name: str
    ) -> TemplateSource:
        for loader in self.loaders:
            try:
                return loader.get_source(env, template_name)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)

    async def get_source_async(  # noqa: D102
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        for loader in self.loaders:
            try:
                return await loader.get_source_async(env, template_name)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)
