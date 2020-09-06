"""Shared configuration from which templates can be loaded and parsed."""

from __future__ import annotations
from collections import ChainMap
from io import StringIO
from pathlib import Path
from typing import Callable, Dict, Any, Type, Union, Optional, TextIO, Mapping

import warnings

from liquid.mode import Mode, mode
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import get_lexer
from liquid.parse import get_parser
from liquid.ast import ParseTree
from liquid import builtin
from liquid.builtin.drops import TemplateDrop
from liquid.exceptions import Error, lookup_warning, LiquidInterrupt, LiquidSyntaxError
from liquid.utils import LRUCache


class Template:
    """A loaded and parsed liquid template.

    Rather than instantiating templates directly, the recommened way to create
    templates is by calling `get_template` or `from_string` from an `Environment`.
    """

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        env: Environment,
        parse_tree: ParseTree,
        name: str = "",
        path: Optional[Path] = None,
        globals: Optional[Mapping[str, Any]] = None,
        uptodate: Optional[Callable[[], bool]] = None,
    ):
        self.env = env
        self.tree = parse_tree
        self._globals = globals or {}
        self.name = name
        self.path = path
        self.uptodate = uptodate

        self.drop = TemplateDrop(self.name, self.path)

    def render(self, *args, **kwargs) -> str:
        """Render the template with `args` and `kwargs` included in the render context.

        Accepts the same arguments as the `dict` constructor.
        """
        _vars = dict(*args, **kwargs)
        context = Context(ChainMap(self._globals, _vars), filters=self.env.filters)
        buf = StringIO()
        self.render_with_context(context, buf)
        return buf.getvalue()

    def render_with_context(
        self,
        context: Context,
        buffer: TextIO,
        *args,
        partial: bool = False,
        block_scope=False,
        **kwargs,
    ):
        """Render the template using an existing context and output buffer.

        Args:
            context: A render context.
            buffer: File-like object to which rendered text is written.
            partial: If `True`, indicates that the current template has been
                included using either a "render" or "include" tag.
            block_scope: If `True`, indicates that assigns, breaks and continues
                from this template will not leak into the parent context.
        """
        # "template" could get overriden from args/kwargs, "partial" will not.
        namespace: Dict[str, Any] = {
            "template": self.drop,
            **dict(*args, **kwargs),
            "partial": partial,
        }
        ctx = context.extend(namespace=namespace)

        for node in self.tree.statements:
            with mode(self.env.mode, node.tok.linenum, filename=self.path):
                try:
                    node.render(ctx, buffer)
                except LiquidInterrupt as err:
                    # If this is an "included" template, the for loop could be in a
                    # parent template. Convert the interrupt to a syntax error if
                    # there is no parent.
                    if not partial or block_scope:
                        raise LiquidSyntaxError(f"unexpected '{err}'") from err
                    raise
                except Error as err:
                    self.env.error(err, linenum=node.tok.linenum)

    @property
    def is_up_to_date(self):
        """False if the template was modified since it was last parsed,
        True otherwise."""
        if not self.uptodate:
            return True
        return self.uptodate()

    def __repr__(self):
        return f"Template(name='{self.name}', path='{self.path}', uptodate={self.is_up_to_date})"


# pylint: disable=too-many-instance-attributes
class Environment:
    """Shared configuration from which templates can be loaded and parsed.

    An `Environment` is also where you'd register custom tags and filters.

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
        tollerence: Indicates how tollerent to be of errors. Must be one of
            `Mode.LAX`, `Mode.WARN` or `Mode.STRICT`.
        loader: A template loader. If you want to use the builtin "render" or
            "include" tags, a loader must be configured.
        globals: A mapping that will be added to the global context of any
            template loaded from this environment.
    """

    # pylint: disable=redefined-builtin too-many-arguments
    def __init__(
        self,
        tag_start_string: str = r"{%",
        tag_end_string: str = r"%}",
        statement_start_string: str = r"{{",
        statement_end_string: str = r"}}",
        strip_tags: bool = False,
        tollerence: Mode = Mode.STRICT,
        loader=None,
        globals: Mapping[[str], Any] = None,
    ):
        self.tag_start_string = tag_start_string
        self.tag_end_string = tag_end_string
        self.statement_start_string = statement_start_string
        self.statement_end_string = statement_end_string
        self.strip_tags = strip_tags
        self.loader = loader
        self.globals = globals or {}

        # Tag register.
        self.tags: Dict[str, Tag] = {}

        # Filter register.
        self.filters: Dict[str, Callable[..., Any]] = {}

        # Tollerence mode
        self.mode = tollerence

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
                builtin filters are implmented in this way.
        """
        # TODO: Warn if overriding an existing filter.
        self.filters[name] = func

    def parse(self, source: str) -> ParseTree:
        """Parse the given string as a liquid template.

        More often than not you'll want to use `Environment.from_string` instead.
        """
        lexer = get_lexer(self)
        parser = get_parser(self)

        token_iter = lexer.tokenize(source)
        parse_tree = parser.parse(token_iter)
        return parse_tree

    # pylint: disable=redefined-builtin
    def from_string(
        self,
        source: str,
        name: str = "",
        path: Path = None,
        globals: Mapping[str, Any] = None,
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
    def get_template(self, name: str, globals: Dict[str, Any] = None) -> Template:
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
        if template and template.is_up_to_date:
            # FIXME: Copy the cached template with new globals.
            # Or just cache the parse tree.
            return template

        template = self.loader.load(self, name, globals=self.make_globals(globals))
        self.cache[name] = template
        return template

    # pylint: disable=redefined-builtin
    def make_globals(self, globals: Mapping[str, Any] = None) -> Mapping[str, Any]:
        """Combine environment globals with template globals."""
        if globals:
            return {**self.globals, **globals}
        return {**self.globals}

    def error(
        self, exc: Union[Type[Error], Error], msg: str = None, linenum: int = None
    ):
        if not isinstance(exc, Error):
            exc = exc(msg, linenum=linenum)
        elif not exc.linenum:
            exc.linenum = linenum

        if self.mode == Mode.STRICT:
            raise exc
        if self.mode == Mode.WARN:
            warnings.warn(str(exc), category=lookup_warning(exc.__class__))
