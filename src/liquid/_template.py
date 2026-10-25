from __future__ import annotations

import re
from collections.abc import Awaitable, Callable, Mapping
from itertools import chain
from typing import TYPE_CHECKING

from ._chain_map import ReadOnlyChainMap
from ._context import RenderContext
from ._io import StringBuffer
from ._markup import render_block, render_block_async
from ._static_analysis import Segments, TemplateAnalysis, analyze, analyze_async
from .exceptions import DetailedLiquidError, LiquidError
from .expressions import ErrorExpr
from .tags import CommentTag, DocTag, ErrorNode, InlineCommentTag, TemplateComment

if TYPE_CHECKING:
    from ._markup import Block, Expression, Node
    from .environment import Environment
    from .tokens import Token


class Template:
    def __init__(
        self,
        env: Environment,
        source: str,
        name: str,
        nodes: Block,
        *,
        path: str | None = None,
        globals: Mapping[str, object] | None,
        matter: Mapping[str, object] | None,
        up_to_date: Callable[[], bool | Awaitable[bool]] | None = None,
    ) -> None:
        self.env = env
        self.source = source
        self.name = name
        self.nodes = nodes
        self.path = path
        self.globals = globals
        self.matter = matter
        self.up_to_date = up_to_date

        self._lines: list[str] | None = None

    @property
    def lines(self) -> list[str]:
        if self._lines is None:
            lines = re.split(r"(?<=\n)", self.source)
            if lines[-1] == "":
                lines.pop()
            self._lines = lines

        return self._lines

    def line_col(self, token: Token) -> tuple[int, int]:
        """Return the line and column number of `token` in this template."""
        index = token[1]
        cumulative_length = 0
        target_line_index = -1

        for i, line in enumerate(self.lines):
            cumulative_length += len(line)
            if index < cumulative_length:
                target_line_index = i
                break

        if target_line_index == -1:
            raise LiquidError("index out of bounds")

        line_number = target_line_index + 1
        line = self.lines[target_line_index]
        column_number = index - (cumulative_length - len(line))
        return line_number, column_number

    def render(self, data: Mapping[str, object] | None = None) -> str:
        buffer: StringBuffer = StringBuffer()
        context = RenderContext(self, globals=self.make_globals(data))
        self.render_with_context(context, buffer)
        return buffer.getvalue()

    async def render_async(self, data: Mapping[str, object] | None = None) -> str:
        buffer: StringBuffer = StringBuffer()
        context = RenderContext(self, globals=self.make_globals(data))
        await self.render_with_context_async(context, buffer)
        return buffer.getvalue()

    def render_with_context(self, context: RenderContext, buffer: StringBuffer) -> None:
        render_block(self.nodes, context, buffer)

    async def render_with_context_async(
        self, context: RenderContext, buffer: StringBuffer
    ) -> None:
        await render_block_async(self.nodes, context, buffer)

    def render_with_error_capture(
        self, data: Mapping[str, object] | None = None
    ) -> tuple[str, list[DetailedLiquidError]]:
        buffer: StringBuffer = StringBuffer()
        context = RenderContext(
            self, globals=self.make_globals(data), capture_errors=True
        )
        self.render_with_context(context, buffer)
        return buffer.getvalue(), context.errors

    async def render_with_error_capture_async(
        self, data: Mapping[str, object] | None = None
    ) -> tuple[str, list[DetailedLiquidError]]:
        buffer: StringBuffer = StringBuffer()
        context = RenderContext(
            self, globals=self.make_globals(data), capture_errors=True
        )
        await self.render_with_context_async(context, buffer)
        return buffer.getvalue(), context.errors

    def make_globals(
        self, data: Mapping[str, object] | None
    ) -> Mapping[str, object] | None:
        if not (data or self.matter or self.globals):
            return None

        chain = ReadOnlyChainMap()

        if self.globals:
            chain.push(self.globals)

        if self.matter:
            chain.push(self.matter)

        if data:
            chain.push(data)

        return chain

    def is_up_to_date(self) -> bool:
        """Return ``False`` if the template has bee modified, ``True`` otherwise."""
        if not self.up_to_date:
            return True

        uptodate = self.up_to_date()
        if not isinstance(uptodate, bool):
            raise LiquidError(
                f"expected a boolean from uptodate, found {type(uptodate).__name__}",
            )
        return uptodate

    async def is_up_to_date_async(self) -> bool:
        """An async version of `is_up_to_date`.

        If `template.up_to_date` is a coroutine, it wil be awaited. Otherwise it will be
        called just like `is_up_to_date`
        """
        if not self.up_to_date:
            return True

        uptodate = self.up_to_date()
        if isinstance(uptodate, Awaitable):
            return await uptodate
        return uptodate

    def analyze(self, *, include_partials: bool = True) -> TemplateAnalysis:
        """Statically analyze this template and any included/rendered templates.

        Parameters
        ----------
        include_partials
            If `True`, we will try to load partial templates and analyze those templates too.
        """
        return analyze(self, include_partials=include_partials)

    async def analyze_async(self, *, include_partials: bool = True) -> TemplateAnalysis:
        """An async version of `analyze`."""
        return await analyze_async(self, include_partials=include_partials)

    def variables(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template without path segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See also [global_variables][liquid.BoundTemplate.global_variables].

        Parameters
        ----------
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

        Parameters
        ----------
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

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return list(
            {v["path"] for v in chain.from_iterable(list(analysis.variables.values()))}
        )

    async def variable_paths_async(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template including all path segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See also [global_variable_paths][liquid.BoundTemplate.global_variable_paths].

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return list(
            {v["path"] for v in chain.from_iterable(list(analysis.variables.values()))}
        )

    def variable_segments(self, *, include_partials: bool = True) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See [global_variable_segments][liquid.BoundTemplate.global_variable_segments].

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return list(
            {w["segments"] for w in chain.from_iterable(analysis.variables.values())}
        )

    async def variable_segments_async(
        self, *, include_partials: bool = True
    ) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Includes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        See [global_variable_segments][liquid.BoundTemplate.global_variable_segments].

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return list(
            {w["segments"] for w in chain.from_iterable(analysis.variables.values())}
        )

    def global_variables(self, *, include_partials: bool = True) -> list[str]:
        """Return a list of variables used in this template without path segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Parameters
        ----------
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

        Parameters
        ----------
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

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return list(
            {v["path"] for v in chain.from_iterable(list(analysis.globals.values()))}
        )

    async def global_variable_paths_async(
        self, *, include_partials: bool = True
    ) -> list[str]:
        """Return a list of variables used in this template including all path segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return list(
            {v["path"] for v in chain.from_iterable(list(analysis.globals.values()))}
        )

    def global_variable_segments(
        self, *, include_partials: bool = True
    ) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = self.analyze(include_partials=include_partials)
        return list(
            {w["segments"] for w in chain.from_iterable(analysis.globals.values())}
        )

    async def global_variable_segments_async(
        self, *, include_partials: bool = True
    ) -> list[Segments]:
        """Return a list of variables used in this template, each as a list of segments.

        Excludes variables that are _local_ to the template, like those crated with
        `{% assign %}` and `{% capture %}`.

        Parameters
        ----------
        include_partials: If `True`, will try to load and find variables in
                included/rendered templates too.

        Returns:
            A list of distinct paths for variables in this template.
        """
        analysis = await self.analyze_async(include_partials=include_partials)
        return list(
            {w["segments"] for w in chain.from_iterable(analysis.globals.values())}
        )

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

    def comments(self) -> list[CommentTag | InlineCommentTag | TemplateComment]:
        """Return a list of comment tag nodes found in this template.

        Instances of `CommentNode` and `InlineCommentNode` have `token` and
        `text` properties. Use `[node.text for node in template.comments()]` to
        get a list of comment strings.

        Note that this method does not try to load included or rendered
        templates.
        """
        nodes: list[CommentTag | InlineCommentTag | TemplateComment] = []

        def visit(node: Node) -> None:
            if isinstance(node, str):
                return

            if isinstance(node, (CommentTag, InlineCommentTag, TemplateComment)):
                nodes.append(node)

            for child in node.children():
                visit(child)

        for child in self.nodes:
            visit(child)

        return nodes

    def docs(self) -> list[DocTag]:
        """Return a list of doc tag nodes found in this template.

        Instances of `DocNode` have `token` and `text` properties. Use
        `[node.text for node in template.docs()]` to get a list of doc strings.
        """
        nodes: list[DocTag] = []

        def visit(node: Node) -> None:
            if isinstance(node, str):
                return

            if isinstance(node, DocTag):
                nodes.append(node)

            for child in node.children():
                visit(child)

        for child in self.nodes:
            visit(child)

        return nodes

    def errors(self) -> list[ErrorNode | ErrorExpr]:
        """Return a list of error nodes found in this template.

        Error nodes are inserted by lax parsers via ``Environment.parser``. Strict
        parsers raise errors before a template can be created.
        """
        nodes: list[ErrorNode | ErrorExpr] = []

        def visit_expr(expr: Expression) -> None:
            if isinstance(expr, ErrorExpr):
                nodes.append(expr)

            for child in expr.children():
                visit_expr(child)

        def visit(node: Node) -> None:
            if isinstance(node, str):
                return

            if isinstance(node, ErrorNode):
                nodes.append(node)

            for expr in node.expressions():
                visit_expr(expr)

            for child in node.children():
                visit(child)

        for child in self.nodes:
            visit(child)

        return nodes

    def __str__(self) -> str:
        return self.source
