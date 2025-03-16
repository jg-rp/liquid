"""Shared configuration from which templates can be loaded and parsed."""

from __future__ import annotations

import warnings
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import Type
from typing import Union

from . import builtin
from .analyze_tags import InnerTagMap
from .analyze_tags import TagAnalysis
from .builtin import DictLoader
from .exceptions import LiquidError
from .exceptions import LiquidSyntaxError
from .exceptions import TemplateInheritanceError
from .exceptions import lookup_warning
from .extra import add_tags_and_filters as register_extra_tags_and_filters
from .lex import get_lexer
from .mode import Mode
from .parser import get_parser
from .stream import TokenStream
from .template import BoundTemplate
from .undefined import Undefined

if TYPE_CHECKING:
    from pathlib import Path

    from .ast import Node
    from .context import RenderContext
    from .loader import BaseLoader
    from .tag import Tag
    from .token import Token


class Environment:
    """Shared configuration from which templates can be loaded and parsed.

    An `Environment` is where you might register custom tags and filters, or store
    global context variables that should be included with every template.

    Args:
        extra: If `True`, register all extra tags and filters. Defaults to `False`.
        tag_start_string: The sequence of characters indicating the start of a
            liquid tag.
        tag_end_string: The sequence of characters indicating the end of a liquid
            tag.
        statement_start_string: The sequence of characters indicating the start of
            an output statement.
        statement_end_string: The sequence of characters indicating the end of an
            output statement.
        template_comments: If `True`, enable template comments, where, by default,
            anything between `{#` and `#}` is considered a comment.
        comment_start_string: The sequence of characters indicating the start of a
            comment. `template_comments` must be `True` for `comment_start_string`
            to have any effect.
        comment_end_string: The sequence of characters indicating the end of a
            comment.  `template_comments` must be `True` for `comment_end_string`
            to have any effect.
        tolerance: Indicates how tolerant to be of errors. Must be one of
            `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
        loader: A template loader. If you want to use the builtin "render" or
            "include" tags, a loader must be configured.
        undefined: A subclass of `Undefined` that represents undefined values. Could be
            one of the built-in undefined types, `Undefined`, `DebugUndefined` or
            `StrictUndefined`.
        strict_filters: If `True`, will raise an exception upon finding an
            undefined filter. Otherwise undefined filters are silently ignored.
        autoescape: If `True`, all render context values will be HTML-escaped before
            output unless they've been explicitly marked as "safe".
        globals: An optional mapping that will be added to the render context of any
            template loaded from this environment.
    """

    context_depth_limit: ClassVar[int] = 30
    """The maximum number of times a render context can be extended or wrapped before
    raising a `ContextDepthError`."""

    loop_iteration_limit: ClassVar[Optional[int]] = None
    """The maximum number of loop iterations allowed before a LoopIterationLimitError is
    raised."""

    local_namespace_limit: ClassVar[Optional[int]] = None
    """The maximum number of bytes (according to `sys.getsizeof`) allowed in a
    template's local namespace before a LocalNamespaceLimitError is raised. We only
    count the size of the namespaces values, not the size of keys/names."""

    output_stream_limit: ClassVar[Optional[int]] = None
    """The maximum number of bytes that can be written to a template's output stream
    before raising an OutputStreamLimitError."""

    template_class: Type[BoundTemplate] = BoundTemplate
    """Instances of `template_class` are returned from `from_string`, `get_template`
    and `get_template_async`. It should be the `BoundTemplate` class or a subclass of
    it."""

    suppress_blank_control_flow_blocks: bool = True
    """When `True`, don't render control flow blocks that contain only whitespace."""

    shorthand_indexes: bool = False
    """When `True`, accept indexes without enclosing square brackets in paths to
    variables. Defaults to `False`."""

    string_sequences: bool = False
    """When `True`, strings are treated as sequences. That is, characters (Unicode code
    points) in a string can be looped over and selected by index. Defaults to `False`.
    """

    string_first_and_last: bool = False
    """When `True`, the special `first` and `last` properties will return the first and
    last charters of a string. Otherwise `first` and `last` will resolve to Undefined
    when applied to a string. Defaults to `False`."""

    logical_not_operator: bool = False
    """When `True`, allow the use of the logical `not` operator in logical expressions.
    Defaults to `False`.
    """

    logical_parentheses: bool = False
    """When `True`, allow the use of parentheses in logical expressions to group terms.
    Defaults to `False.`"""

    ternary_expressions: bool = False
    """When `True`, allow the use of ternary expression in output statements, assign
    tags and echo tags. Defaults to `False`."""

    keyword_assignment: bool = False
    """When `True` accept `=` or `:` as the separator token between argument names
    and argument values. By default only `:` is allowed."""

    def __init__(
        self,
        *,
        extra: bool = False,
        tag_start_string: str = r"{%",
        tag_end_string: str = r"%}",
        statement_start_string: str = r"{{",
        statement_end_string: str = r"}}",
        tolerance: Mode = Mode.STRICT,
        loader: Optional[BaseLoader] = None,
        undefined: Type[Undefined] = Undefined,
        strict_filters: bool = True,
        autoescape: bool = False,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        template_comments: bool = False,
        comment_start_string: str = "{#",
        comment_end_string: str = "#}",
    ):
        self.tag_start_string = tag_start_string
        self.tag_end_string = tag_end_string
        self.statement_start_string = statement_start_string
        self.statement_end_string = statement_end_string

        # An instance of a template loader implementing `liquid.loaders.BaseLoader`.
        # `get_template()` will delegate to this loader.
        self.loader = loader or DictLoader({})

        # A mapping of template variable names to python objects. These variables will
        # be added to the global namespace of any template rendered from this
        # environment using `from_string` or `get_template`.
        self.globals: Mapping[str, object] = globals or {}

        # Extended template comment syntax control.
        self.template_comments = template_comments
        self.comment_start_string = comment_start_string
        self.comment_end_string = comment_end_string
        if not self.template_comments:
            self.comment_start_string = ""
            self.comment_end_string = ""

        self.undefined: Type[Undefined] = undefined
        self.strict_filters: bool = strict_filters
        self.autoescape: bool = autoescape
        self.mode: Mode = tolerance

        self.tags: dict[str, Tag] = {}
        """The environment's tag register, mapping tag names to instances of `Tag`."""

        self.filters: dict[str, Callable[..., Any]] = {}
        """The environment's filter register, mapping filter names to callables."""

        self.setup_tags_and_filters(extra=extra)

    def __hash__(self) -> int:
        return hash(
            (
                self.statement_start_string,
                self.statement_end_string,
                self.tag_start_string,
                self.tag_end_string,
                self.comment_start_string,
                self.comment_end_string,
                self.mode,
            )
        )

    def tokenizer(self) -> Callable[[str], Iterator[Token]]:
        """Return a tokenizer for this environment."""
        return get_lexer(
            self.tag_start_string,
            self.tag_end_string,
            self.statement_start_string,
            self.statement_end_string,
            self.comment_start_string,
            self.comment_end_string,
        )

    def add_tag(self, tag: Type[Tag]) -> None:
        """Register a liquid tag with the environment.

        Built-in tags are registered for you automatically with every new `Environment`.

        Args:
            tag: The tag to register.
        """
        self.tags[tag.name] = tag(self)

    def add_filter(self, name: str, func: Callable[..., Any]) -> None:
        """Register a filter function with the environment.

        Args:
            name: The filter's name. Does not need to match the function name. This is
                what you'll use to apply the filter to an expression in a liquid
                template.
            func: Any callable that accepts at least one argument, the result of the
                expression the filter is applied to. If the filter needs access to the
                active environment or render context, use `liquid.filer.with_context`
                and/or `liquid.filter.with_environment` decorators.
        """
        self.filters[name] = func

    def setup_tags_and_filters(self, *, extra: bool = False) -> None:
        """Add default tags and filters to this environment.

        If _extra_ is `True`, register all extra, non-standard tags and filters too.
        """
        builtin.register(self)
        if extra:
            register_extra_tags_and_filters(self)

    def _parse(self, source: str) -> list[Node]:
        """Parse _source_ as a Liquid template.

        More often than not you'll want to use `Environment.from_string` instead.
        """
        parser = get_parser(self)
        token_iter = self.tokenizer()(source)
        return parser.parse(TokenStream(token_iter))

    def from_string(
        self,
        source: str,
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        matter: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """Parse the given string as a liquid template.

        Args:
            source: The liquid template source code.
            name: Optional name of the template. Available as `Template.name`.
            path: Optional path or identifier to the origin of the template.
            globals: An optional mapping of render context variables attached
                to the resulting template.
            matter: Optional mapping of render context variables associated
                with the template. Could be "front matter" or other meta data.
        """
        try:
            nodes = self._parse(source)
        except (LiquidSyntaxError, TemplateInheritanceError) as err:
            err.template_name = path
            raise err
        except Exception as err:  # noqa: BLE001
            raise LiquidError("unexpected liquid parsing error", token=None) from err
        return self.template_class(
            env=self,
            name=name,
            path=path,
            nodes=nodes,
            globals=self.make_globals(globals),
            matter=matter,
        )

    def parse(
        self,
        source: str,
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        matter: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """Parse the given string as a liquid template.

        Args:
            source: The liquid template source code.
            name: Optional name of the template. Available as `Template.name`.
            path: Optional path or identifier to the origin of the template.
            globals: An optional mapping of render context variables attached
                to the resulting template.
            matter: Optional mapping of render context variables associated
                with the template. Could be "front matter" or other meta data.
        """
        return self.from_string(
            source, name=name, path=path, globals=globals, matter=matter
        )

    def render(self, source: str, **data: object) -> str:
        """Parse and render source text."""
        return self.parse(source).render(**data)

    async def render_async(self, source: str, **data: object) -> str:
        """Parse and render source text."""
        return await self.parse(source).render_async(**data)

    def get_template(
        self,
        name: str,
        *,
        globals: Mapping[str, object] | None = None,  # noqa: A002
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> BoundTemplate:
        """Load and parse a template using the configured loader.

        Args:
            name: The template's name. The loader is responsible for interpreting
                the name. It could be the name of a file or some other identifier.
            globals: A mapping of render context variables attached to the
                resulting template.
            context: An optional render context that can be used to narrow the template
                source search space.
            kwargs: Arbitrary arguments that can be used to narrow the template source
                search space.

        Raises:
            TemplateNotFound: If a template with the given name can not be found.
        """
        try:
            return self.loader.load(
                env=self,
                name=name,
                globals=self.make_globals(globals),
                context=context,
                **kwargs,
            )
        except LiquidError as err:
            if not err.template_name:
                err.template_name = name
            raise

    async def get_template_async(
        self,
        name: str,
        *,
        globals: Mapping[str, object] | None = None,  # noqa: A002
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> BoundTemplate:
        """An async version of `get_template()`."""
        try:
            return await self.loader.load_async(
                env=self,
                name=name,
                globals=self.make_globals(globals),
                context=context,
                **kwargs,
            )
        except LiquidError as err:
            if not err.template_name:
                err.template_name = name
            raise

    def analyze_tags_from_string(
        self,
        source: str,
        name: str = "<string>",
        *,
        inner_tags: Optional[InnerTagMap] = None,
    ) -> TagAnalysis:
        """Analyze tags in template source text.

        Unlike template static or contextual analysis, a tag audit does not parse the
        template source text into an AST, nor does it attempt to load partial templates
        from `{% include %}` or `{% render %}` tags.

        Args:
            source: The source text of the template.
            name: A name or identifier for the template.
            inner_tags: A mapping of block tags to a list of allowed "inner" tags for
                the block. For example, `{% if %}` blocks are allowed to contain
                `{% elsif %}` and `{% else %}` tags.
        """
        return TagAnalysis(
            env=self,
            name=name,
            tokens=list(self.tokenizer()(source)),
            inner_tags=inner_tags,
        )

    def analyze_tags(
        self,
        name: str,
        *,
        context: Optional["RenderContext"] = None,
        inner_tags: Optional[InnerTagMap] = None,
        **kwargs: str,
    ) -> TagAnalysis:
        """Audit template tags without parsing source text into an abstract syntax tree.

        This is useful for identifying unknown, misplaced and unbalanced tags in a
        template's source text. See also `liquid.template.BoundTemplate.analyze`.

        Args:
            name: The template's name or identifier, as you would use with
                `Environment.get_template`. Use `Environment.analyze_tags_from_string`
                to audit tags in template text without using a template loader.
            context: An optional render context the loader might use to modify the
                template search space. If given, uses
                `liquid.loaders.BaseLoader.get_source_with_context` from the current
                loader.
            inner_tags: A mapping of block tags to a list of allowed "inner" tags for
                the block. For example, `{% if %}` blocks are allowed to contain
                `{% elsif %}` and `{% else %}` tags.
            kwargs: Loader context.
        """
        template_source = self.loader.get_source(
            self, template_name=name, context=context, **kwargs
        )

        return self.analyze_tags_from_string(
            template_source.text,
            name=template_source.name,
            inner_tags=inner_tags,
        )

    async def analyze_tags_async(
        self,
        name: str,
        *,
        context: Optional["RenderContext"] = None,
        inner_tags: Optional[InnerTagMap] = None,
        **kwargs: str,
    ) -> TagAnalysis:
        """An async version of `Environment.analyze_tags`."""
        template_source = await self.loader.get_source_async(
            env=self, template_name=name, context=context, **kwargs
        )

        return self.analyze_tags_from_string(
            template_source.text,
            name=template_source.name,
            inner_tags=inner_tags,
        )

    def make_globals(
        self,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
    ) -> dict[str, object]:
        """Combine environment globals with template globals."""
        if globals:
            # Template globals take priority over environment globals.
            return {**self.globals, **globals}
        return dict(self.globals)

    def error(
        self,
        exc: Union[Type[LiquidError], LiquidError],
        msg: Optional[str] = None,
        token: Optional[Token] = None,
    ) -> None:
        """Raise, warn or ignore the given exception according to the current mode."""
        if not isinstance(exc, LiquidError):
            exc = exc(msg, token=token)
        elif not exc.token:
            exc.token = token

        if self.mode == Mode.STRICT:
            raise exc
        if self.mode == Mode.WARN:
            warnings.warn(
                str(exc), category=lookup_warning(exc.__class__), stacklevel=2
            )


@lru_cache(maxsize=10)
def get_implicit_environment(
    *,
    extra: bool = False,
    tag_start_string: str,
    tag_end_string: str,
    statement_start_string: str,
    statement_end_string: str,
    tolerance: Mode,
    loader: Optional[BaseLoader],
    undefined: Type[Undefined],
    strict_filters: bool,
    autoescape: bool,
    globals: Optional[Mapping[str, object]],  # noqa: A002
    template_comments: bool,
    comment_start_string: str,
    comment_end_string: str,
) -> Environment:
    """Return an `Environment` initialized with the given arguments."""
    return Environment(
        extra=extra,
        tag_start_string=tag_start_string,
        tag_end_string=tag_end_string,
        statement_start_string=statement_start_string,
        statement_end_string=statement_end_string,
        tolerance=tolerance,
        loader=loader,
        undefined=undefined,
        strict_filters=strict_filters,
        autoescape=autoescape,
        globals=globals,
        template_comments=template_comments,
        comment_start_string=comment_start_string,
        comment_end_string=comment_end_string,
    )


# `Template` is a factory function masquerading as a class. The desire to have an
# intuitive API and to please the static type checker outweighs this abuse of Python
# naming conventions. At least for now.


def Template(  # noqa: N802, D417
    source: str,
    *,
    extra: bool = False,
    tag_start_string: str = r"{%",
    tag_end_string: str = r"%}",
    statement_start_string: str = r"{{",
    statement_end_string: str = r"}}",
    tolerance: Mode = Mode.STRICT,
    undefined: Type[Undefined] = Undefined,
    strict_filters: bool = True,
    autoescape: bool = False,
    globals: Optional[Mapping[str, object]] = None,  # noqa: A002
    template_comments: bool = False,
    comment_start_string: str = "{#",
    comment_end_string: str = "#}",
) -> BoundTemplate:
    """Parse a template, automatically creating an `Environment` to bind it to.

    Other than `source`, all arguments are passed to the implicit `Environment`,
    which might have been cached from previous calls to `Template`.

    Args:
        extra: If `True`, register all extra tags and filters. Defaults to `False`.
        tag_start_string: The sequence of characters indicating the start of a
            liquid tag.
        tag_end_string: The sequence of characters indicating the end of a liquid
            tag.
        statement_start_string: The sequence of characters indicating the start of
            an output statement.
        statement_end_string: The sequence of characters indicating the end of an
            output statement.
        template_comments: If `True`, enable template comments, where, by default,
            anything between `{#` and `#}` is considered a comment.
        comment_start_string: The sequence of characters indicating the start of a
            comment. `template_comments` must be `True` for `comment_start_string`
            to have any effect.
        comment_end_string: The sequence of characters indicating the end of a
            comment.  `template_comments` must be `True` for `comment_end_string`
            to have any effect.
        tolerance: Indicates how tolerant to be of errors. Must be one of
            `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
        undefined: A subclass of `Undefined` that represents undefined values. Could be
            one of the built-in undefined types, `Undefined`, `DebugUndefined` or
            `StrictUndefined`.
        strict_filters: If `True`, will raise an exception upon finding an
            undefined filter. Otherwise undefined filters are silently ignored.
        autoescape: If `True`, all render context values will be HTML-escaped before
            output unless they've been explicitly marked as "safe".
        globals: An optional mapping that will be added to the render context of any
            template loaded from this environment.
    """
    # Resorting to named arguments (repeated 3 times) as I've twice missed a bug
    # because of positional arguments.
    env = get_implicit_environment(
        extra=extra,
        tag_start_string=tag_start_string,
        tag_end_string=tag_end_string,
        statement_start_string=statement_start_string,
        statement_end_string=statement_end_string,
        tolerance=tolerance,
        loader=None,
        undefined=undefined,
        strict_filters=strict_filters,
        autoescape=autoescape,
        globals=None,
        template_comments=template_comments,
        comment_start_string=comment_start_string,
        comment_end_string=comment_end_string,
    )

    return env.from_string(source, globals=globals)
