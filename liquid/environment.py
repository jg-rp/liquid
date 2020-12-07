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

from liquid.mode import Mode
from liquid.tag import Tag
from liquid.template import Template
from liquid.lex import get_lexer
from liquid.stream import TokenStream
from liquid.parse import get_parser

from liquid import ast
from liquid import builtin
from liquid import loaders

from liquid.exceptions import Error
from liquid.exceptions import lookup_warning

from liquid.utils import LRUCache


# pylint: disable=too-many-instance-attributes
class Environment:
    """Shared configuration from which templates can be loaded and parsed.

    An ``Environment`` is also where you'd register custom tags and filters.

    Args:
        tag_start_string: The sequence of characters indicating the start of a
            liquid tag.
        tag_end_string: The sequence of characters indicating the end of a
            liquid tag.
        statement_start_string: The sequence of characters indicating the start
            of an output statement.
        statement_end_string: The sequence of characters indicating the end
            of an output statement.
        strip_tags: If `True` will strip preceding and trailing whitespace from
            all tags, regardless of whitespace control characters.
        tolerance: Indicates how tolerant to be of errors. Must be one of
            `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
        loader: A template loader. If you want to use the builtin "render" or
            "include" tags, a loader must be configured.
        globals: A mapping that will be added to the context of any template
            loaded from this environment.
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
    ):
        self.tag_start_string = tag_start_string
        self.tag_end_string = tag_end_string
        self.statement_start_string = statement_start_string
        self.statement_end_string = statement_end_string
        self.strip_tags = strip_tags
        self.loader = loader or loaders.DictLoader({})
        self.globals: Mapping[str, object] = globals or {}

        # Tag register.
        self.tags: Dict[str, Tag] = {}

        # Filter register.
        self.filters: Dict[str, Callable[..., Any]] = {}

        # tolerance mode
        self.mode = tolerance

        # Template cache
        self.cache = LRUCache(300)

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

        Args:
            name: The filter's name. Does not need to match the function name.
                This is what you'll use to apply the filter to an expression in
                a liquid template.
            func: Any callable that accepts at least one argument, the result
                of the expression the filter is applied to.

                If the filter needs access to the environment or render
                context, you probably want to make `func` a class that inherits
                from `liquid.Filter`, and override the `__call__` method. All
                builtin filters are implemented in this way.
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
    ) -> Template:
        """Parse the given string as a liquid template.

        `name` and `path` are passed to the `Template` constructor and will be
        used to populate the template's `TemplateDrop`.

        Args:
            source: Liquid template source.
            name: Name of the template.
            path: Location of the template.
            globals: A mapping of context variables made available every time
                the template is rendered.
        Returns:
            A parsed template ready to be rendered.
        """
        parse_tree = self.parse(source)
        return Template(
            env=self,
            name=name,
            path=path,
            parse_tree=parse_tree,
            globals=self.make_globals(globals),
        )

    # pylint: disable=redefined-builtin
    def get_template(
        self, name: str, globals: Optional[Mapping[str, object]] = None
    ) -> Template:
        """Load and parse a template using the configured loader.

        Args:
            name: The template's name. The loader is responsible for
                interpretting the name.
            globals: A mapping of context variables made available every time
                the resulting template is rendered.
        Returns:
            A parsed template ready to be rendered.
        """
        template = self.cache.get(name)

        if isinstance(template, Template) and template.is_up_to_date:
            # Copy the cached template with new globals.
            return Template(
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
