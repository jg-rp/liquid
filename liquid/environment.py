"""Shared configuration from which templates can be loaded and parsed."""
from __future__ import annotations

import warnings
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import Iterator
from typing import Mapping
from typing import MutableMapping
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from liquid import ast
from liquid import builtin
from liquid import loaders
from liquid.analyze_tags import InnerTagMap
from liquid.analyze_tags import TagAnalysis
from liquid.context import Undefined
from liquid.exceptions import Error
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import TemplateInheritanceError
from liquid.exceptions import lookup_warning
from liquid.expressions import parse_boolean_expression
from liquid.expressions import parse_boolean_expression_with_parens
from liquid.expressions import parse_conditional_expression
from liquid.expressions import parse_conditional_expression_with_parens
from liquid.expressions import parse_filtered_expression
from liquid.expressions import parse_loop_expression
from liquid.lex import get_lexer
from liquid.mode import Mode
from liquid.parse import get_parser
from liquid.stream import TokenStream
from liquid.template import BoundTemplate
from liquid.utils import LRUCache

if TYPE_CHECKING:
    from pathlib import Path

    from liquid.context import Context
    from liquid.expression import BooleanExpression
    from liquid.expression import FilteredExpression
    from liquid.expression import LoopExpression
    from liquid.tag import Tag
    from liquid.token import Token


class Environment:
    """Shared configuration from which templates can be loaded and parsed.

    An `Environment` is where you might register custom tags and filters, or store
    global context variables that should be included with every template.

    Args:
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
            output unless they've been explicitly marked as "safe". Requires the package
            Markupsafe.
        auto_reload: If `True`, loaders that have an `uptodate` callable will
            reload template source data automatically. For deployments where template
            sources don't change between service reloads, setting auto_reload to `False`
            can yield an increase in performance by avoiding calls to `uptodate`.
        cache_size: The capacity of the template cache in number of templates.
            If `cache_size` is `None` or less than `1`, it has the effect of setting
            `auto_reload` to `False`.
        expression_cache_size: The capacity of each of the common expression caches.
            A `cache_size` of `0` will disabling expression caching.
        globals: An optional mapping that will be added to the render context of any
            template loaded from this environment.

    Attributes:
        context_depth_limit: Class attribute. The maximum number of times a render
            context can be extended or wrapped before a `ContextDepthError` is raised.
        local_namespace_limit: Class attribute. The maximum number of bytes (according
            to sys.getsizeof) allowed in a template's local namespace, per render,
            before a `LocalNamespaceLimitError` exception is raised. Note that we only
            count the size of the local namespace values, not its keys.
        loop_iteration_limit: Class attribute. The maximum number of loop iterations
            allowed before a  `liquid.exceptions.LoopIterationLimitError` is raised.
        output_stream_limit: Class attribute. The maximum number of bytes that can be
            written to a template's output stream, per render, before an
            `OutputStreamLimitError` exception is raised.
        render_whitespace_only_blocks: Class attribute. Indicates if block tags that,
            when rendered, contain whitespace only should be output. Defaults to
            `False`, meaning empty blocks are suppressed.
        undefined: The undefined type. When an identifier can not be resolved, an
            instance of `undefined` is returned.
        strict_filters: Indicates if an undefined filter should raise an exception or be
            ignored.
        autoescape: Indicates if auto-escape is enabled.
        tags: A dictionary mapping tag names to `liquid.tag.Tag` instances.
        filters: A dictionary mapping filter names to callable objects implementing a
            filter's behavior.
        mode: The current tolerance mode.
        cache: The template cache.
        auto_reload: Indicates if automatic reloading of templates is enabled.
        template_class: `Environment.get_template` and `Environment.from_string`
            return an instance of `Environment.template_class`.
        globals: A dictionary of variables that will be added to the context of every
            template rendered from the environment.
    """

    # Maximum number of times a context can be extended or wrapped before raising
    # a ContextDepthError.
    context_depth_limit: ClassVar[int] = 30

    # Maximum number of loop iterations allowed before a LoopIterationLimitError is
    # raised.
    loop_iteration_limit: ClassVar[Optional[int]] = None

    # Maximum number of bytes (according to sys.getsizeof) allowed in a template's
    # local namespace before a LocalNamespaceLimitError is raised. We only count the
    # size of the namespaces values, not the size of keys/names.
    local_namespace_limit: ClassVar[Optional[int]] = None

    # Maximum number of bytes that can be written to a template's output stream before
    # raising an OutputStreamLimitError.
    output_stream_limit: ClassVar[Optional[int]] = None

    # Instances of `template_class` are returned from `from_string`,
    # `get_template` and `get_template_async`. It should be the `BoundTemplate`
    # class or a subclass of it.
    template_class: Type[BoundTemplate] = BoundTemplate

    # Whether to output blocks that only contain only whitespace when rendered.
    render_whitespace_only_blocks: bool = False

    def __init__(
        self,
        tag_start_string: str = r"{%",
        tag_end_string: str = r"%}",
        statement_start_string: str = r"{{",
        statement_end_string: str = r"}}",
        strip_tags: bool = False,
        tolerance: Mode = Mode.STRICT,
        loader: Optional[loaders.BaseLoader] = None,
        undefined: Type[Undefined] = Undefined,
        strict_filters: bool = True,
        autoescape: bool = False,
        auto_reload: bool = True,
        cache_size: int = 300,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        template_comments: bool = False,
        comment_start_string: str = "{#",
        comment_end_string: str = "#}",
        expression_cache_size: int = 0,
    ):
        self.tag_start_string = tag_start_string
        self.tag_end_string = tag_end_string
        self.statement_start_string = statement_start_string
        self.statement_end_string = statement_end_string

        # Automatic tag stripping is not yet implemented. Changing this has no effect.
        self.strip_tags = strip_tags

        # An instance of a template loader implementing `liquid.loaders.BaseLoader`.
        # `get_template()` will delegate to this loader.
        self.loader = loader or loaders.DictLoader({})

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

        # The undefined type. When an identifier can not be resolved, the returned value
        # is `Undefined` or a subclass of `Undefined`.
        self.undefined: Type[Undefined] = undefined

        # Indicates if an undefined filter should raise an exception or be ignored.
        self.strict_filters: bool = strict_filters

        # Indicates if autoescape is enabled.
        self.autoescape: bool = autoescape

        # Tag register.
        self.tags: Dict[str, Tag] = {}

        # Filter register.
        self.filters: Dict[str, Callable[..., Any]] = {}

        # tolerance mode
        self.mode: Mode = tolerance

        # Template cache
        if cache_size and cache_size > 0 and not self.loader.caching_loader:
            self.cache: Optional[MutableMapping[Any, Any]] = LRUCache(cache_size)
            self.auto_reload: bool = auto_reload
        else:
            self.cache = None
            self.auto_reload = False

        # Common expression parsing functions that might be cached.
        self.expression_cache_size = expression_cache_size
        (
            self.parse_boolean_expression_value,
            self.parse_boolean_expression_value_with_parens,
            self.parse_conditional_expression_value,
            self.parse_conditional_expression_value_with_parens,
            self.parse_filtered_expression_value,
            self.parse_loop_expression_value,
        ) = self._get_expression_parsers(self.expression_cache_size)

        self.setup_tags_and_filters()

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
                self.strip_tags,
                # Necessary when replacing the standard output statement implementation.
                self.tags.get("statement"),
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

    def setup_tags_and_filters(self) -> None:
        """Add default tags and filters to this environment."""
        builtin.register(self)

    def parse(self, source: str) -> ast.ParseTree:
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
            parse_tree = self.parse(source)
        except (LiquidSyntaxError, TemplateInheritanceError) as err:
            err.filename = path
            err.source = source
            raise err
        except Exception as err:  # noqa: BLE001
            raise Error("unexpected liquid parsing error") from err
        return self.template_class(
            env=self,
            name=name,
            path=path,
            parse_tree=parse_tree,
            globals=self.make_globals(globals),
            matter=matter,
        )

    def get_template(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
    ) -> BoundTemplate:
        """Load and parse a template using the configured loader.

        Args:
            name: The template's name. The loader is responsible for interpreting
                the name. It could be the name of a file or some other identifier.
            globals: A mapping of render context variables attached to the
                resulting template.

        Raises:
            TemplateNotFound: If a template with the given name can not be found.
        """
        if self.cache is not None:
            cached = self.cache.get(name)
            if isinstance(cached, BoundTemplate) and (
                not self.auto_reload or cached.is_up_to_date
            ):
                cached.globals.update(self.make_globals(globals))
                return cached

        template = self.loader.load(self, name, globals=self.make_globals(globals))
        if self.cache is not None:
            self.cache[name] = template
        return template

    async def get_template_async(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
    ) -> BoundTemplate:
        """An async version of `get_template`."""
        if self.cache is not None:
            cached = self.cache.get(name)
            if isinstance(cached, BoundTemplate) and (
                not self.auto_reload or await cached.is_up_to_date_async()
            ):
                cached.globals.update(self.make_globals(globals))
                return cached

        template = await self.loader.load_async(
            self, name, globals=self.make_globals(globals)
        )
        if self.cache is not None:
            self.cache[name] = template
        return template

    def get_template_with_args(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        """Load and parse a template with arbitrary loader arguments.

        This method bypasses the environment's template cache. You should use a caching
        loader instead when the loader requires extra keyword arguments.

        _New in version 1.9.0._
        """
        return self.loader.load_with_args(self, name, globals, **kwargs)

    async def get_template_with_args_async(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,  # noqa: A002
        **kwargs: object,
    ) -> BoundTemplate:
        """An async version of `get_template_with_args`.

        _New in version 1.9.0._
        """
        return await self.loader.load_with_args_async(self, name, globals, **kwargs)

    def get_template_with_context(
        self,
        context: "Context",
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """Load and parse a template with reference to a render context.

        This method bypasses the environment's template cache. You should consider using
        a caching loader.
        """
        return self.loader.load_with_context(context, name, **kwargs)

    async def get_template_with_context_async(
        self,
        context: "Context",
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """An async version of `get_template_with_context`."""
        return await self.loader.load_with_context_async(context, name, **kwargs)

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
        context: Optional["Context"] = None,
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
        if context:
            template_source = self.loader.get_source_with_context(
                context=context, template_name=name, **kwargs
            )
        else:
            template_source = self.loader.get_source(self, template_name=name)

        return self.analyze_tags_from_string(
            template_source.source,
            name=template_source.filename,
            inner_tags=inner_tags,
        )

    async def analyze_tags_async(
        self,
        name: str,
        *,
        context: Optional["Context"] = None,
        inner_tags: Optional[InnerTagMap] = None,
        **kwargs: str,
    ) -> TagAnalysis:
        """An async version of `Environment.analyze_tags`."""
        if context:
            template_source = await self.loader.get_source_with_context_async(
                context=context, template_name=name, **kwargs
            )
        else:
            template_source = await self.loader.get_source_async(
                env=self, template_name=name
            )

        return self.analyze_tags_from_string(
            template_source.source,
            name=template_source.filename,
            inner_tags=inner_tags,
        )

    def make_globals(
        self, globals: Optional[Mapping[str, object]] = None  # noqa: A002
    ) -> Dict[str, object]:
        """Combine environment globals with template globals."""
        if globals:
            # Template globals take priority over environment globals.
            return {**self.globals, **globals}
        return dict(self.globals)

    def error(
        self,
        exc: Union[Type[Error], Error],
        msg: Optional[str] = None,
        linenum: Optional[int] = None,
    ) -> None:
        """Raise, warn or ignore the given exception according to the current mode."""
        if not isinstance(exc, Error):
            exc = exc(msg, linenum=linenum)
        elif not exc.linenum:
            exc.linenum = linenum

        if self.mode == Mode.STRICT:
            raise exc
        if self.mode == Mode.WARN:
            warnings.warn(
                str(exc), category=lookup_warning(exc.__class__), stacklevel=2
            )

    def set_expression_cache_size(self, maxsize: int = 0) -> None:
        """Create or replace cached versions of the common expression parsers.

        If `maxsize` is less than `1`, no expression caching will happen.

        Args:
            maxsize: The maximum size of each expression cache.
        """
        self.expression_cache_size = maxsize
        (
            self.parse_boolean_expression_value,
            self.parse_boolean_expression_value_with_parens,
            self.parse_conditional_expression_value,
            self.parse_conditional_expression_value_with_parens,
            self.parse_filtered_expression_value,
            self.parse_loop_expression_value,
        ) = self._get_expression_parsers(self.expression_cache_size)

    def _get_expression_parsers(
        self, cache_size: int = 0
    ) -> Tuple[
        Callable[[str], "BooleanExpression"],
        Callable[[str], "BooleanExpression"],
        Callable[[str], "FilteredExpression"],
        Callable[[str], "FilteredExpression"],
        Callable[[str], "FilteredExpression"],
        Callable[[str], "LoopExpression"],
    ]:
        if cache_size >= 1:
            return (
                lru_cache(maxsize=cache_size)(parse_boolean_expression),
                lru_cache(maxsize=cache_size)(parse_boolean_expression_with_parens),
                lru_cache(maxsize=cache_size)(parse_conditional_expression),
                lru_cache(maxsize=cache_size)(parse_conditional_expression_with_parens),
                lru_cache(maxsize=cache_size)(parse_filtered_expression),
                lru_cache(maxsize=cache_size)(parse_loop_expression),
            )
        return (
            parse_boolean_expression,
            parse_boolean_expression_with_parens,
            parse_conditional_expression,
            parse_conditional_expression_with_parens,
            parse_filtered_expression,
            parse_loop_expression,
        )


@lru_cache(maxsize=10)
def get_implicit_environment(
    tag_start_string: str,
    tag_end_string: str,
    statement_start_string: str,
    statement_end_string: str,
    strip_tags: bool,
    tolerance: Mode,
    loader: Optional[loaders.BaseLoader],
    undefined: Type[Undefined],
    strict_filters: bool,
    autoescape: bool,
    auto_reload: bool,
    cache_size: int,
    globals: Optional[Mapping[str, object]],  # noqa: A002
    template_comments: bool,
    comment_start_string: str,
    comment_end_string: str,
    expression_cache_size: int,
) -> Environment:
    """Return an `Environment` initialized with the given arguments."""
    return Environment(
        tag_start_string=tag_start_string,
        tag_end_string=tag_end_string,
        statement_start_string=statement_start_string,
        statement_end_string=statement_end_string,
        strip_tags=strip_tags,
        tolerance=tolerance,
        loader=loader,
        undefined=undefined,
        strict_filters=strict_filters,
        autoescape=autoescape,
        auto_reload=auto_reload,
        cache_size=cache_size,
        globals=globals,
        template_comments=template_comments,
        comment_start_string=comment_start_string,
        comment_end_string=comment_end_string,
        expression_cache_size=expression_cache_size,
    )


# `Template` is a factory function masquerading as a class. The desire to have an
# intuitive API and to please the static type checker outweighs this abuse of Python
# naming conventions. At least for now.


def Template(  # noqa: N802, D417
    source: str,
    tag_start_string: str = r"{%",
    tag_end_string: str = r"%}",
    statement_start_string: str = r"{{",
    statement_end_string: str = r"}}",
    strip_tags: bool = False,
    tolerance: Mode = Mode.STRICT,
    undefined: Type[Undefined] = Undefined,
    strict_filters: bool = True,
    autoescape: bool = False,
    auto_reload: bool = True,
    cache_size: int = 300,
    globals: Optional[Mapping[str, object]] = None,  # noqa: A002
    template_comments: bool = False,
    comment_start_string: str = "{#",
    comment_end_string: str = "#}",
    expression_cache_size: int = 0,
) -> BoundTemplate:
    """Parse a template, automatically creating an `Environment` to bind it to.

    Other than `source`, all arguments are passed to the implicit `Environment`,
    which might have been cached from previous calls to `Template`.

    Args:
        tag_start_string: The sequence of characters indicating the start of a
            liquid tag.
        tag_end_string: The sequence of characters indicating the end of a liquid
            tag.
        statement_start_string: The sequence of characters indicating the start of
            an output statement.
        statement_end_string: The sequence of characters indicating the end of an
            output statement.
        strip_tags: Has no effect. We don't support automatic whitespace stripping.
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
            output unless they've been explicitly marked as "safe". Requires the package
            Markupsafe.
        auto_reload: If `True`, loaders that have an `uptodate` callable will
            reload template source data automatically. For deployments where template
            sources don't change between service reloads, setting auto_reload to `False`
            can yield an increase in performance by avoiding calls to `uptodate`.
        cache_size: The capacity of the template cache in number of templates.
            If `cache_size` is `None` or less than `1`, it has the effect of setting
            `auto_reload` to `False`.
        expression_cache_size: The capacity of each of the common expression caches.
            A `cache_size` of `0` will disabling expression caching.
        globals: An optional mapping that will be added to the render context of any
            template loaded from this environment.
    """
    # Resorting to named arguments (repeated 3 times) as I've twice missed a bug
    # because of positional arguments.
    env = get_implicit_environment(
        tag_start_string=tag_start_string,
        tag_end_string=tag_end_string,
        statement_start_string=statement_start_string,
        statement_end_string=statement_end_string,
        strip_tags=strip_tags,
        tolerance=tolerance,
        loader=None,
        undefined=undefined,
        strict_filters=strict_filters,
        autoescape=autoescape,
        auto_reload=auto_reload,
        cache_size=cache_size,
        globals=None,
        template_comments=template_comments,
        comment_start_string=comment_start_string,
        comment_end_string=comment_end_string,
        expression_cache_size=expression_cache_size,
    )

    return env.from_string(source, globals=globals)
