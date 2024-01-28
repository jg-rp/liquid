"""Base template loader."""
from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Union

from liquid.exceptions import TemplateNotFound

if TYPE_CHECKING:
    from liquid import Context
    from liquid import Environment
    from liquid.template import BoundTemplate

# ruff: noqa: D102 D101

TemplateNamespace = Optional[Mapping[str, object]]
UpToDate = Union[Callable[[], bool], Callable[[], Awaitable[bool]], None]


class TemplateSource(NamedTuple):
    """A Liquid template source as returned by the `get_source` method of a `loader`.

    Attributes:
        source: The liquid template source code.
        filename: The liquid template file name or other string identifying its origin.
        uptodate: Optional callable that will return `True` if the template is up to
            date, or `False` if it needs to be reloaded.
        matter: Optional mapping containing variables associated with the template.
            Could be "front matter" or other meta data.
    """

    source: str
    filename: str
    uptodate: UpToDate
    matter: TemplateNamespace = None


class BaseLoader(ABC):  # noqa: B024
    """Base template loader from which all template loaders are derived.

    Attributes:
        caching_loader (bool): Indicates if this loader implements its own cache.
            Setting this sto `True` will cause the `Environment` to disable its cache
            when initialized with a caching loader.
    """

    caching_loader = False

    def get_source(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        """Get the template source, filename and reload helper for a template.

        Args:
            env: The `Environment` attempting to load the template source text.
            template_name: A name or identifier for a template's source text.
        """
        raise NotImplementedError("template loaders must implement a get_source method")

    async def get_source_async(
        self,
        env: Environment,
        template_name: str,
    ) -> TemplateSource:
        """An async version of `get_source`.

        The default implementation delegates to `get_source()`.
        """
        return self.get_source(env, template_name)

    def get_source_with_args(
        self,
        env: Environment,
        template_name: str,
        **kwargs: object,  # noqa: ARG002
    ) -> TemplateSource:
        """Get template source text, optionally referencing arbitrary keyword arguments.

        Keyword arguments can be useful for multi-user environments where you need to
        modify a template loader's search space for a given user.

        By default, this method delegates to `get_source`, ignoring any keyword
        arguments.

        _New in version 1.9.0._
        """
        return self.get_source(env, template_name)

    async def get_source_with_args_async(
        self, env: Environment, template_name: str, **kwargs: object
    ) -> TemplateSource:
        """An async version of `get_source_with_args`.

        _New in version 1.9.0._
        """
        return self.get_source_with_args(env, template_name, **kwargs)

    def get_source_with_context(
        self,
        context: Context,
        template_name: str,
        **kwargs: str,  # noqa: ARG002
    ) -> TemplateSource:
        """Get a template's source, optionally referencing a render context."""
        return self.get_source(context.env, template_name)

    async def get_source_with_context_async(
        self,
        context: Context,
        template_name: str,
        **kwargs: str,  # noqa: ARG002
    ) -> TemplateSource:
        """An async version of `get_source_with_context`."""
        return await self.get_source_async(context.env, template_name)

    def load(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        """Find and parse template source code.

        This is used internally by `liquid.Environment` to load template
        source text. `load()` delegates to `BaseLoader.get_source()`. Custom
        loaders would typically implement `get_source()` rather than overriding
        `load()`.
        """
        try:
            source, filename, uptodate, matter = self.get_source(env, name)
        except Exception as err:  # noqa: BLE001
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source,
            globals=globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
    ) -> BoundTemplate:
        """An async version of `load()`."""
        try:
            template_source = await self.get_source_async(env, name)
            source, filename, uptodate, matter = template_source
        except Exception as err:  # noqa: BLE001
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source,
            globals=globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    def load_with_args(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        """Load template source text, optionally referencing extra keyword arguments.

        Most custom loaders will want to override `get_source_with_args()` rather than
        this method. For example, you might want to override `load_with_args()` and
        `get_source_with_args()` when implementing a custom caching loader. Where cache
        handling happens in `load_*` methods.
        """
        try:
            source, filename, uptodate, matter = self.get_source_with_args(
                env, name, **kwargs
            )
        except Exception as err:  # noqa: BLE001
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source,
            globals=globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    async def load_with_args_async(
        self,
        env: Environment,
        name: str,
        globals: TemplateNamespace = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        """An async version of `load_with_args()`."""
        try:
            template_source = await self.get_source_with_args_async(env, name, **kwargs)
            source, filename, uptodate, matter = template_source
        except Exception as err:  # noqa: BLE001
            raise TemplateNotFound(name) from err

        template = env.from_string(
            source,
            globals=globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    def load_with_context(
        self,
        context: Context,
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """Load and parse a template, optionally referencing a render context."""
        try:
            source, filename, uptodate, matter = self.get_source_with_context(
                context, name, **kwargs
            )
        except Exception as err:  # noqa: BLE001
            raise TemplateNotFound(name) from err

        template = context.env.from_string(
            source,
            globals=context.globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template

    async def load_with_context_async(
        self,
        context: Context,
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """An async version of `load_with_context`."""
        try:
            (
                source,
                filename,
                uptodate,
                matter,
            ) = await self.get_source_with_context_async(context, name, **kwargs)
        except Exception as err:  # noqa: BLE001
            raise TemplateNotFound(name) from err

        template = context.env.from_string(
            source,
            globals=context.globals,
            name=name,
            path=Path(filename),
            matter=matter,
        )
        template.uptodate = uptodate
        return template


class DictLoader(BaseLoader):
    """A loader that loads templates from a dictionary.

    Args:
        templates: A dictionary mapping template names to template source strings.
    """

    def __init__(self, templates: Dict[str, str]):
        super().__init__()
        self.templates = templates

    def get_source(self, _: Environment, template_name: str) -> TemplateSource:
        try:
            source = self.templates[template_name]
        except KeyError as err:
            raise TemplateNotFound(template_name) from err

        return TemplateSource(source, template_name, None)
