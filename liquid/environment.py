"""Shared configuration from which templates can be loaded and parsed."""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path

from typing import Callable
from typing import Dict
from typing import Any
from typing import Type
from typing import Union
from typing import Optional
from typing import Mapping
from typing import MutableMapping

import warnings

from liquid.context import Undefined
from liquid.mode import Mode
from liquid.tag import Tag
from liquid.template import BoundTemplate
from liquid.lex import get_lexer
from liquid.stream import TokenStream
from liquid.parse import get_parser
from liquid.utils import LRUCache

from liquid import ast
from liquid import builtin
from liquid import loaders

from liquid.exceptions import Error
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import lookup_warning


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
    :param globals: An optional mapping that will be added to the context of any
        template loaded from this environment. Defaults to ``None``.
    :type globals: dict
    """

    # pylint: disable=redefined-builtin too-many-arguments
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
    ):
        self.tag_start_string = tag_start_string
        self.tag_end_string = tag_end_string
        self.statement_start_string = statement_start_string
        self.statement_end_string = statement_end_string
        self.strip_tags = strip_tags
        self.loader = loader or loaders.DictLoader({})
        self.globals: Mapping[str, object] = globals or {}

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

        self.template_class = BoundTemplate

        builtin.register(self)

    def __hash__(self) -> int:
        return hash(
            (
                self.statement_start_string,
                self.statement_end_string,
                self.tag_start_string,
                self.tag_end_string,
                self.mode,
                self.strip_tags,
            )
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

        More often than not you'll want to use `Environment.from_string` instead.
        """
        tokenize = get_lexer(
            self.tag_start_string,
            self.tag_end_string,
            self.statement_start_string,
            self.statement_end_string,
        )
        parser = get_parser(self)

        token_iter = tokenize(source)
        parse_tree = parser.parse(TokenStream(token_iter))
        return parse_tree

    # pylint: disable=redefined-builtin
    def from_string(
        self,
        source: str,
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Mapping[str, object]] = None,
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
        :returns: A parsed template ready to be rendered.
        :rtype: liquid.template.BoundTemplate
        """
        try:
            parse_tree = self.parse(source)
        except LiquidSyntaxError as err:
            err.filename = path
            err.source = source
            raise err
        return self.template_class(
            env=self,
            name=name,
            path=path,
            parse_tree=parse_tree,
            globals=self.make_globals(globals),
        )

    # pylint: disable=redefined-builtin
    def get_template(
        self,
        name: str,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """Load and parse a template using the configured loader.

        :param name: The template's name. The loader is responsible for interpretting
            the name.
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
            _globals = {**self.globals, **globals}
        else:
            _globals = {**self.globals}
        return _globals

    def error(
        self,
        exc: Union[Type[Error], Error],
        msg: Optional[str] = None,
        linenum: Optional[int] = None,
    ) -> None:
        """Raise ,warn or ignore the given exception according to the current mode."""
        if not isinstance(exc, Error):
            exc = exc(msg, linenum=linenum)
        elif not exc.linenum:
            exc.linenum = linenum

        if self.mode == Mode.STRICT:
            raise exc
        if self.mode == Mode.WARN:
            warnings.warn(str(exc), category=lookup_warning(exc.__class__))


@lru_cache(maxsize=10)
def get_implicit_environment(*args: Any) -> Environment:
    """Return an :class:`Environment` initialized with the given arguments."""
    return Environment(*args)


# `Template` is a factory function masquerading as a class. The desire to have
# an intuitive API and to please the static type checker outweighs this abuse of
# Python naming conventions. At least for now.

# pylint: disable=redefined-builtin too-many-arguments invalid-name
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
    :param globals: An optional mapping that will be added to the context of any
        template loaded from this environment. Defaults to ``None``.
    :type globals: dict
    """
    env = get_implicit_environment(
        tag_start_string,
        tag_end_string,
        statement_start_string,
        statement_end_string,
        strip_tags,
        None,  # loader
        tolerance,
        undefined,
        strict_filters,
        autoescape,
        auto_reload,
        cache_size,
    )

    return env.from_string(source, globals=globals)
