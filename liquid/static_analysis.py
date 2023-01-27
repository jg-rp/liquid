"""Analyze template variables, tags and filters by traversing a template's AST."""
from __future__ import annotations
import re

from collections import defaultdict

from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import TYPE_CHECKING

from typing_extensions import Literal

from liquid.ast import BlockNode
from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import ParseTree

from liquid.context import Context
from liquid.context import ReadOnlyChainMap

from liquid.exceptions import StopRender
from liquid.exceptions import TemplateInheritanceError
from liquid.exceptions import TemplateNotFound
from liquid.exceptions import TemplateTraversalError

from liquid.expression import Expression
from liquid.expression import FilteredExpression
from liquid.expression import Identifier
from liquid.expression import IdentifierPathElement
from liquid.expression import IdentifierTuple
from liquid.expression import StringLiteral

from liquid.extra.tags.extends import BlockNode as InheritanceBlockNode
from liquid.extra.tags.extends import _BlockStackItem
from liquid.extra.tags.extends import stack_blocks

from liquid.token import TOKEN_TAG

if TYPE_CHECKING:  # pragma: no cover
    from liquid import BoundTemplate

RE_SPLIT_IDENT = re.compile(r"(\.|\[)")


class ReferencedVariable(str):
    """A str subclass for variables found during static analysis that retains
    information about a variable's parts.
    """

    def __new__(cls, obj: object) -> ReferencedVariable:
        _str = super().__new__(cls, obj)
        _str.obj = obj
        return _str

    def __init__(self, _: object) -> None:
        super().__init__()
        self.obj: object
        if isinstance(self.obj, Identifier):
            self._parts = self.obj.as_tuple()
        else:
            self._parts = (str(self.obj),)

    @property
    def parts(self) -> IdentifierTuple:
        """A tuple representation of the variable's parts, which might contain
        nested tuples for nested variables. For example, the variable
        ``some[foo.bar[a.b]].other`` as a tuple would look like this:

            ("some", ("foo", "bar", ("a", "b")), "other.thing")
        """
        return self._parts


# (template_name, line_number).
Location = Tuple[str, int]

# A mapping of template variables to their (template_name, line_number) locations.
Refs = Dict[ReferencedVariable, List[Location]]

# A mapping of Identifier expressions to their (template_name, line_number) locations.
IdentifierMap = DefaultDict[Identifier, List[Location]]

# A mapping of template, tag or filter names to their (template_name, line_number)
# locations.
NameRefs = Dict[str, List[Location]]


# pylint: disable=too-few-public-methods
class ContextualTemplateAnalysis:
    """The result of analyzing a template's filters and variables using
    :meth:`BoundTemplate.analyze_with_context`.

    Each of the following properties is a dictionary mapping variable or filter names
    to the number of times that variable was referenced.

    :ivar all_variables: All variables references along a path through the template's
        syntax tree.
    :ivar local_variables: The names of variables assigned using the built-in ``assign``
        ``capture``, ``increment`` or ``decrement`` tags, or any custom tag that uses
        ``Context.assign()``.
    :ivar undefined_variables: The names of variables that could not be resolved. If a
        name is referenced before it is assigned, it will appear in ``undefined`` and
        ``assigns``.
    :ivar filters: Names of filters found during contextual analysis.
    """

    __slots__ = ("all_variables", "local_variables", "undefined_variables", "filters")

    def __init__(
        self,
        *,
        all_variables: Dict[str, int],
        local_variables: Dict[str, int],
        undefined_variables: Dict[str, int],
        filters: Dict[str, int],
    ) -> None:
        self.all_variables = all_variables
        self.local_variables = local_variables
        self.undefined_variables = undefined_variables
        self.filters = filters


# pylint: disable=too-few-public-methods
class TemplateAnalysis:
    """The result of analyzing a template's tags, filters and variables using
    :meth:`BoundTemplate.analyze`.

    Each of the following properties is a dictionary mapping variable, tag or filter
    names to a list of tuples. Each tuple holds the location of a reference to the name
    as (<template name>, <line number>). If a name is referenced multiple times, it will
    appear multiple times in the list. If a name is referenced before it is "assigned",
    it will appear in ``local_variables`` and ``global_variables``.

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
    :ivar filters: All filters found during static analysis.
    :ivar tags: All tags found during static analysis.
    """

    __slots__ = (
        "variables",
        "local_variables",
        "global_variables",
        "failed_visits",
        "unloadable_partials",
        "filters",
        "tags",
    )

    def __init__(
        self,
        *,
        variables: Refs,
        local_variables: Refs,
        global_variables: Refs,
        failed_visits: NameRefs,
        unloadable_partials: NameRefs,
        filters: NameRefs,
        tags: NameRefs,
    ) -> None:
        self.variables = variables
        self.local_variables = local_variables
        self.global_variables = global_variables
        self.failed_visits = failed_visits
        self.unloadable_partials = unloadable_partials
        self.filters = filters
        self.tags = tags


# pylint: disable=too-many-instance-attributes
class _TemplateCounter:
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
        template_locals: Optional[IdentifierMap] = None,
        partials: Optional[List[Tuple[str, Optional[Dict[str, str]]]]] = None,
    ) -> None:
        self.template = template
        self._template_name = self.template.name or "<string>"
        self.follow_partials = follow_partials
        self.raise_for_failures = raise_for_failures

        # Names that are added to the template "local" scope.
        self.template_locals: IdentifierMap = (
            template_locals if template_locals is not None else defaultdict(list)
        )

        # Names that are referenced but are not in the template local scope
        self.template_globals: IdentifierMap = defaultdict(list)

        # Names that are referenced by a Liquid expression.
        self.variables: IdentifierMap = defaultdict(list)

        # Tag and filter names.
        self.filters: NameRefs = defaultdict(list)
        self.tags: NameRefs = defaultdict(list)

        # Nodes and Expressions that don't implement a `children()` method.
        self.failed_visits: NameRefs = defaultdict(list)

        # Tags that load templates with an expression that can not be analyzed
        # statically.
        self.unloadable_partials: NameRefs = defaultdict(list)

        # Block scoped names.
        self._scope = scope if scope is not None else ReadOnlyChainMap()

        # Partial templates (include, render, etc.)
        self._partials = partials if partials is not None else []

        # get_template_with_context requires a `Context`.
        self._empty_context = Context(self.template.env)

    def analyze(self) -> _TemplateCounter:
        """Traverse the template's syntax tree and count variables as we go.

        It is not safe to call this method multiple times.
        """
        for node in self.template.tree.statements:
            try:
                self._analyze(node)
            except StopRender:
                break

        self._raise_for_failures()
        return self

    async def analyze_async(self) -> _TemplateCounter:
        """An async version of :meth:`_TemplateVariableCounter.analyze`"""
        for node in self.template.tree.statements:
            try:
                await self._analyze_async(node)
            except StopRender:
                break

        self._raise_for_failures()
        return self

    def _analyze(self, node: Node) -> None:
        self._count_tag(node)

        try:
            children = node.children()
        except NotImplementedError:
            name = node.__class__.__name__
            self.failed_visits[name].append((self._template_name, node.token().linenum))
            return

        for child in children:
            self._analyze_expression(child)
            self._expression_hook(child)
            self._update_template_scope(child)

            if child.block_scope:
                self._scope.push({n: None for n in child.block_scope})

            if self.follow_partials:
                if child.load_mode == "include":
                    self._analyze_include(child)
                elif child.load_mode == "render":
                    self._analyze_render(child)
                elif child.load_mode == "extends":
                    self._analyze_template_inheritance_chain(child, self.template)
                    raise StopRender("stop static analysis")
                elif child.load_mode is not None:
                    raise TemplateTraversalError(
                        f"unknown load mode '{child.load_mode}'"
                    )

            # Recurse
            if child.node:
                self._analyze(child.node)

            if child.block_scope:
                self._scope.pop()

    async def _analyze_async(self, node: Node) -> None:
        self._count_tag(node)

        try:
            children = node.children()
        except NotImplementedError:
            name = node.__class__.__name__
            self.failed_visits[name].append((self._template_name, node.token().linenum))
            return

        for child in children:
            self._analyze_expression(child)
            await self._async_expression_hook(child)
            self._update_template_scope(child)

            if child.block_scope:
                self._scope.push({n: None for n in child.block_scope})

            if self.follow_partials:
                if child.load_mode == "include":
                    await self._analyze_include_async(child)
                elif child.load_mode == "render":
                    await self._analyze_render_async(child)
                elif child.load_mode == "extends":
                    await self._analyze_template_inheritance_chain_async(
                        child, self.template
                    )
                    raise StopRender("stop static analysis")
                elif child.load_mode is not None:
                    raise TemplateTraversalError(
                        f"unknown load mode '{child.load_mode}'"
                    )

            # Recurse
            if child.node:
                await self._analyze_async(child.node)

            if child.block_scope:
                self._scope.pop()

    def _analyze_expression(self, child: ChildNode) -> None:
        if not child.expression:
            return

        try:
            refs = self._update_expression_refs(child.expression)
        except NotImplementedError:
            name = child.expression.__class__.__name__
            self.failed_visits[name].append((self._template_name, child.linenum))
            return

        for ref in refs.variable_references:
            self.variables[ref].append((self._template_name, child.linenum))

        # Check refs that are not in scope or in the local namespace before
        # pushing the next block scope. This should highlight names that are
        # expected to be "global".
        for ref in refs.variable_references:
            _ref = RE_SPLIT_IDENT.split(str(ref), 1)[0]
            if (
                _ref not in self._scope
                and Identifier(path=[IdentifierPathElement(_ref)])
                not in self.template_locals
            ):
                self.template_globals[ref].append((self._template_name, child.linenum))

        for f_ref in refs.filter_references:
            self.filters[f_ref].append((self._template_name, child.linenum))

    def _update_template_scope(self, child: ChildNode) -> None:
        if not child.template_scope:
            return

        for name in child.template_scope:
            self.template_locals[Identifier(path=[IdentifierPathElement(name)])].append(
                (self._template_name, child.linenum)
            )

    def _update_expression_refs(self, expression: Expression) -> References:
        """Return a list of references used in the given expression."""
        refs: References = References()

        if isinstance(expression, Identifier):
            refs.append_variable(expression)

        if isinstance(expression, FilteredExpression):
            refs.append_filters([f.name for f in expression.filters])

        for expr in expression.children():
            refs.extend(self._update_expression_refs(expr))

        return refs

    def _analyze_include(self, child: ChildNode) -> None:
        name, load_context = self._make_load_context(child, "include")
        if name is None or load_context is None:
            return

        try:
            template = self._get_template(
                name, load_context, self._template_name, child
            )
        except TemplateNotFound:
            return

        # Partial templates rendered in "include" mode share the same template local
        # namespace as their parent template. Note that block scoped variables have
        # already been pushed and will be popped by the caller.
        refs = _TemplateCounter(
            template,
            follow_partials=self.follow_partials,
            scope=self._scope,
            template_locals=self.template_locals,
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
        ).analyze()

        self._update_reference_counters(refs)

    async def _analyze_include_async(self, child: ChildNode) -> None:
        name, load_context = self._make_load_context(child, "include")
        if name is None or load_context is None:
            return

        try:
            template = await self._get_template_async(
                name, load_context, self._template_name, child
            )
        except TemplateNotFound:
            return

        refs = await _TemplateCounter(
            template,
            follow_partials=self.follow_partials,
            scope=self._scope,
            template_locals=self.template_locals,
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
        ).analyze_async()

        self._update_reference_counters(refs)

    def _analyze_render(self, child: ChildNode) -> None:
        name, load_context = self._make_load_context(child, "render")
        if name is None or load_context is None:
            return

        try:
            template = self._get_template(
                name, load_context, self._template_name, child
            )
        except TemplateNotFound:
            return

        # Partial templates rendered in "render" mode do not share the parent template
        # local namespace. We do not pass the current block scope stack to "rendered"
        # templates either.
        scope = {n: None for n in child.block_scope} if child.block_scope else {}
        refs = _TemplateCounter(
            template,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap(scope),
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
        ).analyze()

        self._update_reference_counters(refs)

    async def _analyze_render_async(self, child: ChildNode) -> None:
        name, load_context = self._make_load_context(child, "render")
        if name is None or load_context is None:
            return None

        try:
            template = await self._get_template_async(
                name, load_context, self._template_name, child
            )
        except TemplateNotFound:
            return

        scope = {n: None for n in child.block_scope} if child.block_scope else {}
        refs = await _TemplateCounter(
            template,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap(scope),
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
        ).analyze_async()

        self._update_reference_counters(refs)

    def _analyze_template_inheritance_chain(
        self, node: ChildNode, template: BoundTemplate
    ) -> None:
        name, load_context = self._make_load_context(node, "extends")
        if name is None or load_context is None:
            return

        stack_context = self._empty_context.copy({}, template=template)
        stack_context.tag_namespace["extends"] = defaultdict(list)

        # Guard against recursive `extends`.
        seen: Set[str] = set()

        # Add blocks from the leaf template to the stack context.
        extends_name, _ = self._stack_blocks(stack_context, template, count_tags=False)
        assert extends_name
        seen.add(extends_name)

        try:
            parent = self._get_template(name, load_context, self._template_name, node)
        except TemplateNotFound:
            return

        parent_template_name, _ = self._stack_blocks(stack_context, parent)

        if parent_template_name:
            if parent_template_name in seen:
                raise TemplateInheritanceError(
                    f"circular extends {parent_template_name!r}",
                    linenum=node.linenum,
                    filename=template.name,
                )
            seen.add(parent_template_name)

        while parent_template_name:
            try:
                parent = self._get_template(
                    parent_template_name, load_context, self._template_name, node
                )
            except TemplateNotFound:
                return

            parent_template_name, _ = self._stack_blocks(stack_context, parent)
            if parent_template_name:
                if parent_template_name in seen:
                    raise TemplateInheritanceError(
                        f"circular extends {parent_template_name!r}"
                    )
                seen.add(parent_template_name)

        refs = _InheritanceChainCounter(
            parent,
            stack_context,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap({"block": None}, self._scope),
            template_locals=self.template_locals,
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
        ).analyze()

        self._update_reference_counters(refs)

    async def _analyze_template_inheritance_chain_async(
        self, child: ChildNode, template: BoundTemplate
    ) -> None:
        name, load_context = self._make_load_context(child, "extends")
        if name is None or load_context is None:
            return

        stack_context = self._empty_context.copy({})
        stack_context.tag_namespace["extends"] = defaultdict(list)

        # Add blocks from the leaf template to the stack context.
        self._stack_blocks(stack_context, template, count_tags=False)

        try:
            parent = await self._get_template_async(
                name, load_context, self._template_name, child
            )
        except TemplateNotFound:
            return
        parent_template_name, _ = self._stack_blocks(stack_context, parent)

        while parent_template_name:
            try:
                parent = await self._get_template_async(
                    parent_template_name, load_context, self._template_name, child
                )
            except TemplateNotFound:
                return
            parent_template_name, _ = self._stack_blocks(stack_context, parent)

        refs = await _InheritanceChainCounter(
            parent,
            stack_context,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap({"block": None}, self._scope),
            template_locals=self.template_locals,
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
        ).analyze_async()

        self._update_reference_counters(refs)

    def _make_load_context(
        self, child: ChildNode, load_mode: Literal["extends", "include", "render"]
    ) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        # Partial templates rendered in "include" mode might use a variable template
        # name. We can't statically analyze a partial template unless it's name is a
        # literal string (or possibly an integer, but unlikely).
        if load_mode == "include" and not isinstance(child.expression, StringLiteral):
            self.unloadable_partials[str(child.expression)].append(
                (self._template_name, child.linenum)
            )
            return None, None

        if not isinstance(child.expression, StringLiteral):
            raise TemplateTraversalError(
                f"can't load from a variable expression when in {load_mode!r} mode"
            )

        name = child.expression.value
        load_context = child.load_context or {}

        if (name, load_context) in self._partials:
            return None, None

        self._partials.append((name, load_context))
        return name, load_context

    def _get_template(
        self,
        name: str,
        load_context: Dict[str, str],
        parent_name: str,
        parent_node: ChildNode,
    ) -> BoundTemplate:
        try:
            return self._empty_context.get_template_with_context(name, **load_context)
        except TemplateNotFound:
            self.unloadable_partials[name].append((parent_name, parent_node.linenum))
            raise

    async def _get_template_async(
        self,
        name: str,
        load_context: Dict[str, str],
        parent_name: str,
        parent_node: ChildNode,
    ) -> BoundTemplate:
        try:
            return await self._empty_context.get_template_with_context_async(
                name, **load_context
            )
        except TemplateNotFound:
            self.unloadable_partials[name].append((parent_name, parent_node.linenum))
            raise

    def _stack_blocks(
        self, stack_context: Context, template: BoundTemplate, count_tags: bool = True
    ) -> Tuple[Optional[str], List[InheritanceBlockNode]]:
        template_name = template.name or "<string>"
        ast_extends_node, ast_block_nodes = stack_blocks(stack_context, template)

        # Count `extends` and `block` tags here, as we don't get the chance later.
        if count_tags:
            if ast_extends_node:
                token = ast_extends_node.token()
                self.tags[token.value].append((template_name, token.linenum))
        for ast_node in ast_block_nodes:
            token = ast_node.token()
            self.tags[token.value].append((template_name, token.linenum))

        if ast_extends_node:
            return ast_extends_node.name.evaluate(stack_context), ast_block_nodes
        return None, ast_block_nodes

    def _count_tag(self, node: Node) -> None:
        token = node.token()
        if not isinstance(node, BlockNode) and token.type == TOKEN_TAG:
            self.tags[token.value].append((self._template_name, token.linenum))

    def _update_reference_counters(self, refs: _TemplateCounter) -> None:
        # Accumulate references from the partial/child template into its parent.
        for _name, _refs in refs.variables.items():
            self.variables[_name].extend(_refs)

        for _name, _refs in refs.template_globals.items():
            self.template_globals[_name].extend(_refs)

        for node_name, _refs in refs.failed_visits.items():
            self.failed_visits[node_name].extend(_refs)

        for template_name, _refs in refs.unloadable_partials.items():
            self.unloadable_partials[template_name].extend(_refs)

        for filter_name, _refs in refs.filters.items():
            self.filters[filter_name].extend(_refs)

        for tag_name, _refs in refs.tags.items():
            self.tags[tag_name].extend(_refs)

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

    def _expression_hook(self, child: ChildNode) -> None:
        pass

    async def _async_expression_hook(self, child: ChildNode) -> None:
        pass


class _InheritanceChainCounter(_TemplateCounter):
    def __init__(
        self,
        base_template: BoundTemplate,
        stack_context: Context,
        *,
        parent_block_stack_item: Optional[_BlockStackItem] = None,
        follow_partials: bool = True,
        raise_for_failures: bool = True,
        scope: Optional[ReadOnlyChainMap] = None,
        template_locals: Optional[IdentifierMap] = None,
        partials: Optional[List[Tuple[str, Optional[Dict[str, str]]]]] = None,
    ) -> None:
        self.stack_context = stack_context
        self.parent_block_stack_item = parent_block_stack_item
        super().__init__(
            template=base_template,
            follow_partials=follow_partials,
            raise_for_failures=raise_for_failures,
            scope=scope,
            template_locals=template_locals,
            partials=partials,
        )

    def _analyze(self, node: Node) -> None:
        if isinstance(node, InheritanceBlockNode):
            return self._analyze_block(node)
        return super()._analyze(node)

    async def _analyze_async(self, node: Node) -> None:
        if isinstance(node, InheritanceBlockNode):
            return await self._analyze_block_async(node)
        return await super()._analyze_async(node)

    def _expression_hook(self, child: ChildNode) -> None:
        expression = child.expression
        if not expression:
            return

        if not self.parent_block_stack_item:
            return

        if self._contains_super(expression):
            template = self._make_template(self.parent_block_stack_item)
            scope = {str(ident.path[0]): None for ident in self.template_locals}
            refs = _InheritanceChainCounter(
                template,
                self.stack_context,
                follow_partials=self.follow_partials,
                scope=ReadOnlyChainMap({"block": None}, self._scope, scope),
                raise_for_failures=self.raise_for_failures,
                partials=self._partials,
            ).analyze()

            self._update_reference_counters(refs)

    async def _async_expression_hook(self, child: ChildNode) -> None:
        expression = child.expression
        if not expression:
            return

        if not self.parent_block_stack_item:
            return

        if self._contains_super(expression):
            template = self._make_template(self.parent_block_stack_item)
            scope = {str(ident.path[0]): None for ident in self.template_locals}
            refs = await _InheritanceChainCounter(
                template,
                self.stack_context,
                follow_partials=self.follow_partials,
                scope=ReadOnlyChainMap({"block": None}, self._scope, scope),
                raise_for_failures=self.raise_for_failures,
                partials=self._partials,
            ).analyze_async()

            self._update_reference_counters(refs)

    def _contains_super(self, expression: Expression) -> bool:
        if isinstance(expression, Identifier) and str(expression) == "block.super":
            return True

        if isinstance(expression, FilteredExpression):
            if (
                isinstance(expression.expression, Identifier)
                and str(expression.expression) == "block.super"
            ):
                return True

        for expr in expression.children():
            return self._contains_super(expr)

        return False

    def _analyze_block(self, block: InheritanceBlockNode) -> None:
        block_stacks: Dict[
            str, List[_BlockStackItem]
        ] = self.stack_context.tag_namespace["extends"]

        block_stack_item = block_stacks[block.name][0]
        template = self._make_template(block_stack_item)
        scope = {str(ident.path[0]): None for ident in self.template_locals}

        refs = _InheritanceChainCounter(
            template,
            self.stack_context,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap({"block": None}, self._scope, scope),
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
            parent_block_stack_item=block_stack_item.parent,
        ).analyze()

        self._update_reference_counters(refs)

    async def _analyze_block_async(self, block: InheritanceBlockNode) -> None:
        block_stacks: Dict[
            str, List[_BlockStackItem]
        ] = self.stack_context.tag_namespace["extends"]

        block_stack_item = block_stacks[block.name][0]
        template = self._make_template(block_stack_item)
        scope = {str(ident.path[0]): None for ident in self.template_locals}

        refs = await _InheritanceChainCounter(
            template,
            self.stack_context,
            follow_partials=self.follow_partials,
            scope=ReadOnlyChainMap({"block": None}, self._scope, scope),
            raise_for_failures=self.raise_for_failures,
            partials=self._partials,
            parent_block_stack_item=block_stack_item.parent,
        ).analyze_async()

        self._update_reference_counters(refs)

    def _make_template(self, item: _BlockStackItem) -> BoundTemplate:
        parse_tree = ParseTree()
        parse_tree.statements = [item.block.block]
        return self.template.env.template_class(
            self.template.env, parse_tree=parse_tree, name=item.source_name
        )


class References:
    "Collects references for Template.analyze and friends"

    def __init__(self) -> None:
        self.variable_references: List[Identifier] = []
        self.filter_references: List[str] = []

    def append_variable(self, var: Identifier) -> None:
        "Add a variable reference"
        self.variable_references.append(var)

    def append_filters(self, filters: List[str]) -> None:
        "Add references to filters"
        self.filter_references.extend(filters)

    def extend(self, refs: References) -> None:
        "Incorporate references from another References"
        self.variable_references.extend(refs.variable_references)
        self.filter_references.extend(refs.filter_references)
