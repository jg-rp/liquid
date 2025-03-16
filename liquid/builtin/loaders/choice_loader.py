"""A template loader that delegates to other template loaders."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from liquid.exceptions import TemplateNotFoundError
from liquid.loader import BaseLoader
from liquid.loader import TemplateSource

from .mixins import CachingLoaderMixin

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext


class ChoiceLoader(BaseLoader):
    """A template loader that delegates to other template loaders.

    Args:
        loaders: A list of loaders implementing `liquid.loaders.BaseLoader`.
    """

    def __init__(self, loaders: list[BaseLoader]):
        super().__init__()
        self.loaders = loaders

    def get_source(
        self,
        env: Environment,
        template_name: str,
        *,
        context: Optional[RenderContext] = None,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source information for a template."""
        for loader in self.loaders:
            try:
                return loader.get_source(env, template_name, context=context, **kwargs)
            except TemplateNotFoundError:
                pass

        raise TemplateNotFoundError(template_name)

    async def get_source_async(
        self,
        env: Environment,
        template_name: str,
        *,
        context: Optional[RenderContext] = None,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source information for a template."""
        for loader in self.loaders:
            try:
                return await loader.get_source_async(
                    env, template_name, context=context, **kwargs
                )
            except TemplateNotFoundError:
                pass

        raise TemplateNotFoundError(template_name)


class CachingChoiceLoader(CachingLoaderMixin, ChoiceLoader):
    """A `ChoiceLoader` that caches parsed templates in memory.

    Args:
        loaders: A list of loaders implementing `liquid.loaders.BaseLoader`.
        auto_reload: If `True`, automatically reload a cached template if it has been
            updated.
        namespace_key: The name of a global render context variable or loader keyword
            argument that resolves to the current loader "namespace" or "scope".
        capacity: The maximum number of templates to hold in the cache before removing
            the least recently used template.
    """

    def __init__(
        self,
        loaders: list[BaseLoader],
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

        ChoiceLoader.__init__(self, loaders)
