from __future__ import annotations

from typing import TYPE_CHECKING

from .._loader import Loader, TemplateSource
from ..exceptions import TemplateNotFoundError
from .mixins import CachingLoaderMixin

if TYPE_CHECKING:
    from .._context import RenderContext
    from ..environment import Environment


class ChoiceLoader(Loader):
    """A template loader that delegates to other template loaders.

    Parameters
    ----------
    loaders
        A list of loaders implementing `liquid.Loader`.
    """

    def __init__(self, loaders: list[Loader]):
        super().__init__()
        self.loaders = loaders

    def get_source(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source information for a template."""
        for loader in self.loaders:
            try:
                return loader.get_source(env, name, context=context, **kwargs)
            except TemplateNotFoundError:
                pass

        raise TemplateNotFoundError(name)

    async def get_source_async(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source information for a template."""
        for loader in self.loaders:
            try:
                return await loader.get_source_async(
                    env, name, context=context, **kwargs
                )
            except TemplateNotFoundError:
                pass

        raise TemplateNotFoundError(name)


class CachingChoiceLoader(CachingLoaderMixin, ChoiceLoader):
    """A `ChoiceLoader` that caches parsed templates in memory.

    Parameters
    ----------
    loaders
        A list of loaders implementing `liquid.Loader`.
    auto_reload
        If ``True``, automatically reload a cached template if it has been updated.
    namespace_key
        The name of a global render context variable or loader keyword argument
        that resolves to the current loader "namespace" or "scope".
    capacity
        The maximum number of templates to hold in the cache before removing the
        least recently used template.
    """

    def __init__(
        self,
        loaders: list[Loader],
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
