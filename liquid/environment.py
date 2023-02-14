"""Shared configuration from which templates can be loaded and parsed."""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path

from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import Iterator
from typing import Mapping
from typing import MutableMapping
from typing import Optional
from typing import Type
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union

import warnings

from liquid.context import Undefined
from liquid.mode import Mode
from liquid.tag import Tag
from liquid.template import BoundTemplate
from liquid.lex import get_lexer
from liquid.parse import get_parser
from liquid.stream import TokenStream
from liquid.analyze_tags import InnerTagMap
from liquid.analyze_tags import TagAnalysis
from liquid.utils import LRUCache

from liquid.expressions import parse_boolean_expression
from liquid.expressions import parse_boolean_expression_with_parens
from liquid.expressions import parse_conditional_expression
from liquid.expressions import parse_conditional_expression_with_parens
from liquid.expressions import parse_filtered_expression
from liquid.expressions import parse_loop_expression

from liquid import ast
from liquid import builtin
from liquid import loaders

from liquid.exceptions import Error
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import lookup_warning
from liquid.exceptions import TemplateInheritanceError

if TYPE_CHECKING:  # pragma: no cover
    from liquid.expression import BooleanExpression
    from liquid.expression import FilteredExpression
    from liquid.expression import LoopExpression
    from liquid.context import Context
    from liquid.token import Token


# pylint: disable=too-many-instance-attributes
class Environment:
    """Shared configuration from which templates can be loaded and parsed.

    An ``Environment`` is where you might register custom tags and filters, or store
    global context variables that should be included with every template.

    :param tag_start_string: The sequence of characters indicating the start of a
        liquid tag. Defaults to ``{%``.
    :type tag_start_string: str
    :param tag_end_string: The sequence of characters indicating the end of a liquid
        tag. Defaults to ``%}``.
    :type tag_end_string: str
    :param statement_start_string: The sequence of characters indicating the start of
        an output statement. Defaults to ``{{``.
    :type statement_start_string: str
    :param statement_end_string: The sequence of characters indicating the end of an
        output statement. Defaults to ``}}``
    :type statement_end_string: str
    :param template_comments: If ``True``, enable template comments. Where, by default,
        anything between ``{#`` and ``#}`` is considered a comment. Defaults to
        ``False``.
    :type template_comments: bool
    :param comment_start_string: The sequence of characters indicating the start of a
        comment. Defaults to ``{#``. ``template_comments`` must be ``True`` for
        ``comment_start_string`` to have any effect.
    :type comment_start_string: str
    :param comment_end_string: The sequence of characters indicating the end of a
        comment. Defaults to ``#}``. ``template_comments`` must be ``True`` for
        ``comment_end_string`` to have any effect.
    :type comment_end_string: str
    :param tolerance: Indicates how tolerant to be of errors. Must be one of
        ``Mode.LAX``, ``Mode.WARN`` or ``Mode.STRICT``. Defaults to ``Mode.STRICT``.
    :type tolerance: Mode
    :param loader: A template loader. If you want to use the builtin "render" or
        "include" tags, a loader must be configured. Defaults to an empty
        :class:`liquid.loaders.DictLoader`.
    :type loader: liquid.loaders.BaseLoader
    :param undefined: A subclass of :class:`Undefined` that represents undefined values.
        Could be one of the built-in undefined types, :class:`Undefined`,
        :class:`DebugUndefined` or :class:`StrictUndefined`. Defaults to
        :class:`Undefined`, an undefined type that silently ignores undefined values.
    :type undefined: liquid.Undefined
    :param strict_filters: If ``True``, will raise an exception upon finding an
        undefined filter. Otherwise undefined filters are silently ignored. Defaults to
        ``True``.
    :type strict_filters: bool
    :param autoescape: If `True`, all context values will be HTML-escaped before output
        unless they've been explicitly marked as "safe". Requires the package
        Markupsafe. Defaults to ``False``.
    :type autoescape: bool
    :param auto_reload: If `True`, loaders that have an ``uptodate`` callable will
        reload template source data automatically. For deployments where template
        sources don't change between service reloads, setting auto_reload to `False` can
        yield an increase in performance by avoiding calls to ``uptodate``. Defaults to
        ``True``.
    :type auto_reload: bool
    :param cache_size: The capacity of the template cache in number of templates.
        Defaults to 300. If ``cache_size`` is ``None`` or less than ``1``, it has the
        effect of setting ``auto_reload`` to ``False``.
    :type cache_size: int
    :param expression_cache_size: The capacity of each of the common expression caches.
        Defaults to ``0``, disabling expression caching.
    :type expression_cache_size: int
    :param globals: An optional mapping that will be added to the context of any
        template loaded from this environment. Defaults to ``None``.
    :type globals: dict
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

    # Instances of ``template_class`` are returned from ``from_string``,
    # ``get_template`` and ``get_template_async``. It should be the ``BoundTemplate``
    # class or a subclass of it.
    template_class = BoundTemplate

    # pylint: disable=redefined-builtin too-many-arguments too-many-locals
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
        globals: Optional[Mapping[str, object]] = None,
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

        # An instance of a template loader implementing ``liquid.loaders.BaseLoader``.
        # ``get_template()`` will delegate to this loader.
        self.loader = loader or loaders.DictLoader({})

        # A mapping of template variable names to python objects. These variables will
        # be added to the global namespace of any template rendered from this
        # environment using ``from_string`` or ``get_template``.
        self.globals: Mapping[str, object] = globals or {}

        # Extended template comment syntax control.
        self.template_comments = template_comments
        self.comment_start_string = comment_start_string
        self.comment_end_string = comment_end_string
        if not self.template_comments:
            self.comment_start_string = ""
            self.comment_end_string = ""

        # The undefined type. When an identifier can not be resolved, the returned value
        # is ``Undefined`` or a subclass of ``Undefined``.
        self.undefined = undefined

        # Indicates if an undefined filter should raise an exception or be ignored.
        self.strict_filters = strict_filters

        # Indicates if autoescape is enabled.
        self.autoescape = autoescape

        # Tag register.
        self.tags: Dict[str, Tag] = {}

        # Filter register.
        self.filters: Dict[str, Callable[..., Any]] = {}

        # tolerance mode
        self.mode = tolerance

        # Template cache
        if cache_size and cache_size > 0:
            self.cache: MutableMapping[Any, Any] = LRUCache(cache_size)
            self.auto_reload = auto_reload
        else:
            self.cache = {}
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

        builtin.register(self)

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
        """Register a liquid tag with the environment. Built-in tags are registered for
        you automatically with every new :class:`Environment`.

        :param tag: The tag to register.
        :type tag: Type[Tag]
        """
        self.tags[tag.name] = tag(self)

    def add_filter(self, name: str, func: Callable[..., Any]) -> None:
        """Register a filter function with the environment.

        :param name: The filter's name. Does not need to match the function name. This
            is what you'll use to apply the filter to an expression in a liquid
            template.
        :type name: str
        :param func: Any callable that accepts at least one argument, the result of the
            expression the filter is applied to. If the filter needs access to the
            environment or render context, you probably want to make ``func`` a class
            that inherits from :class:`liquid.filter.Filter`, and override the
            ``__call__`` method. All builtin filters are implemented in this way.
        :type func: Callable[..., Any]
        """
        self.filters[name] = func

    def parse(self, source: str) -> ast.ParseTree:
        """Parse the given string as a liquid template.

        More often than not you'll want to use :meth:`Environment.from_string` instead.
        """
        parser = get_parser(self)
        token_iter = self.tokenizer()(source)
        return parser.parse(TokenStream(token_iter))

    # pylint: disable=redefined-builtin
    def from_string(
        self,
        source: str,
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Mapping[str, object]] = None,
        matter: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """Parse the given string as a liquid template.

        :param source: The liquid template source code.
        :type source: str
        :param name: Optional name of the template. Available as ``Template.name``.
            Defaults to the empty string.
        :type name: str
        :param path: Optional path or identifier to the origin of the template. Defaults
            to ``None``.
        :type path: str, pathlib.Path
        :param globals: An optional mapping of context variables made available every
            time the resulting template is rendered. Defaults to ``None``.
        :type globals: dict
        :param matter: Optional mapping containing variables associated with the
            template. Could be "front matter" or other meta data.
        :type matter: Optional[Mapping[str, object]]
        :returns: A parsed template ready to be rendered.
        :rtype: liquid.template.BoundTemplate
        """
        try:
            parse_tree = self.parse(source)
        except (LiquidSyntaxError, TemplateInheritanceError) as err:
            err.filename = path
            err.source = source
            raise err
        except Exception as err:
            raise Error("unexpected liquid parsing error") from err
        return self.template_class(
            env=self,
            name=name,
            path=path,
            parse_tree=parse_tree,
            globals=self.make_globals(globals),
            matter=matter,
        )

    # pylint: disable=redefined-builtin
    def get_template(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """Load and parse a template using the configured loader.

        :param name: The template's name. The loader is responsible for interpreting
            the name. It could be the name of a file or some other identifier.
        :param globals: A mapping of context variables made available every time the
            resulting template is rendered.
        :returns: A parsed template ready to be rendered.
        :rtype: liquid.template.BoundTemplate
        :raises:
            :class:`liquid.exceptions.TemplateNotFound`: if a template with the given
            name can not be found.
        """
        template = self._check_cache(name, globals)

        if not template:
            template = self.loader.load(self, name, globals=self.make_globals(globals))
            self.cache[name] = template

        return template

    async def get_template_async(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """An async version of ``get_template``."""
        template = self.cache.get(name)

        if isinstance(template, BoundTemplate) and (
            not self.auto_reload or await template.is_up_to_date_async()
        ):
            template.globals.update(self.make_globals(globals))
        else:
            template = await self.loader.load_async(
                self,
                name,
                globals=self.make_globals(globals),
            )
            self.cache[name] = template

        return template

    def get_template_with_context(
        self,
        context: "Context",
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """Load and parse a template using the configured loader, optionally referencing
        a render context."""
        # No template caching. How would we know what context variables a loader needs?
        # A custom loader that uses context could implement its own cache.
        return self.loader.load_with_context(context, name, **kwargs)

    async def get_template_with_context_async(
        self,
        context: "Context",
        name: str,
        **kwargs: str,
    ) -> BoundTemplate:
        """An async version of ``get_template_with_context``."""
        return await self.loader.load_with_context_async(context, name, **kwargs)

    def analyze_tags_from_string(
        self,
        source: str,
        name: str = "<string>",
        *,
        inner_tags: Optional[InnerTagMap] = None,
    ) -> TagAnalysis:
        """Analyze tags in template source text against those registered with this
        environment.

        Unlike template static or contextual analysis, a tag audit does not parse the
        template source text into an AST, nor does it attempt to load partial templates
        from ``{% include %}`` or `{% render %}` tags.

        :param source: The source text of the template.
        :type source: str
        :param name: A name or identifier for the template. Defaults to "<string>".
        :type name: str
        :param inner_tags: A mapping of block tags to a list of allowed "inner" tags for
            the block. For example, ``{% if %}`` blocks are allowed to contain
            ``{% elsif %}`` and ``{% else %}`` tags.
        :type inner_tags: Mapping[str, Iterable[str]]
        :returns: A tag audit including the location of any unknown tags and any
            unbalanced block tags.
        :rtype: :class:`liquid.analyze_tags.TagAnalysis`
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
        template's source text. See also :meth:`liquid.template.BoundTemplate.analyze`.

        :param name: The template's name or identifier, as you would use with
            :meth:`Environment.get_template`. Use :meth:`Environment.analyze_tags_from_string`
            to audit tags in template text without using a template loader.
        :type name: str
        :param context: An optional render context the loader might use to modify the
            template search space. If given, uses
            :meth:`liquid.loaders.BaseLoader.get_source_with_context` from the current
            loader.
        :type context: Optional[:class:`liquid.Context`]
        :param inner_tags: A mapping of block tags to a list of allowed "inner" tags for
            the block. For example, ``{% if %}`` blocks are allowed to contain
            ``{% elsif %}`` and ``{% else %}`` tags.
        :type inner_tags: Mapping[str, Iterable[str]]
        :returns: A tag audit including the location of any unknown tags and any
            unbalanced block tags.
        :rtype: :class:`liquid.analyze_tags.TagAnalysis`
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
        """An async version of :meth:`Environment.analyze_tags`."""
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

    def _check_cache(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> Optional[BoundTemplate]:
        _cached = self.cache.get(name)

        if isinstance(_cached, BoundTemplate) and (
            not self.auto_reload or _cached.is_up_to_date
        ):
            _cached.globals.update(self.make_globals(globals))
            return _cached
        return None

    # pylint: disable=redefined-builtin
    def make_globals(
        self, globals: Optional[Mapping[str, object]] = None
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
        """Create or replace cached versions of the common expression parsers. If
        `maxsize` is less than ``1``, no expression caching will happen.

        :param maxsize: The maximum size of each expression cache.
        :type maxsize: int
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


# pylint: disable=redefined-builtin too-many-arguments too-many-locals
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
    globals: Optional[Mapping[str, object]],
    template_comments: bool,
    comment_start_string: str,
    comment_end_string: str,
    expression_cache_size: int,
) -> Environment:
    """Return an :class:`Environment` initialized with the given arguments."""
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


# ``Template`` is a factory function masquerading as a class. The desire to have an
# intuitive API and to please the static type checker outweighs this abuse of Python
# naming conventions. At least for now.


# pylint: disable=redefined-builtin too-many-arguments invalid-name too-many-locals
def Template(
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
    globals: Optional[Mapping[str, object]] = None,
    template_comments: bool = False,
    comment_start_string: str = "{#",
    comment_end_string: str = "#}",
    expression_cache_size: int = 0,
) -> BoundTemplate:
    """Returns a :class:`liquid.template.BoundTemplate`, automatically creating an
    :class:`Environment` to bind it to.

    Other than `source`, all arguments are passed to the implicit :class:`Environment`,
    which might have been cached from previous calls to :func:`Template`.

    :param source: A Liquid template source string.
    :type source: str
    :param tag_start_string: The sequence of characters indicating the start of a
        liquid tag. Defaults to ``{%``.
    :type tag_start_string: str
    :param tag_end_string: The sequence of characters indicating the end of a liquid
        tag. Defaults to ``%}``.
    :type tag_end_string: str
    :param statement_start_string: The sequence of characters indicating the start of
        an output statement. Defaults to ``{{``.
    :type statement_start_string: str
    :param statement_end_string: The sequence of characters indicating the end of an
        output statement. Defaults to ``}}``
    :type statement_end_string: str
    :param template_comments: If ``True``, enable template comments. Where, by default,
        anything between ``{#`` and ``#}`` is considered a comment. Defaults to
        ``False``.
    :type template_comments: bool
    :param comment_start_string: The sequence of characters indicating the start of a
        comment. Defaults to ``{#``. ``template_comments`` must be ``True`` for
        ``comment_start_string`` to have any effect.
    :type comment_start_string: str
    :param comment_end_string: The sequence of characters indicating the end of a
        comment. Defaults to ``#}``. ``template_comments`` must be ``True`` for
        ``comment_end_string`` to have any effect.
    :type comment_end_string: str
    :param tolerance: Indicates how tolerant to be of errors. Must be one of
        `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`. Defaults to ``Mode.STRICT``.
    :type tolerance: Mode
    :param undefined: A subclass of :class:`Undefined` that represents undefined values.
        Could be one of the built-in undefined types, :class:`Undefined`,
        :class:`DebugUndefined` or :class:`StrictUndefined`. Defaults to
        :class:`Undefined`, an undefined type that silently ignores undefined values.
    :type undefined: Undefined
    :param strict_filters: If ``True``, will raise an exception upon finding an
        undefined filter. Otherwise undefined filters are silently ignored. Defaults to
        ``True``.
    :type strict_filters: bool
    :param autoescape: If `True`, all context values will be HTML-escaped before output
        unless they've been explicitly marked as "safe". Requires the package
        Markupsafe. Defaults to ``False``.
    :type autoescape: bool
    :param auto_reload: If `True`, loaders that have an ``uptodate`` callable will
        reload template source data automatically. For deployments where template
        sources don't change between service reloads, setting auto_reload to `False` can
        yield an increase in performance by avoiding calls to ``uptodate``. Defaults to
        ``True``.
    :type auto_reload: bool
    :param cache_size: The capacity of the template cache in number of templates.
        Defaults to 300. If ``cache_size`` is ``None`` or less than ``1``, it has the
        effect of setting ``auto_reload`` to ``False``.
    :type cache_size: int
    :param expression_cache_size: The capacity of each of the common expression caches.
        Defaults to ``0``, disabling expression caching.
    :type expression_cache_size: int
    :param globals: An optional mapping that will be added to the context of any
        template loaded from this environment. Defaults to ``None``.
    :type globals: dict
    :rtype: BoundTemplate
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
