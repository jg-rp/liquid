"""A template loader that delegates to other template loaders."""
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import List

from liquid.exceptions import TemplateNotFound

from .base_loader import BaseLoader
from .mixins import CachingLoaderMixin

if TYPE_CHECKING:
    from liquid import Context
    from liquid import Environment

    from .base_loader import TemplateSource


class ChoiceLoader(BaseLoader):
    """A template loader that will try each of a list of loaders in turn.

    Args:
        loaders: A list of loaders implementing `liquid.loaders.BaseLoader`.
    """

    def __init__(self, loaders: List[BaseLoader]):
        super().__init__()
        self.loaders = loaders

    def get_source(self, env: Environment, template_name: str) -> TemplateSource:
        """Get source code for a template from one of the configured loaders."""
        for loader in self.loaders:
            try:
                return loader.get_source(env, template_name)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)

    async def get_source_async(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        """An async version of `get_source`."""
        for loader in self.loaders:
            try:
                return await loader.get_source_async(env, template_name)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)

    def get_source_with_args(
        self,
        env: Environment,
        template_name: str,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source code for a template from one of the configured loaders."""
        for loader in self.loaders:
            try:
                return loader.get_source_with_args(env, template_name, **kwargs)
            except TemplateNotFound:
                pass

        # TODO: include arguments in TemplateNotFound exception.
        raise TemplateNotFound(template_name)

    async def get_source_with_args_async(
        self,
        env: Environment,
        template_name: str,
        **kwargs: object,
    ) -> TemplateSource:
        """An async version of `get_source_with_args`."""
        for loader in self.loaders:
            try:
                return await loader.get_source_with_args_async(
                    env, template_name, **kwargs
                )
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)

    def get_source_with_context(
        self, context: Context, template_name: str, **kwargs: str
    ) -> TemplateSource:
        """Get source code for a template from one of the configured loaders."""
        for loader in self.loaders:
            try:
                return loader.get_source_with_context(context, template_name, **kwargs)
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)

    async def get_source_with_context_async(
        self, context: Context, template_name: str, **kwargs: str
    ) -> TemplateSource:
        """Get source code for a template from one of the configured loaders."""
        for loader in self.loaders:
            try:
                return await loader.get_source_with_context_async(
                    context, template_name, **kwargs
                )
            except TemplateNotFound:
                pass

        raise TemplateNotFound(template_name)


class CachingChoiceLoader(CachingLoaderMixin, ChoiceLoader):
    """A `ChoiceLoader` that caches parsed templates in memory.

    Args:
        loaders: A list of loaders implementing `liquid.loaders.BaseLoader`.
        auto_reload: If `True`, automatically reload a cached template if it has been
            updated.
        namespace_key: The name of a global render context variable or loader keyword
            argument that resolves to the current loader "namespace" or "scope".
        cache_size: The maximum number of templates to hold in the cache before removing
            the least recently used template.

    _New in version 1.11.0._
    """

    def __init__(
        self,
        loaders: List[BaseLoader],
        *,
        auto_reload: bool = True,
        namespace_key: str = "",
        cache_size: int = 300,
    ):
        super().__init__(
            auto_reload=auto_reload,
            namespace_key=namespace_key,
            cache_size=cache_size,
        )

        ChoiceLoader.__init__(self, loaders)
