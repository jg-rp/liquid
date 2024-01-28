"""A template loader that delegates to other template loaders."""
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import List

from liquid.exceptions import TemplateNotFound

from .base_loader import BaseLoader
from .base_loader import TemplateSource

if TYPE_CHECKING:
    from liquid import Context
    from liquid import Environment


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
