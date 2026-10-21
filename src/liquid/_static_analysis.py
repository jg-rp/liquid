from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, TypedDict

from . import expressions
from ._context import RenderContext
from ._markup import SCOPE_ISOLATED
from .exceptions import LiquidError
from .tokens import span, token_value

if TYPE_CHECKING:
    from ._markup import Expression, Markup
    from ._template import Template
    from .tokens import Token


@dataclass(slots=True, kw_only=True)
class _Location:
    template: Template
    token: Token

    def line_col(self, index: int) -> tuple[int, int]:
        cumulative_length = 0
        target_line_index = -1

        for i, line in enumerate(self.template.lines):
            cumulative_length += len(line)
            if index < cumulative_length:
                target_line_index = i
                break

        if target_line_index == -1:
            raise LiquidError("index out of bounds")

        line_number = target_line_index + 1
        line = self.template.lines[target_line_index]
        column_number = index - (cumulative_length - len(line))
        return line_number, column_number

    def span(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return self.line_col(self.token[1]), self.line_col(self.token[2])

    def value(self) -> str:
        return token_value(self.token, self.template.source)


class Loc(TypedDict):
    start_index: int
    end_index: int
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    value: str
    template_name: str
    template_path: str | None


type Segments = tuple[int | str | Segments, ...]
"""Names and indexes that make up a path to a variable."""


class Var(Loc):
    segments: Segments
    path: str


type Vars = dict[str, list[Var]]

type Locations = dict[str, list[Loc]]

RE_PROPERTY = re.compile(r"[a-zA-Z_][a-zA-Z0-9_-]*\??")


@dataclass(slots=True, kw_only=True)
class _StaticVariable:
    segments: Segments
    location: _Location

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _StaticVariable) and self.segments == other.segments

    def root(self) -> str:
        segment = self.segments[0] if self.segments else ""
        if isinstance(segment, tuple):
            return self._to_str(segment)
        return str(segment)

    def __str__(self) -> str:
        return self._to_str(self.segments)

    def _to_str(self, segments: Segments) -> str:
        def segment_str(segment: int | str | Segments) -> str:
            if isinstance(segment, tuple):
                return f"[{self._to_str(segment)}]"
            if isinstance(segment, str) and RE_PROPERTY.match(segment):
                return f".{segment}"
            return f"[{segment}]"

        it = iter(segments)
        head = next(it)

        return "".join(chain(str(head), (segment_str(s) for s in it)))


class _StaticScope:
    def __init__(self, globals: set[str]) -> None:
        self.stack: list[set[str]] = [globals]

    def add(self, name: str) -> None:
        self.stack[0].add(name)

    def __contains__(self, key: str) -> bool:
        for scope in self.stack:
            if key in scope:
                return True

        return False

    def pop(self) -> set[str] | None:
        return self.stack.pop() if self.stack else None

    def push(self, scope: set[str]) -> _StaticScope:
        self.stack.append(scope)
        return self


class _VariableMap:
    def __init__(self) -> None:
        self.data: dict[str, list[_StaticVariable]] = {}

    def add(self, key: _StaticVariable) -> None:
        v = self.get(key)
        if v is not None:
            v.append(key)

    def get(self, key: _StaticVariable) -> list[_StaticVariable] | None:
        k = key.root()
        if k not in self.data:
            self.data[k] = []
        return self.data[k]

    def asdict(self) -> Vars:
        obj: Vars = {}

        for k, v in self.data.items():
            a: list[Var] = []

            for sv in v:
                ((start_line, start_column), (end_line, end_column)) = (
                    sv.location.span()
                )

                a.append(
                    {
                        "segments": sv.segments,
                        "path": str(sv),
                        "start_index": sv.location.token[1],
                        "end_index": sv.location.token[2],
                        "start_line": start_line,
                        "start_column": start_column,
                        "end_line": end_line,
                        "end_column": end_column,
                        "value": sv.location.value(),
                        "template_name": sv.location.template.name,
                        "template_path": sv.location.template.path,
                    }
                )

            obj[k] = a

        return obj


@dataclass(slots=True, kw_only=True)
class TemplateAnalysis:
    variables: Vars
    locals: Vars
    globals: Vars
    filters: Locations
    tags: Locations


def analyze(template: Template, *, include_partials: bool) -> TemplateAnalysis:
    variables = _VariableMap()
    globals = _VariableMap()
    locals = _VariableMap()

    filters: defaultdict[str, list[_Location]] = defaultdict(list)
    tags: defaultdict[str, list[_Location]] = defaultdict(list)

    template_Scope: set[str] = set()
    root_scope = _StaticScope(template_Scope)
    static_context = RenderContext(template)

    # Names of partial templates that have already been analyzed.
    # Keys are hashes of partial template name and its arguments. If we've
    # visited a template before but with different arguments, later visits
    # only record global variables so as not to double count locals, filters
    # and tags.
    seen: defaultdict[str, set[int | None]] = defaultdict(set)

    def visit(
        node: Markup,
        template: Template,
        scope: _StaticScope,
        *,
        just_globals: bool = False,
    ) -> None:
        if template.name and not just_globals:
            seen[template.name].add(None)

        # Update tags
        # Markup with empty `node.tag` is silenced.
        if not just_globals and node.tag:
            tags[node.tag].append(_Location(template=template, token=node.token))

        # Update variables from `node.expressions()`
        for expr in node.expressions():
            analyze_variables(
                expr,
                template,
                scope,
                globals,
                variables if not just_globals else _VariableMap(),
                static_context,
            )

            if not just_globals:
                # Update filters from expr
                for filter_name, span in extract_filters(
                    expr, template, static_context
                ):
                    filters[filter_name].append(span)

        # Update template scope from `node.template_scope()`
        for name in node.template_scope():
            scope.add(name.value)
            locals.add(
                _StaticVariable(
                    segments=(name.value,),
                    location=_Location(template=template, token=name.span),
                )
            )

        # Set block scope before descending into child nodes.
        block_scope = node.block_scope()
        if block_scope:
            scope.push({n.value for n in block_scope})

        for child in node.children():
            visit(child, template, scope, just_globals=just_globals)

        if block_scope:
            scope.pop()

        # Descend into partial templates
        if include_partials:
            for partial in node.partials(static_context):
                template_name = partial.template.name

                # If we've seen this partial before but with different arguments,
                # we might want to visit it again but only capture globals.
                just_globals_ = template_name in seen

                if not partial.key in seen[template_name]:
                    seen[template_name].add(partial.key)
                    partial_globals = {n.value for n in partial.in_scope}

                    partial_scope = (
                        _StaticScope(partial_globals)
                        if partial.scope == SCOPE_ISOLATED
                        else root_scope.push(partial_globals)
                    )

                    for partial_node in partial.template.nodes:
                        if not isinstance(partial_node, str):
                            visit(
                                partial_node,
                                partial.template,
                                partial_scope,
                                just_globals=just_globals_,
                            )

                    if partial.scope != SCOPE_ISOLATED:
                        partial_scope.pop()

    for node in template.nodes:
        if not isinstance(node, str):
            visit(node, template, root_scope)

    return TemplateAnalysis(
        variables=variables.asdict(),
        locals=locals.asdict(),
        globals=globals.asdict(),
        filters=to_locations(filters),
        tags=to_locations(tags),
    )


async def analyze_async(
    template: Template, *, include_partials: bool
) -> TemplateAnalysis:
    variables = _VariableMap()
    globals = _VariableMap()
    locals = _VariableMap()

    filters: defaultdict[str, list[_Location]] = defaultdict(list)
    tags: defaultdict[str, list[_Location]] = defaultdict(list)

    template_Scope: set[str] = set()
    root_scope = _StaticScope(template_Scope)
    static_context = RenderContext(template)

    # Names of partial templates that have already been analyzed.
    # Keys are hashes of partial template name and its arguments. If we've
    # visited a template before but with different arguments, later visits
    # only record global variables so as not to double count locals, filters
    # and tags.
    seen: defaultdict[str, set[int | None]] = defaultdict(set)

    async def visit(
        node: Markup,
        template: Template,
        scope: _StaticScope,
        *,
        just_globals: bool = False,
    ) -> None:
        if template.name and not just_globals:
            seen[template.name].add(None)

        # Update tags
        # Markup with empty `node.tag` is silenced.
        if not just_globals and node.tag:
            tags[node.tag].append(_Location(template=template, token=node.token))

        # Update variables from `node.expressions()`
        for expr in node.expressions():
            analyze_variables(
                expr,
                template,
                scope,
                globals,
                variables if not just_globals else _VariableMap(),
                static_context,
            )

            if not just_globals:
                # Update filters from expr
                for filter_name, span in extract_filters(
                    expr, template, static_context
                ):
                    filters[filter_name].append(span)

        # Update template scope from `node.template_scope()`
        for name in node.template_scope():
            scope.add(name.value)
            locals.add(
                _StaticVariable(
                    segments=(name.value,),
                    location=_Location(template=template, token=name.span),
                )
            )

        # Set block scope before descending into child nodes.
        block_scope = node.block_scope()
        if block_scope:
            scope.push({n.value for n in block_scope})

        for child in node.children():
            await visit(child, template, scope, just_globals=just_globals)

        if block_scope:
            scope.pop()

        # Descend into partial templates
        if include_partials:
            for partial in await node.partials_async(static_context):
                temlate_name = partial.template.name

                # If we've seen this partial before but with different arguments,
                # we might want to visit it again but only capture globals.
                just_globals_ = temlate_name in seen

                if not partial.key in seen[temlate_name]:
                    seen[temlate_name].add(partial.key)
                    partial_globals = {n.value for n in partial.in_scope}

                    partial_scope = (
                        _StaticScope(partial_globals)
                        if partial.scope == SCOPE_ISOLATED
                        else root_scope.push(partial_globals)
                    )

                    for partial_node in partial.template.nodes:
                        if not isinstance(partial_node, str):
                            await visit(
                                partial_node,
                                partial.template,
                                partial_scope,
                                just_globals=just_globals_,
                            )

                    if partial.scope != SCOPE_ISOLATED:
                        partial_scope.pop()

    for node in template.nodes:
        if not isinstance(node, str):
            await visit(node, template, root_scope)

    return TemplateAnalysis(
        variables=variables.asdict(),
        locals=locals.asdict(),
        globals=globals.asdict(),
        filters=to_locations(filters),
        tags=to_locations(tags),
    )


def analyze_variables(
    expression: Expression,
    template: Template,
    scope: _StaticScope,
    globals: _VariableMap,
    variables: _VariableMap,
    static_context: RenderContext,
) -> None:
    if isinstance(expression, expressions.Variable):
        v = _StaticVariable(
            segments=segments(expression, template),
            location=_Location(template=template, token=expression.span),
        )

        variables.add(v)

        if str(expression.root) not in scope:
            globals.add(v)

    for expr in expression.children():
        analyze_variables(expr, template, scope, globals, variables, static_context)


def segments(variable: expressions.Variable, template: Template) -> Segments:

    def generate_segments() -> Iterable[int | str | Segments]:
        if isinstance(variable.root, expressions.VariableSegment):
            yield segments(variable.root.var, template)
        else:
            yield variable.root.value

        if variable.selectors:
            for s in variable.selectors:
                if isinstance(s, expressions.VariableSegment):
                    yield segments(s.var, template)
                else:
                    yield s.value

    return tuple(generate_segments())


def extract_filters(
    expression: Expression, template: Template, static_context: RenderContext
) -> Iterable[tuple[str, _Location]]:
    if isinstance(expression, expressions.Filtered):
        yield (
            expression.name.value,
            _Location(
                template=template, token=span(expression.name.token, expression.span)
            ),
        )

    for expr in expression.children():
        yield from extract_filters(expr, template, static_context)


def to_locations(d: defaultdict[str, list[_Location]]) -> Locations:
    result: Locations = {}

    for k, v in d.items():
        a: list[Loc] = []

        for l in v:
            ((start_line, start_column), (end_line, end_column)) = l.span()

            a.append(
                {
                    "start_index": l.token[1],
                    "end_index": l.token[2],
                    "start_line": start_line,
                    "start_column": start_column,
                    "end_line": end_line,
                    "end_column": end_column,
                    "value": l.value(),
                    "template_name": l.template.name,
                    "template_path": l.template.path,
                }
            )

        result[k] = a

    return result
