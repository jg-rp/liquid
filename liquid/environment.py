"""Shared configuration from which templates can be loaded and parsed."""

from __future__ import annotations
from pathlib import Path

from typing import Callable
from typing import Dict
from typing import Any
from typing import Type
from typing import Union
from typing import Optional
from typing import Mapping

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
from liquid.exceptions import lookup_warning


# pylint: disable=too-many-instance-attributes
class Environment:
    """Shared configuration from which templates can be loaded and parsed.

    An ``Environment`` is also where you'd register custom tags and filters.

    :param tag_start_string: The sequence of characters indicating the start of a
        liquid tag.
    :param tag_end_string: The sequence of characters indicating the end of a liquid
        tag.
    :param statement_start_string: The sequence of characters indicating the start of
        an output statement.
    :param statement_end_string: The sequence of characters indicating the end of an
        output statement.
    :param strip_tags: If `True` will strip leading and trailing whitespace from all
        tags, regardless of whitespace control characters.
    :param tolerance: Indicates how tolerant to be of errors. Must be one of
        `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
    :param loader: A template loader. If you want to use the builtin "render" or
        "include" tags, a loader must be configured.
    :param globals: A mapping that will be added to the context of any template loaded
        from this environment.
    :param undefined: A subclass of :class:`Undefined` that represents undefined values.
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
        globals: Optional[Mapping[str, object]] = None,
        undefined: Type[Undefined] = Undefined,
    ):
        self.tag_start_string = tag_start_string
        self.tag_end_string = tag_end_string
        self.statement_start_string = statement_start_string
        self.statement_end_string = statement_end_string
        self.strip_tags = strip_tags
        self.loader = loader or loaders.DictLoader({})
        self.globals: Mapping[str, object] = globals or {}

        #
        self.undefined = undefined

        # Tag register.
        self.tags: Dict[str, Tag] = {}

        # Filter register.
        self.filters: Dict[str, Callable[..., Any]] = {}

        # tolerance mode
        self.mode = tolerance

        # Template cache
        self.cache = LRUCache(300)

        self.template_class = BoundTemplate

        builtin.register(self)

    def __hash__(self):
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
        """Register a liquid tag with the environment."""
        self.tags[tag.name] = tag(self)

    def add_filter(self, name: str, func: Callable[..., Any]) -> None:
        """Register a filter function with the environment.

        :param name: The filter's name. Does not need to match the function name. This
            is what you'll use to apply the filter to an expression in a liquid
            template.
        :param func: Any callable that accepts at least one argument, the result of the
            expression the filter is applied to.

            If the filter needs access to the environment or render context, you
            probably want to make `func` a class that inherits from `liquid.Filter`, and
            override the `__call__` method. All builtin filters are implemented in this
            way.
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
        path: Optional[Path] = None,
        globals: Optional[Mapping[str, object]] = None,
    ) -> BoundTemplate:
        """Parse the given string as a liquid template.

        `name` and `path` are passed to the `Template` constructor and will be
        used to populate the template's `TemplateDrop`.

        :param source: Liquid template source.
        :param name: Name of the template.
        :param path: Location of the template.
        :param globals: A mapping of context variables made available every time the
            template is rendered.
        :returns: A parsed template ready to be rendered.
        """
        parse_tree = self.parse(source)
        return self.template_class(
            env=self,
            name=name,
            path=path,
            parse_tree=parse_tree,
            globals=self.make_globals(globals),
        )

    # pylint: disable=redefined-builtin
    def get_template(
        self, name: str, globals: Optional[Mapping[str, object]] = None
    ) -> BoundTemplate:
        """Load and parse a template using the configured loader.

        :param name: The template's name. The loader is responsible for interpretting
            the name.
        :param globals: A mapping of context variables made available every time the
            resulting template is rendered.
        :returns: A parsed template ready to be rendered.
        """
        template = self.cache.get(name)

        if isinstance(template, BoundTemplate) and template.is_up_to_date:
            # Copy the cached template with new globals.
            return self.template_class(
                env=self,
                name=template.name,
                path=template.path,
                parse_tree=template.tree,
                globals=self.make_globals(globals),
            )

        template = self.loader.load(self, name, globals=self.make_globals(globals))
        self.cache[name] = template
        return template

    # pylint: disable=redefined-builtin
    def make_globals(
        self, globals: Optional[Mapping[str, object]] = None
    ) -> Mapping[str, object]:
        """Combine environment globals with template globals."""
        if globals:
            _globals: Dict[str, object] = {**self.globals, **globals}
        else:
            _globals: Dict[str, object] = {**self.globals}
        return _globals

    def error(
        self,
        exc: Union[Type[Error], Error],
        msg: Optional[str] = None,
        linenum: Optional[int] = None,
    ) -> None:
        if not isinstance(exc, Error):
            exc = exc(msg, linenum=linenum)
        elif not exc.linenum:
            exc.linenum = linenum

        if self.mode == Mode.STRICT:
            raise exc
        if self.mode == Mode.WARN:
            warnings.warn(str(exc), category=lookup_warning(exc.__class__))


_implicit_environments = LRUCache(10)


def get_implicit_environment(*args):
    """Return an :class:`Environment` initialized with the given arguments."""
    try:
        return _implicit_environments[args]
    except KeyError:
        env = Environment(*args)
        _implicit_environments[args] = env
        return env


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
    globals: Optional[Mapping[str, object]] = None,
    undefined: Type[Undefined] = Undefined,
) -> BoundTemplate:
    """A :class:`BoundTemplate` factory.

    :param source: A Liquid template source string.
    :param tag_start_string: The sequence of characters indicating the start of a
        liquid tag.
    :param tag_end_string: The sequence of characters indicating the end of a liquid
        tag.
    :param statement_start_string: The sequence of characters indicating the start of
        an output statement.
    :param statement_end_string: The sequence of characters indicating the end of an
        output statement.
    :param strip_tags: If `True` will strip leading and trailing whitespace from all
        tags, regardless of whitespace control characters.
    :param tolerance: Indicates how tolerant to be of errors. Must be one of
        `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
    :param loader: A template loader. If you want to use the builtin "render" or
        "include" tags, a loader must be configured.
    :param globals: A mapping that will be added to the context of any template loaded
        from this environment.
    :param undefined: A subclass of :class:`Undefined` that represents undefined values.
    """
    env = get_implicit_environment(
        tag_start_string,
        tag_end_string,
        statement_start_string,
        statement_end_string,
        strip_tags,
        tolerance,
        undefined,
    )

    return env.from_string(source, globals=globals)
