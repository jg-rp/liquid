"""Liquid template definition."""

from __future__ import annotations

from io import StringIO
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Awaitable
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import TextIO
from typing import Type
from typing import Union

from .context import FutureContext
from .context import RenderContext
from .exceptions import LiquidError
from .exceptions import LiquidInterrupt
from .exceptions import LiquidSyntaxError
from .exceptions import StopRender
from .output import LimitedStringIO
from .static_analysis import _analyze
from .static_analysis import _analyze_async
from .utils import ReadOnlyChainMap

if TYPE_CHECKING:
    from collections import abc

    from .ast import Node
    from .environment import Environment
    from .loader import UpToDate
    from .static_analysis import Segments
    from .static_analysis import TemplateAnalysis


__all__ = (
    "AwareBoundTemplate",
    "BoundTemplate",
    "FutureAwareBoundTemplate",
    "FutureBoundTemplate",
    "TemplateDrop",
)


class BoundTemplate:
    """A liquid template that has been parsed and is bound to a `liquid.Environment`.

    You probably don't want to instantiate `BoundTemplate` directly. Use
    `liquid.Environment.from_string()` or `liquid.Environment.get_template()`
    instead.

    Args:
        env: The environment this template is bound to.
        nodes: The parse tree representing this template.
        name: Optional name of the template. Defaults to an empty string.
        path: Optional origin path or identifier for the template.
        globals: An optional mapping of context variables made available every
            time the resulting template is rendered. Defaults to `None`.
        matter: Optional mapping containing variables associated with the template.
            Could be "front matter" or other meta data.
        uptodate: Optional callable that will return `True` if the template is up
            to date, or `False` if it needs to be reloaded. Defaults to `None`.
    """

    # Subclass `BoundTemplate` and override `context_class` to use a subclass of
    # `Context` when rendering templates.
    context_class: Type[RenderContext] = RenderContext

    def __init__(
        self,
        env: Environment,
        nodes: list[Node],
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        matter: Optional[Mapping[str, object]] = None,
        uptodate: UpToDate = None,
    ):
        self.env = env
        self.nodes = nodes
        self.globals = globals or {}
        self.matter = matter or {}
        self.name = name
        self.path = path
        self.uptodate = uptodate

    def __str__(self) -> str:
        return "".join(str(node) for node in self.nodes)

    def full_name(self) -> str:
        """Return this template's path, if available, joined with its name."""
        if self.path:
            path = Path(self.path)
            return str(path / self.name if not path.name else path)
        return self.name

    def render(self, *args: Any, **kwargs: Any) -> str:
        """Render the template with `args` and `kwargs` included in the render context.

        Accepts the same arguments as the `dict` constructor.
        """
        context = self.context_class(
            self,
            globals=self.make_globals(dict(*args, **kwargs)),
        )
        buf = self._get_buffer()
        self.render_with_context(context, buf)
        return buf.getvalue()

    async def render_async(self, *args: Any, **kwargs: Any) -> str:
        """An async version of `liquid.template.BoundTemplate.render`."""
        context = self.context_class(
            self,
            globals=self.make_globals(dict(*args, **kwargs)),
        )
        buf = self._get_buffer()
        await self.render_with_context_async(context, buf)
        return buf.getvalue()

    def _get_buffer(self) -> StringIO:
        if self.env.output_stream_limit is None:
            return StringIO()
        return LimitedStringIO(limit=self.env.output_stream_limit)

    def render_with_context(
        self,
        context: RenderContext,
        buffer: TextIO,
        *args: Any,
        partial: bool = False,
        block_scope: bool = False,
        **kwargs: Any,
    ) -> None:
        """Render the template using an existing context and output buffer.

        Args:
            context: A render context.
            buffer: File-like object to which rendered text is written.
            partial: If `True`, indicates that the current template has been
                included using either a "render" or "include" tag. Defaults to `False`.
            block_scope: If `True`, indicates that assigns, breaks and continues
                from this template will not leak into the parent context. Defaults to
                `False`.
            args: Passed to the `dict` constructor. The resulting dictionary is added to
                the render context.
            kwargs: Passed to the `dict` constructor. The resulting dictionary is added
                to the render context.
        """
        # "template" could get overridden from args/kwargs, "partial" will not.
        namespace = self.make_partial_namespace(partial, dict(*args, **kwargs))

        with context.extend(namespace=namespace):
            for node in self.nodes:
                try:
                    node.render(context, buffer)
                except LiquidInterrupt as err:
                    # If this is an "included" template, there could be a for loop
                    # in a parent template. A for loop that could be interrupted
                    # from an included template.
                    #
                    # Convert the interrupt to a syntax error if there is no parent.
                    if not partial or block_scope:
                        self.env.error(
                            LiquidSyntaxError(f"unexpected '{err}'", token=node.token)
                        )
                    else:
                        raise
                except StopRender:
                    break
                except LiquidError as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, token=node.token)

    async def render_with_context_async(
        self,
        context: RenderContext,
        buffer: TextIO,
        *args: Any,
        partial: bool = False,
        block_scope: bool = False,
        **kwargs: Any,
    ) -> None:
        """An async version of `render_with_context`."""
        # "template" could get overridden from args/kwargs, "partial" will not.
        namespace = self.make_partial_namespace(partial, dict(*args, **kwargs))

        with context.extend(namespace=namespace):
            for node in self.nodes:
                try:
                    await node.render_async(context, buffer)
                except LiquidInterrupt as err:
                    # If this is an "included" template, there could be a for loop
                    # in a parent template. A for loop that could be interrupted
                    # from an included template.
                    #
                    # Convert the interrupt to a syntax error if there is no parent.
                    if not partial or block_scope:
                        self.env.error(
                            LiquidSyntaxError(f"unexpected '{err}'", token=node.token)
                        )
                    else:
                        raise
                except StopRender:
                    break
                except LiquidError as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, token=node.token)

    def is_up_to_date(self) -> bool:
        """`False` if the template has bee modified, `True` otherwise."""
        if not self.uptodate:
            return True

        uptodate = self.uptodate()
        if not isinstance(uptodate, bool):
            raise LiquidError(
                f"expected a boolean from uptodate, found {type(uptodate).__name__}",
                token=None,
            )
        return uptodate

    async def is_up_to_date_async(self) -> bool:
        """An async version of the `is_up_to_date` property.

        If `template.uptodate` is a coroutine, it wil be awaited. Otherwise it will be
        called just like `is_up_to_date`
        """
        if not self.uptodate:
            return True

        uptodate = self.uptodate()
        if isinstance(uptodate, Awaitable):
            return await uptodate
        return uptodate

    def make_globals(self, render_args: Mapping[str, object]) -> Mapping[str, object]:
        """Return a mapping including render arguments and template globals."""
        return ReadOnlyChainMap(
            render_args,
            self.matter,
            self.globals,
        )

    def make_partial_namespace(
        self,
        partial: bool,
        render_args: Mapping[str, object],
    ) -> Mapping[str, object]:
        """Return a namespace dictionary.

        This is used by `render_with_context` to extend an existing context.
        """
        return {**render_args, "partial": partial}

    def analyze(self, *, include_partials: bool = True) -> TemplateAnalysis:
        """Statically analyze this template and any included/rendered templates.

        Args:
            include_partials: If `True`, we will try to load partial templates and
                analyze those templates too.
        """
        return _analyze(self, include_partials=include_partials)

    async def analyze_async(self, *, include_partials: bool = True) -> TemplateAnalysis:
        """An async version of `analyze`."""
        return await _analyze_async(self, include_partials=include_partials)

    def variables(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template without path segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See also [global_variables][liquid.BoundTemplate.global_variables].

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct _root segments_ for variables in this template.
        """
        return list(self.analyze(include_partials=include_partials).variables)

    async def variables_async(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template without path segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See also [global_variables][liquid.BoundTemplate.global_variables].

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct _root segments_ for variables in this template.
        """
        return list(
            (await self.analyze_async(include_partials=include_partials)).variables
        )

    def variable_paths(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template including all path segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See also [global_variable_paths][liquid.BoundTemplate.global_variable_paths].

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return list(
            {str(v) for v in chain.from_iterable(list(analysis.variables.values()))}
        )

    async def variable_paths_async(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template including all path segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See also [global_variable_paths][liquid.BoundTemplate.global_variable_paths].

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return list(
            {str(v) for v in chain.from_iterable(list(analysis.variables.values()))}
        )

    def variable_segments(self, *, include_partials: bool = True) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See [global_variable_segments][liquid.BoundTemplate.global_variable_segments].

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return [
            v.segments
            for v in set(chain.from_iterable(list(analysis.variables.values())))
        ]

    async def variable_segments_async(
        self, *, include_partials: bool = True
    ) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See [global_variable_segments][liquid.BoundTemplate.global_variable_segments].

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return [
            v.segments
            for v in set(chain.from_iterable(list(analysis.variables.values())))
        ]

    def global_variables(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template without path segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct _root segments_ for variables in this template.
        """
        return list(self.analyze(include_partials=include_partials).globals)

    async def global_variables_async(
        self, *, include_partials: bool = True
    ) -> list[str]:
        """Return a list of variables used in this template without path segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct _root segments_ for variables in this template.
        """
        return list(
            (await self.analyze_async(include_partials=include_partials)).globals
        )

    def global_variable_paths(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template including all path segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return list(
            {str(v) for v in chain.from_iterable(list(analysis.globals.values()))}
        )

    async def global_variable_paths_async(
        self, *, include_partials: bool = True
    ) -> list[str]:
        """Return a list of variables used in this template including all path segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return list(
            {str(v) for v in chain.from_iterable(list(analysis.globals.values()))}
        )

    def global_variable_segments(
        self, *, include_partials: bool = True
    ) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return [
            v.segments
            for v in set(chain.from_iterable(list(analysis.globals.values())))
        ]

    async def global_variable_segments_async(
        self, *, include_partials: bool = True
    ) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Args:
            include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return [
            v.segments
            for v in set(chain.from_iterable(list(analysis.globals.values())))
        ]

    def filter_names(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of filter names used in this template."""
        return list(self.analyze(include_partials=include_partials).filters)

    async def filter_names_async(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of filter names used in this template."""
        return list(
            (await self.analyze_async(include_partials=include_partials)).filters
        )

    def tag_names(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of tag names used in this template."""
        return list(self.analyze(include_partials=include_partials).tags)

    async def tag_names_async(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of tag names used in this template."""
        return list((await self.analyze_async(include_partials=include_partials)).tags)


class AwareBoundTemplate(BoundTemplate):
    """A `BoundTemplate` subclass with a `TemplateDrop` in the global namespace."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.drop = TemplateDrop(self.name, self.path)

    def make_partial_namespace(  # noqa: D102
        self,
        partial: bool,
        render_args: Mapping[str, object],
    ) -> abc.Mapping[str, object]:
        return {
            "template": self.drop,
            **super().make_partial_namespace(partial, render_args),
        }


class FutureBoundTemplate(BoundTemplate):
    """A `BoundTemplate` configured to use the `FutureContext` render context.

    See `liquid.future.Environment`.
    """

    context_class = FutureContext


class FutureAwareBoundTemplate(AwareBoundTemplate):
    """A `BoundTemplate` configured to use the `FutureContext` render context.

    Inserts a `TemplateDrop` into the global namespace automatically.

    See `liquid.future.Environment`.
    """

    context_class = FutureContext


class TemplateDrop(Mapping[str, Optional[str]]):
    """Template meta data mapping."""

    def __init__(self, name: str, path: Optional[Union[str, Path]]):
        self.name = name
        self.path = path

        if not self.path or isinstance(self.path, str):
            self.path = Path(self.name)

        self.stem = self.path.stem
        self.suffix: Optional[str] = None

        if "." in self.stem:
            self.suffix = self.stem.split(".")[-1]

        self._items = {
            "directory": self.path.parent.name,
            "name": self.path.name.split(".")[0],
            "suffix": self.suffix,
        }

    def __str__(self) -> str:
        return self.stem

    def __repr__(self) -> str:
        return (
            f"TemplateDrop(directory='{self['directory']}', "
            f"name='{self['name']}', suffix='{self['suffix']}')"
        )  # pragma: no cover

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __getitem__(self, key: object) -> Optional[str]:
        return self._items[str(key)]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)
