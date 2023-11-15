"""Liquid template definition."""
from __future__ import annotations

from collections import Counter
from collections import abc
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Awaitable
from typing import Dict
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import TextIO
from typing import Union

from liquid.context import Context
from liquid.context import FutureContext
from liquid.context import FutureVariableCaptureContext
from liquid.context import ReadOnlyChainMap
from liquid.context import VariableCaptureContext
from liquid.exceptions import Error
from liquid.exceptions import LiquidInterrupt
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import StopRender
from liquid.output import LimitedStringIO
from liquid.static_analysis import ContextualTemplateAnalysis
from liquid.static_analysis import NameRefs
from liquid.static_analysis import ReferencedVariable
from liquid.static_analysis import Refs
from liquid.static_analysis import TemplateAnalysis
from liquid.static_analysis import _TemplateCounter

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.ast import ParseTree
    from liquid.loaders import UpToDate


__all__ = (
    "AwareBoundTemplate",
    "BoundTemplate",
    "ContextualTemplateAnalysis",
    "FutureAwareBoundTemplate",
    "FutureBoundTemplate",
    "NameRefs",
    "Refs",
    "ReferencedVariable",
    "TemplateAnalysis",
    "TemplateDrop",
)


class BoundTemplate:
    """A liquid template that has been parsed and is bound to a `liquid.Environment`.

    You probably don't want to instantiate `BoundTemplate` directly. Use
    `liquid.Environment.from_string()` or `liquid.Environment.get_template()`
    instead.

    Args:
        env: The environment this template is bound to.
        parse_tree: The parse tree representing this template.
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
    context_class = Context
    capture_context_class = VariableCaptureContext

    def __init__(
        self,
        env: Environment,
        parse_tree: ParseTree,
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Dict[str, object]] = None,  # noqa: A002
        matter: Optional[Mapping[str, object]] = None,
        uptodate: UpToDate = None,
    ):
        self.env = env
        self.tree = parse_tree
        self.globals = globals or {}
        self.matter = matter or {}
        self.name = name
        self.path = path
        self.uptodate = uptodate

    def render(self, *args: Any, **kwargs: Any) -> str:
        """Render the template with `args` and `kwargs` included in the render context.

        Accepts the same arguments as the `dict` constructor.
        """
        context = self.context_class(
            self.env,
            globals=self.make_globals(dict(*args, **kwargs)),
            template=self,
        )
        buf = self._get_buffer()
        self.render_with_context(context, buf)
        return buf.getvalue()

    async def render_async(self, *args: Any, **kwargs: Any) -> str:
        """An async version of `liquid.template.BoundTemplate.render`."""
        context = self.context_class(
            self.env,
            globals=self.make_globals(dict(*args, **kwargs)),
            template=self,
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
        context: Context,
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
            for node in self.tree.statements:
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
                            LiquidSyntaxError(
                                f"unexpected '{err}'", linenum=node.token().linenum
                            )
                        )
                    else:
                        raise
                except StopRender:
                    break
                except Error as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, linenum=node.token().linenum)

    async def render_with_context_async(
        self,
        context: Context,
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
            for node in self.tree.statements:
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
                            LiquidSyntaxError(
                                f"unexpected '{err}'", linenum=node.token().linenum
                            )
                        )
                    else:
                        raise
                except StopRender:
                    break
                except Error as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, linenum=node.token().linenum)

    @property
    def is_up_to_date(self) -> bool:
        """`False` if the template has bee modified, `True` otherwise."""
        if not self.uptodate:
            return True

        uptodate = self.uptodate()
        if not isinstance(uptodate, bool):
            raise Error(
                f"expected a boolean from uptodate, found {type(uptodate).__name__}"
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

    def __repr__(self) -> str:
        return f"Template(name='{self.name}', path='{self.path}')"  # pragma: no cover

    def analyze(
        self, follow_partials: bool = True, raise_for_failures: bool = True
    ) -> TemplateAnalysis:
        """Statically analyze this template and any included/rendered templates.

        Args:
            follow_partials: If `True`, we will try to load partial templates and
                analyze those templates too.
            raise_for_failures: If `True`, will raise an exception if an
                `ast.Node` or `expression.Expression` does not define a `children()`
                method, or if a partial template can not be loaded. When `False`, no
                exception is raised and a mapping of failed nodes and expressions is
                available as the `failed_visits` property. A mapping of unloadable
                partial templates is stored in the `unloadable_partials` property.
        """
        refs = _TemplateCounter(
            self,
            follow_partials=follow_partials,
            raise_for_failures=raise_for_failures,
        ).analyze()

        return TemplateAnalysis(
            variables={ReferencedVariable(k): v for k, v in refs.variables.items()},
            local_variables={
                ReferencedVariable(k): v for k, v in refs.template_locals.items()
            },
            global_variables={
                ReferencedVariable(k): v for k, v in refs.template_globals.items()
            },
            failed_visits=dict(refs.failed_visits),
            unloadable_partials=dict(refs.unloadable_partials),
            filters=dict(refs.filters),
            tags=dict(refs.tags),
        )

    async def analyze_async(
        self, follow_partials: bool = True, raise_for_failures: bool = True
    ) -> TemplateAnalysis:
        """An async version of `analyze`."""
        refs = await _TemplateCounter(
            self,
            follow_partials=follow_partials,
            raise_for_failures=raise_for_failures,
        ).analyze_async()

        return TemplateAnalysis(
            variables={ReferencedVariable(k): v for k, v in refs.variables.items()},
            local_variables={
                ReferencedVariable(k): v for k, v in refs.template_locals.items()
            },
            global_variables={
                ReferencedVariable(k): v for k, v in refs.template_globals.items()
            },
            failed_visits=dict(refs.failed_visits),
            unloadable_partials=dict(refs.unloadable_partials),
            filters=dict(refs.filters),
            tags=dict(refs.tags),
        )

    def analyze_with_context(
        self, *args: Any, **kwargs: Any
    ) -> ContextualTemplateAnalysis:
        """Analyze a path through this template's syntax tree given some context data.

        Unlike `analyze`, this form of template analysis does perform a render,
        capturing template variables as we go.

        Python Liquid does not currently support template introspection from within a
        render context or `Expression` object. Meaning line numbers and template names
        are not available. Only variable names are reported along with the number of
        times they were referenced.

        It's also, using this method, not currently possible to detect names added to a
        block's scope. For example, `forloop.index` will be included in the results
        object if referenced within a `for` loop block.

        Accepts the same arguments as `render`.
        """
        context = self.capture_context_class(
            self.env, globals=self.make_globals(dict(*args, **kwargs))
        )
        buf = self._get_buffer()
        self.render_with_context(context, buf)
        return ContextualTemplateAnalysis(
            all_variables=dict(Counter(context.all_references)),
            local_variables=dict(Counter(context.local_references)),
            undefined_variables=dict(Counter(context.undefined_references)),
            filters=dict(Counter(context.filters)),
        )

    async def analyze_with_context_async(
        self, *args: Any, **kwargs: Any
    ) -> ContextualTemplateAnalysis:
        """An async version of `analyze_with_context`."""
        context = self.capture_context_class(
            self.env, globals=self.make_globals(dict(*args, **kwargs))
        )
        buf = self._get_buffer()
        await self.render_with_context_async(context, buf)
        return ContextualTemplateAnalysis(
            all_variables=dict(Counter(context.all_references)),
            local_variables=dict(Counter(context.local_references)),
            undefined_variables=dict(Counter(context.undefined_references)),
            filters=dict(Counter(context.filters)),
        )


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
    capture_context_class = FutureVariableCaptureContext


class FutureAwareBoundTemplate(AwareBoundTemplate):
    """A `BoundTemplate` configured to use the `FutureContext` render context.

    Inserts a `TemplateDrop` into the global namespace automatically.

    See `liquid.future.Environment`.
    """

    context_class = FutureContext
    capture_context_class = FutureVariableCaptureContext


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
