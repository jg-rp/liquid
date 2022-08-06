"""Liquid template definition."""
from __future__ import annotations

import re

from collections import abc
from collections import Counter
from collections import defaultdict

from io import StringIO
from pathlib import Path

from typing import Awaitable
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import TextIO
from typing import Tuple
from typing import Union
from typing import TYPE_CHECKING

from liquid.ast import ChildNode
from liquid.ast import Node

from liquid.context import Context
from liquid.context import VariableCaptureContext
from liquid.context import ReadOnlyChainMap

from liquid.exceptions import TemplateTraversalError, LiquidInterrupt
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import Error
from liquid.exceptions import TemplateNotFound

from liquid.expression import Expression, StringLiteral
from liquid.expression import Identifier
from liquid.expression import Literal

from liquid.output import LimitedStringIO


if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid.ast import ParseTree
    from liquid.loaders import UpToDate


class BoundTemplate:
    """A liquid template that has been parsed and is bound to a
    :class:`liquid.Environment`.

    You probably don't want to instantiate :class:`BoundTemplate` directly. Use
    :meth:`liquid.Environment.from_string` or :meth:`liquid.Environment.get_template`
    instead.

    :param env: The environment this template is bound to.
    :type env: liquid.Environment
    :param parse_tree: The parse tree representing this template.
    :type parse_tree: liquid.ast.ParseTree
    :param name: Optional name of the template. Defaults to an empty string.
    :type name: Optional[str]
    :param path: Optional origin path or identifier for the template.
    :type path: Optional[Union[str, Path]]
    :param globals: An optional mapping of context variables made available every
        time the resulting template is rendered. Defaults to ``None``.
    :type globals: Optional[Dict[str, object]]
    :param matter: Optional mapping containing variables associated with the template.
        Could be "front matter" or other meta data.
    :type matter: Optional[Mapping[str, object]]
    :param uptodate: Optional callable that will return ``True`` if the template is up
        to date, or ``False`` if it needs to be reloaded. Defaults to ``None``.
    :type uptodate: Optional[Callable[[], bool]]
    """

    # Subclass `BoundTemplate` and override `context_class` to use a subclass of
    # `Context` when rendering templates.
    context_class = Context
    capture_context_class = VariableCaptureContext

    # pylint: disable=redefined-builtin, too-many-arguments
    def __init__(
        self,
        env: Environment,
        parse_tree: ParseTree,
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Dict[str, object]] = None,
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

        Accepts the same arguments as the :class:`dict` constructor.
        """
        context = self.context_class(
            self.env, globals=self.make_globals(dict(*args, **kwargs))
        )
        buf = self._get_buffer()
        self.render_with_context(context, buf)
        return buf.getvalue()

    async def render_async(self, *args: Any, **kwargs: Any) -> str:
        """An async version of :meth:`liquid.template.BoundTemplate.render`."""
        context = self.context_class(
            self.env, globals=self.make_globals(dict(*args, **kwargs))
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

        ``args`` and ``kwargs`` are passed to the :class:`dict` constructor. The
        resulting dictionary is added to the render context.

        :param context: A render context.
        :param buffer: File-like object to which rendered text is written.
        :param partial: If `True`, indicates that the current template has been
            included using either a "render" or "include" tag. Defaults to ``False``.
        :param block_scope: If `True`, indicates that assigns, breaks and continues
            from this template will not leak into the parent context. Defaults to
            ``False``.
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
                except Error as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, linenum=node.token().linenum)

    @property
    def is_up_to_date(self) -> bool:
        """False if the template was modified since it was last parsed,
        True otherwise."""
        if not self.uptodate:
            return True

        uptodate = self.uptodate()
        if not isinstance(uptodate, bool):
            raise Error(
                f"expected a boolean from uptodate, found {type(uptodate).__name__}"
            )
        return uptodate

    async def is_up_to_date_async(self) -> bool:
        """An async version of the ``is_up_to_date`` property.

        If ``template.uptodate`` is a coroutine, it wil be awaited. Otherwise it will be
        called just like ``is_up_to_date``
        """
        if not self.uptodate:
            return True

        uptodate = self.uptodate()
        if isinstance(uptodate, Awaitable):
            return await uptodate
        return uptodate

    def make_globals(self, render_args: Mapping[str, object]) -> Mapping[str, object]:
        """Return a mapping aggregated from render arguments, template globals and
        matter variables."""
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
        """Return a namespace dictionary. This is used by `render_with_context` to
        extend an existing context."""
        return {**render_args, "partial": partial}

    def __repr__(self) -> str:
        return (
            f"Template(name='{self.name}', "
            f"path='{self.path}', uptodate={self.is_up_to_date})"
        )  # pragma: no cover

    def analyze(
        self, follow_partials: bool = True, raise_for_failures: bool = True
    ) -> TemplateAnalysis:
        """Statically analyze this template and any included/rendered templates.

        Currently we only analyze references to template variables.

        :param follow_partials: If ``True``, we will try to load partial templates and
            analyze those templates too. Default's to ``True``.
        :type follow_partials: bool
        :param raise_for_failures: If ``True``, will raise an exception if an
            ``ast.Node`` or ``expression.Expression`` does not define a ``children()``
            method, or if a partial template can not be loaded. When ``False``, no
            exception is raised and a mapping of failed nodes and expressions is
            available as the ``failed_visits`` property. A mapping of unloadable partial
            templates is stored in the ``unloadable_partials`` property.
        :type raised_for_failed_visits: bool
        :returns: A object containing analysis results.
        :rtype: :class:`liquid.template.TemplateAnalysis`
        """
        refs = _TemplateVariableCounter(
            self,
            follow_partials=follow_partials,
            raise_for_failures=raise_for_failures,
        ).analyze()

        return TemplateAnalysis(
            variables=dict(refs.variables),
            local_variables=dict(refs.template_locals),
            global_variables=dict(refs.template_globals),
            failed_visits=dict(refs.failed_visits),
            unloadable_partials=dict(refs.unloadable_partials),
        )

    async def analyze_async(
        self, follow_partials: bool = True, raise_for_failures: bool = True
    ) -> TemplateAnalysis:
        """An async version of :meth:`analyze`."""
        refs = await _TemplateVariableCounter(
            self,
            follow_partials=follow_partials,
            raise_for_failures=raise_for_failures,
        ).analyze_async()

        return TemplateAnalysis(
            variables=dict(refs.variables),
            local_variables=dict(refs.template_locals),
            global_variables=dict(refs.template_globals),
            failed_visits=dict(refs.failed_visits),
            unloadable_partials=dict(refs.unloadable_partials),
        )

    def analyze_with_context(
        self, *args: Any, **kwargs: Any
    ) -> ContextualTemplateAnalysis:
        """Analyze a path through this template's syntax tree given some context data.

        Unlike :meth:`analyze`, this form of template analysis does perform a render,
        capturing template variables as we go.

        Python Liquid does not currently support template introspection from within a
        render context or ``Expression`` object. Meaning line numbers and template names
        are not available. Only variable names are reported along with the number of
        times they were referenced.

        It's also, using this method, not currently possible to detect names added to a
        block's scope. For example, ``forloop.index`` will be included in the results
        object if referenced within a ``for`` loop block.

        Accepts the same arguments as :meth:`render`.

        :returns: Contextual analysis results.
        :rtype: :class:`liquid.template.ContextualTemplateAnalysis`
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
        )

    async def analyze_with_context_async(
        self, *args: Any, **kwargs: Any
    ) -> ContextualTemplateAnalysis:
        """An async version of :meth:`analyze_with_context`."""
        context = self.capture_context_class(
            self.env, globals=self.make_globals(dict(*args, **kwargs))
        )
        buf = self._get_buffer()
        await self.render_with_context_async(context, buf)
        return ContextualTemplateAnalysis(
            all_variables=dict(Counter(context.all_references)),
            local_variables=dict(Counter(context.local_references)),
            undefined_variables=dict(Counter(context.undefined_references)),
        )


class AwareBoundTemplate(BoundTemplate):
    """A `BoundTemplate` subclass that automatically includes a `TemplateDrop` in the
    global namespace."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.drop = TemplateDrop(self.name, self.path)

    def make_partial_namespace(
        self,
        partial: bool,
        render_args: Mapping[str, object],
    ) -> abc.Mapping[str, object]:
        return {
            "template": self.drop,
            **super().make_partial_namespace(partial, render_args),
        }


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


RE_SPLIT_IDENT = re.compile(r"(\.|\[)")

Refs = Dict[str, List[Tuple[str, int]]]
ReferenceMap = DefaultDict[str, List[Tuple[str, int]]]


# pylint: disable=too-few-public-methods
class ContextualTemplateAnalysis:
    """The result of analyzing a template's variables using
    :meth:`BoundTemplate.analyze_with_context`.

    Each of the following properties is a dictionary mapping variable names to the
    number of times that variable was referenced.

    :ivar all_variables: All variables references along a path through the template's
        syntax tree.
    :ivar local_variables: The names of variables assigned using the built-in ``assign``
        ``capture``, ``increment`` or ``decrement`` tags, or any custom tag that uses
        ``Context.assign()``.
    :ivar undefined_variables: The names of variables that could not be resolved. If a
        name is referenced before it is assigned, it will appear in ``undefined`` and
        ``assigns``.
    """

    __slots__ = ("all_variables", "local_variables", "undefined_variables")

    def __init__(
        self,
        *,
        all_variables: Dict[str, int],
        local_variables: Dict[str, int],
        undefined_variables: Dict[str, int],
    ) -> None:
        self.all_variables = all_variables
        self.local_variables = local_variables
        self.undefined_variables = undefined_variables


# pylint: disable=too-few-public-methods
class TemplateAnalysis:
    """The result of analyzing a template's variables using
    :meth:`BoundTemplate.analyze`.

    Each of the following properties is a dictionary mapping variable names to a list of
    two-tuples. Each tuple holds the location of a reference to the name as (<template
    name>, <line number>). If a name is referenced multiple times, it will appear
    multiple times in the list. If a name is referenced before it is "assigned", it will
    appear in ``local_variables`` and ``global_variables``.

    :ivar variables: All referenced variables, whether they are in scope or not.
        Including references to names such as ``forloop`` from the ``for`` tag.
    :ivar local_variables: Template variables that are added to the template local
        scope, whether they are subsequently used or not.
    :ivar global_variables: Template variables that, on the given line number and
        "file", are out of scope or are assumed to be "global". That is, expected to be
        included by the application developer rather than a template author.
    :ivar failed_visits: Names of AST ``Node`` and ``Expression`` objects that could not
        be visited, probably because they do not implement a ``children`` method.
    :ivar unloadable_partials: Names or identifiers of partial templates that could not
        be loaded. This will be empty if ``follow_partials`` is ``False``.
    """

    __slots__ = (
        "variables",
        "local_variables",
        "global_variables",
        "failed_visits",
        "unloadable_partials",
    )

    def __init__(
        self,
        *,
        variables: Refs,
        local_variables: Refs,
        global_variables: Refs,
        failed_visits: Refs,
        unloadable_partials: Refs,
    ) -> None:
        self.variables = variables
        self.local_variables = local_variables
        self.global_variables = global_variables
        self.failed_visits = failed_visits
        self.unloadable_partials = unloadable_partials


# pylint: disable=too-many-instance-attributes
class _TemplateVariableCounter:
    """Count references to variable names in a Liquid template.

    :param template: The Liquid template to analyze.
    :type template: liquid.BoundTemplate
    :param follow_partials: If ``True``, the reference counter will try to load partial
        templates and count variable references in those partials too. Default's to
        ``True``.
    :type follow_partials: bool
    :param raise_for_failures: If ``True``, will raise an exception if an ``ast.Node``
        or ``expression.Expression`` does not define a ``children()`` method, or if a
        partial template can not be loaded.

        When ``False``, no exception is raised and a mapping of failed nodes/expressions
        is available as the ``failed_visits`` property. A mapping of unloadable partial
        templates are stored in the ``unloadable_partials`` property.
    :type: raised_for_failed_visits: bool
    """

    def __init__(
        self,
        template: BoundTemplate,
        *,
        follow_partials: bool = True,
        raise_for_failures: bool = True,
        scope: Optional[ReadOnlyChainMap] = None,
        template_locals: Optional[ReferenceMap] = None,
        partials: Optional[List[Tuple[str, Optional[Dict[str, str]]]]] = None,
    ) -> None:
        self.template = template
        self._template_name = self.template.name or "<string>"

        self.follow_partials = follow_partials
        self.raise_for_failures = raise_for_failures

        # Names that are added to the template "local" scope.
        self.template_locals: ReferenceMap = (
            template_locals if template_locals is not None else defaultdict(list)
        )
        # Names that are referenced but are not in the template local scope
        self.template_globals: ReferenceMap = defaultdict(list)
        # Names that are referenced by a Liquid expression.
        self.variables: ReferenceMap = defaultdict(list)

        # Nodes and Expressions that don't implement a `children()` method.
        self.failed_visits: ReferenceMap = defaultdict(list)

        # Tags that load templates with an expression that can not be analyzed
        # statically.
        self.unloadable_partials: ReferenceMap = defaultdict(list)

        # Block scoped names.
        self._scope = scope if scope is not None else ReadOnlyChainMap()

        # Partial templates (include, render, etc.)
        self._partials = partials if partials is not None else []

        # get_template_with_context requires a `Context`.
        self._empty_context = Context(self.template.env)

    def analyze(self) -> _TemplateVariableCounter:
        """Traverse the template's syntax tree and count variables as we go.

        It is not safe to call this method multiple times.
        """
        for node in self.template.tree.statements:
            self._analyze(node)

        self._raise_for_failures()
        return self

    async def analyze_async(self) -> _TemplateVariableCounter:
        """An async version of :meth:`_TemplateVariableCounter.analyze`"""
        for node in self.template.tree.statements:
            await self._analyze_async(node)

        self._raise_for_failures()
        return self

    def _analyze(self, root: Node) -> None:
        try:
            children = root.children()
        except NotImplementedError:
            name = root.__class__.__name__
            self.failed_visits[name].append((self._template_name, root.token().linenum))
            return

        for child in children:
            self._analyze_child(child)

            if child.block_scope:
                self._scope.push({n: None for n in child.block_scope})

            if self.follow_partials:
                if child.load_mode == "include":
                    self._analyze_include(child)
                elif child.load_mode == "render":
                    self._analyze_render(child)
                elif child.load_mode is not None:
                    raise TemplateTraversalError(
                        f"unknown load mode '{child.load_mode}'"
                    )

            # Recurse
            if child.node:
                self._analyze(child.node)

            if child.block_scope:
                self._scope.pop()

    async def _analyze_async(self, root: Node) -> None:
        try:
            children = root.children()
        except NotImplementedError:
            name = root.__class__.__name__
            self.failed_visits[name].append((self._template_name, root.token().linenum))
            return

        for child in children:
            self._analyze_child(child)

            if child.block_scope:
                self._scope.push({n: None for n in child.block_scope})

            if self.follow_partials:
                if child.load_mode == "include":
                    await self._analyze_include_async(child)
                elif child.load_mode == "render":
                    await self._analyze_render_async(child)
                elif child.load_mode is not None:
                    raise TemplateTraversalError(
                        f"unknown load mode '{child.load_mode}'"
                    )

            # Recurse
            if child.node:
                await self._analyze_async(child.node)

            if child.block_scope:
                self._scope.pop()

    def _analyze_child(self, child: ChildNode) -> None:
        if child.expression:
            try:
                refs = self._analyze_expression(child.expression)
            except NotImplementedError:
                name = child.expression.__class__.__name__
                self.failed_visits[name].append((self._template_name, child.linenum))
                return

            for ref in refs:
                self.variables[ref].append((self._template_name, child.linenum))

            # Check refs that are not in scope or in the local namespace before
            # pushing the next block scope. This should highlight names that are
            # expected to be "global".
            for ref in refs:
                _ref = RE_SPLIT_IDENT.split(ref, 1)[0]
                if _ref not in self._scope and _ref not in self.template_locals:
                    self.template_globals[ref].append(
                        (self._template_name, child.linenum)
                    )

        if child.template_scope:
            for name in child.template_scope:
                self.template_locals[name].append((self._template_name, child.linenum))

    def _analyze_expression(self, expression: Expression) -> List[str]:
        """Return a list of references used in the given expression."""
        refs: List[str] = []

        if isinstance(expression, Identifier):
            refs.append(str(expression))

        for expr in expression.children():
            refs.extend(self._analyze_expression(expr))

        return refs

    def _analyze_include(self, child: ChildNode) -> None:
        name, load_context = self._include_context(child)
        if name is None or load_context is None:
            return

        try:
            template = self._empty_context.get_template_with_context(
                name, **load_context
            )
        except TemplateNotFound:
            self.unloadable_partials[name].append((self._template_name, child.linenum))
            return

        # Partial templates rendered in "include" mode share the same template local
        # namespace as their parent template. Note that block scoped variables have
        # already been pushed and will be popped by the caller.
        refs = _TemplateVariableCounter(
            template,
            follow_partials=self.follow_partials,
            scope=self._scope,
            template_locals=self.template_locals,
            partials=self._partials,
        ).analyze()

        self._update_reference_counters(refs)

    async def _analyze_include_async(self, child: ChildNode) -> None:
        name, load_context = self._include_context(child)
        if name is None or load_context is None:
            return

        try:
            template = await self._empty_context.get_template_with_context_async(
                name, **load_context
            )
        except TemplateNotFound:
            self.unloadable_partials[name].append((self._template_name, child.linenum))
            return

        refs = await _TemplateVariableCounter(
            template,
            follow_partials=self.follow_partials,
            scope=self._scope,
            template_locals=self.template_locals,
            partials=self._partials,
        ).analyze_async()

        self._update_reference_counters(refs)

    def _include_context(
        self, child: ChildNode
    ) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        # Partial templates rendered in "include" mode might use a variable template
        # name. We can't statically analyze a partial template unless it's name is a
        # literal string (or possibly an integer, but unlikely).
        if not isinstance(child.expression, Literal):
            key = str(child.expression)
            self.unloadable_partials[key].append((self._template_name, child.linenum))
            return None, None

        name = str(child.expression.value)
        load_context = child.load_context or {}

        # Keep track of partial templates that have already been analyzed. This prevents
        # us from analysing the same template twice and protects us against recursive
        # includes/renders.
        if (name, load_context) in self._partials:
            return None, None

        self._partials.append((name, load_context))
        return (name, load_context)

    def _analyze_render(self, child: ChildNode) -> None:
        name, load_context = self._render_context(child)
        if name is None or load_context is None:
            return

        try:
            template = self._empty_context.get_template_with_context(
                name, **load_context
            )
        except TemplateNotFound:
            self.unloadable_partials[name].append((self._template_name, child.linenum))
            return

        # Partial templates rendered in "render" mode do not share the parent template
        # local namespace. We do not pass the current block scope stack to "rendered"
        # templates either.
        scope = {n: None for n in child.block_scope} if child.block_scope else {}
        refs = _TemplateVariableCounter(
            template,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap(scope),
            partials=self._partials,
        ).analyze()

        self._update_reference_counters(refs)

    async def _analyze_render_async(self, child: ChildNode) -> None:
        name, load_context = self._render_context(child)
        if name is None or load_context is None:
            return None

        try:
            template = await self._empty_context.get_template_with_context_async(
                name, **load_context
            )
        except TemplateNotFound:
            self.unloadable_partials[name].append((self._template_name, child.linenum))
            return

        # Partial templates rendered in "render" mode do not share the parent template
        # local namespace. We do not pass the current block scope stack to "rendered"
        # templates either.
        scope = {n: None for n in child.block_scope} if child.block_scope else {}
        refs = await _TemplateVariableCounter(
            template,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap(scope),
            partials=self._partials,
        ).analyze_async()

        self._update_reference_counters(refs)

    def _render_context(
        self, child: ChildNode
    ) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        if not isinstance(child.expression, StringLiteral):
            raise TemplateTraversalError(
                "can't load from a variable expression when in 'render' mode"
            )

        name = child.expression.value
        load_context = child.load_context or {}

        # Keep track of partial templates that have already been analyzed. This prevents
        # us from analysing the same template twice and protects us against recursive
        # includes/renders.
        if (name, load_context) in self._partials:
            return None, None

        self._partials.append((name, load_context))
        return name, load_context

    def _update_reference_counters(self, refs: _TemplateVariableCounter) -> None:
        # Accumulate references from the partial/child template into its parent.
        for _name, _refs in refs.variables.items():
            self.variables[_name].extend(_refs)

        for _name, _refs in refs.template_globals.items():
            self.template_globals[_name].extend(_refs)

        for _name, _refs in refs.failed_visits.items():
            self.failed_visits[_name].extend(_refs)

        for _name, _refs in refs.unloadable_partials.items():
            self.unloadable_partials[_name].extend(_refs)

    def _raise_for_failures(self) -> None:
        if self.raise_for_failures and self.failed_visits:
            msg_target = next(iter(self.failed_visits.keys()))
            if len(self.failed_visits) > 1:
                msg = (
                    f"{msg_target} (+{len(self.failed_visits) -1} more) "
                    "does not implement a 'children' method"
                )
            else:
                msg = f"{msg_target} does not implement a 'children' method"
            raise TemplateTraversalError(f"failed visit: {msg}")

        if self.raise_for_failures and self.unloadable_partials:
            msg_target = next(iter(self.unloadable_partials.keys()))
            if len(self.unloadable_partials) > 1:
                msg = (
                    f"partial template '{msg_target}' "
                    f"(+{len(self.unloadable_partials) -1} more) "
                    "could not be loaded"
                )
            else:
                msg = f"partial template '{msg_target}' could not be loaded"
            raise TemplateTraversalError(f"failed visit: {msg}")
