"""A template loader that loads templates from a dictionary of strings."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from liquid.exceptions import TemplateNotFoundError
from liquid.loader import BaseLoader
from liquid.loader import TemplateSource

from .mixins import CachingLoaderMixin

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.context import RenderContext


class DictLoader(BaseLoader):
    """A loader that loads templates from a dictionary.

    Args:
        templates: A dictionary mapping template names to template source strings.
    """

    def __init__(self, templates: dict[str, str]):
        super().__init__()
        self.templates = templates

    def get_source(
        self,
        env: Environment,  # noqa: ARG002
        template_name: str,
        *,
        context: Optional[RenderContext] = None,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> TemplateSource:
        """Get the source, filename and reload helper for a template."""
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFoundError(template_name) from err

        return TemplateSource(source, template_name, None)


class CachingDictLoader(CachingLoaderMixin, DictLoader):
    """A `DictLoader` that caches parsed templates in memory."""

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
