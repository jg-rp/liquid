"""Liquid template definition."""

from __future__ import annotations

from collections import ChainMap
from collections import abc

from io import StringIO
from pathlib import Path

from typing import Callable
from typing import Dict
from typing import Any
from typing import Optional
from typing import TextIO
from typing import Mapping
from typing import TYPE_CHECKING

from liquid.context import Context

from liquid.exceptions import LiquidInterrupt
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import Error

if TYPE_CHECKING:
    from liquid import Environment
    from liquid.ast import ParseTree


# pylint: disable=too-many-instance-attributes
class Template:
    """A loaded and parsed liquid template.

    Rather than instantiating templates directly, the recommended way to create
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

        self.bytecode = None

    def render(self, *args: ..., **kwargs: ...) -> str:
        """Render the template with `args` and `kwargs` included in the render context.

        Accepts the same arguments as the `dict` constructor.
        """
        _vars: Dict[str, object] = dict(*args, **kwargs)

        context = Context(self.env, ChainMap(_vars, self._globals))

        buf = StringIO()
        self.render_with_context(context, buf)
        return buf.getvalue()

    def render_with_context(
        self,
        context: Context,
        buffer: TextIO,
        *args: ...,
        partial: bool = False,
        block_scope: bool = False,
        **kwargs: ...,
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
        # "template" could get overridden from args/kwargs, "partial" will not.
        namespace: Dict[str, Any] = {
            "template": self.drop,
            **dict(*args, **kwargs),
            "partial": partial,
        }

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
                                f"unexpected '{err}'", linenum=node.tok.linenum
                            )
                        )
                    else:
                        raise
                except Error as err:
                    # Raise or warn according to the current mode.
                    self.env.error(err, linenum=node.tok.linenum)

    @property
    def is_up_to_date(self) -> bool:
        """False if the template was modified since it was last parsed,
        True otherwise."""
        if not self.uptodate:
            return True
        return self.uptodate()

    def __repr__(self):
        return (
            f"Template(name='{self.name}', "
            f"path='{self.path}', uptodate={self.is_up_to_date})"
        )


class TemplateDrop(abc.Mapping):
    """Template meta data mapping."""

    def __init__(self, name: str, path: Optional[Path]):
        self.name = name
        self.path = path or Path(name)

        self.stem = self.path.stem
        if "." in self.stem:
            self.suffix = self.stem.split(".")[-1]
        else:
            self.suffix = None

        self._items = {
            "directory": self.path.parent.name,
            "name": self.path.name.split(".")[0],
            "suffix": self.suffix,
        }

    def __str__(self):
        return self.stem

    def __repr__(self):
        return (
            f"TemplateDrop(directory='{self['directory']}', "
            f"name='{self['name']}', suffix='{self['suffix']}')"
        )

    def __contains__(self, item):
        return item in self._items

    def __getitem__(self, key):
        return self._items[key]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)
