"""Liquid template definition."""

from __future__ import annotations

from collections import ChainMap
from collections import abc

from io import StringIO
from pathlib import Path

from typing import Awaitable
from typing import Dict
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import Optional
from typing import TextIO
from typing import Union
from typing import TYPE_CHECKING

from liquid.context import Context

from liquid.exceptions import LiquidInterrupt
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import Error


if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid.ast import ParseTree
    from liquid.loaders import UpToDate


class BoundTemplate:
    """A liquid template that has been parsed and is bound to a
    :class:`liquid.Environment`.

    You probably don't want to be instantiate :class:`BoundTemplate` directly. Instead,
    use :meth:`liquid.Environment.from_string` or
    :meth:`liquid.Environment.get_template`.

    :param env: The environment this template is bound to.
    :type env: liquid.Environment
    :param parse_tree: The parse tree representing this template.
    :type parse_tree: liquid.ast.ParseTree
    :param name: Optional name of the template. Defaults to an empty string.
    :type name: str
    :param path: Optional origin path or identifier for the template.
    :type path: Optional[Union[str, Path]]
    :param uptodate: Optional callable that will return ``True`` if the template is up
        to date, or ``False`` if it needs to be reloaded. Defaults to ``None``.
    :type uptodate: Optional[Callable[[], bool]]
    """

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        env: Environment,
        parse_tree: ParseTree,
        name: str = "",
        path: Optional[Union[str, Path]] = None,
        globals: Optional[Dict[str, Any]] = None,
        uptodate: UpToDate = None,
    ):
        self.env = env
        self.tree = parse_tree
        self.globals = globals or {}
        self.name = name
        self.path = path
        self.uptodate = uptodate

    def render(self, *args: Any, **kwargs: Any) -> str:
        """Render the template with `args` and `kwargs` included in the render context.

        Accepts the same arguments as the :class:`dict` constructor.
        """
        _vars: Dict[str, object] = dict(*args, **kwargs)
        context = Context(self.env, ChainMap(_vars, self.globals))

        buf = StringIO()
        self.render_with_context(context, buf)
        return buf.getvalue()

    async def render_async(self, *args: Any, **kwargs: Any) -> str:
        """An async version of :meth:`liquid.template.BoundTemplate.render`."""
        _vars: Dict[str, object] = dict(*args, **kwargs)
        context = Context(self.env, ChainMap(_vars, self.globals))

        buf = StringIO()
        await self.render_with_context_async(context, buf)
        return buf.getvalue()

    def render_with_context(
        self,
        context: Context,
        buffer: TextIO,
        *args: Any,
        partial: bool = False,
        block_scope: bool = False,
        **kwargs: Any,
    ) -> None:
        """Render the template using an existing context and output buffer.

        ``args`` and ``kwargs`` are passed to the :class:`dict` constructor. The
        resulting dictionary is added to the render context.

        :param context: A render context.
        :param buffer: File-like object to which rendered text is written.
        :param partial: If `True`, indicates that the current template has been
            included using either a "render" or "include" tag. Defaults to ``False``.
        :param block_scope: If `True`, indicates that assigns, breaks and continues
            from this template will not leak into the parent context. Defaults to
            ``False``.
        """
        # "template" could get overridden from args/kwargs, "partial" will not.
        namespace = self._make_globals(partial, args, kwargs)

        with context.extend(namespace=namespace):
            for node in self.tree.statements:
                try:
                    node.render(context, buffer)
                except LiquidInterrupt as err:
                    # If this is an "included" template, there could be a for loop
                    # in a parent template. A for loop that could be interrupted
                    # from an included template.
                    #
                    # Convert the interrupt to a syntax error if there is no parent.
                    if not partial or block_scope:
                        self.env.error(
                            LiquidSyntaxError(
                                f"unexpected '{err}'", linenum=node.token().linenum
                            )
                        )
                    else:
                        raise
                except Error as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, linenum=node.token().linenum)

    async def render_with_context_async(
        self,
        context: Context,
        buffer: TextIO,
        *args: Any,
        partial: bool = False,
        block_scope: bool = False,
        **kwargs: Any,
    ) -> None:
        """An async version of :meth:`liquid.template.BoundTemplate.render_with_context`."""
        # "template" could get overridden from args/kwargs, "partial" will not.
        namespace = self._make_globals(partial, args, kwargs)

        with context.extend(namespace=namespace):
            for node in self.tree.statements:
                try:
                    await node.render_async(context, buffer)
                except LiquidInterrupt as err:
                    # If this is an "included" template, there could be a for loop
                    # in a parent template. A for loop that could be interrupted
                    # from an included template.
                    #
                    # Convert the interrupt to a syntax error if there is no parent.
                    if not partial or block_scope:
                        self.env.error(
                            LiquidSyntaxError(
                                f"unexpected '{err}'", linenum=node.token().linenum
                            )
                        )
                    else:
                        raise
                except Error as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, linenum=node.token().linenum)

    @property
    def is_up_to_date(self) -> bool:
        """False if the template was modified since it was last parsed,
        True otherwise."""
        if not self.uptodate:
            return True

        uptodate = self.uptodate()
        if not isinstance(uptodate, bool):
            raise Error(
                f"expected a boolean from uptodate, found {type(uptodate).__name__}"
            )
        return uptodate

    async def is_up_to_date_async(self) -> bool:
        """An async version of the ``is_up_to_date`` property.

        If ``template.uptodate`` is a coroutine, it wil be awaited. Otherwise it will be
        called just like ``is_up_to_date``
        """
        if not self.uptodate:
            return True

        uptodate = self.uptodate()
        if isinstance(uptodate, Awaitable):
            return await uptodate
        return uptodate

    def _make_globals(
        self, partial: bool, args: Any, kwargs: Any
    ) -> abc.Mapping[str, object]:
        return {
            **dict(*args, **kwargs),
            "partial": partial,
        }

    def __repr__(self) -> str:
        return (
            f"Template(name='{self.name}', "
            f"path='{self.path}', uptodate={self.is_up_to_date})"
        )  # pragma: no cover


class AwareBoundTemplate(BoundTemplate):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.drop = TemplateDrop(self.name, self.path)

    def _make_globals(
        self, partial: bool, args: Any, kwargs: Any
    ) -> abc.Mapping[str, object]:
        return {"template": self.drop, **super()._make_globals(partial, args, kwargs)}


class TemplateDrop(Mapping[str, Optional[str]]):
    """Template meta data mapping."""

    def __init__(self, name: str, path: Optional[Union[str, Path]]):
        self.name = name
        self.path = path

        if not self.path or isinstance(self.path, str):
            self.path = Path(self.name)

        self.stem = self.path.stem
        self.suffix: Optional[str] = None

        if "." in self.stem:
            self.suffix = self.stem.split(".")[-1]

        self._items = {
            "directory": self.path.parent.name,
            "name": self.path.name.split(".")[0],
            "suffix": self.suffix,
        }

    def __str__(self) -> str:
        return self.stem

    def __repr__(self) -> str:
        return (
            f"TemplateDrop(directory='{self['directory']}', "
            f"name='{self['name']}', suffix='{self['suffix']}')"
        )  # pragma: no cover

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __getitem__(self, key: object) -> Optional[str]:
        return self._items[str(key)]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)
