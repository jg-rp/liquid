"""Base class for all template loaders."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Awaitable
from typing import Callable
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Union

if TYPE_CHECKING:
    from .context import RenderContext
    from .environment import Environment
    from .template import BoundTemplate


class BaseLoader(ABC):
    """Base class for all template loaders."""

    @abstractmethod
    def get_source(
        self,
        env: Environment,
        template_name: str,
        *,
        context: Optional[RenderContext] = None,
        **kwargs: object,
    ) -> TemplateSource:
        """Get source information for a template.

        Args:
            env: The `Environment` attempting to load the template source text.
            template_name: A name or identifier for a template's source text.
            context: An optional render context that can be used to narrow the template
                source search space.
            kwargs: Arbitrary arguments that can be used to narrow the template source
                search space.
        """

    async def get_source_async(
        self,
        env: Environment,
        template_name: str,
        *,
        context: Optional[RenderContext] = None,
        **kwargs: object,
    ) -> TemplateSource:
        """An async version of `get_source`.

        The default implementation delegates to `get_source()`.
        """
        return self.get_source(env, template_name, context=context, **kwargs)

    def load(
        self,
        env: Environment,
        name: str,
        *,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        context: Optional[RenderContext] = None,
        **kwargs: object,
    ) -> BoundTemplate:
        """Find and parse template source code.

        Args:
            env: The `Environment` attempting to load the template source text.
            name: A name or identifier for a template's source text.
            globals: A mapping of render context variables attached to the
                resulting template.
            context: An optional render context that can be used to narrow the template
                source search space.
            kwargs: Arbitrary arguments that can be used to narrow the template source
                search space.
        """
        source, full_name, uptodate, matter = self.get_source(
            env, name, context=context, **kwargs
        )

        path = Path(full_name)

        template = env.from_string(
            source,
            name=path.name,
            path=path,
            globals=globals,
            matter=matter,
        )

        template.uptodate = uptodate
        return template

    async def load_async(
        self,
        env: Environment,
        name: str,
        *,
        globals: Union[Mapping[str, object], None] = None,  # noqa: A002
        context: Union[RenderContext, None] = None,
        **kwargs: object,
    ) -> BoundTemplate:
        """An async version of `load()`."""
        source, full_name, uptodate, matter = await self.get_source_async(
            env, name, context=context, **kwargs
        )

        template = env.from_string(
            source,
            name=name,
            path=Path(full_name),
            globals=globals,
            matter=matter,
        )

        template.uptodate = uptodate
        return template


UpToDate = Union[Callable[[], bool], Callable[[], Awaitable[bool]], None]


class TemplateSource(NamedTuple):
    """A Liquid template source as returned by the `get_source` method of a `loader`.

    Attributes:
        text: The liquid template source code.
        name: The liquid template file name or other string identifying its origin.
        uptodate: Optional callable that will return `True` if the template is up to
            date, or `False` if it needs to be reloaded.
        matter: Optional mapping containing variables associated with the template.
            Could be "front matter" or other meta data.
    """

    text: str
    name: str
    uptodate: Union[Callable[[], bool], Callable[[], Awaitable[bool]], None]
    matter: Union[dict[str, object], None] = None
