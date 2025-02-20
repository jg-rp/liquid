"""A built-in expression for paths to a value/variable.

Note that a path might contain just one segment, in which case we might just
call it a "variable".
"""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING
from typing import TypeAlias
from typing import Union

from liquid.expression import Expression

if TYPE_CHECKING:
    from liquid import RenderContext

Segments: TypeAlias = tuple[Union[str, int, "Path"], ...]
Location: TypeAlias = tuple[Union[str, int, "Location"], ...]


# This is use for pretty printing paths with shorthand notation where possible.
RE_PROPERTY = re.compile(r"[\u0080-\uFFFFa-zA-Z_][\u0080-\uFFFFa-zA-Z0-9_-]*")


class Path(Expression):
    __slots__ = ("path",)

    def __init__(self, path: Segments):
        self.path = path

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Path) and self.path == other.path

    def __repr__(self) -> str:  # pragma: no cover
        return f"Identifier(path={self.path})"

    def __str__(self) -> str:
        it = iter(self.path)
        buf = [str(next(it))]
        for segment in it:
            if isinstance(segment, Path):
                buf.append(f"[{segment}]")
            elif isinstance(segment, str):
                if RE_PROPERTY.fullmatch(segment):
                    buf.append(f".{segment}")
                else:
                    buf.append(f"[{segment!r}]")
            else:
                buf.append(f"[{segment}]")
        return "".join(buf)

    def __hash__(self) -> int:
        return hash(self.path)

    def __sizeof__(self) -> int:
        return super().__sizeof__() + sys.getsizeof(self.path)

    def location(self) -> Location:
        """Return this path's segments as a tuple of strings and ints.

        Segments can also be nested tuples of strings, ints and tuples if the path
        contains nested paths.
        """
        return tuple([s.location() if isinstance(s, Path) else s for s in self.path])

    def evaluate(self, context: RenderContext) -> object:
        return context.get(
            [p.evaluate(context) if isinstance(p, Path) else p for p in self.path]
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return await context.get_async(
            [
                await p.evaluate_async(context) if isinstance(p, Path) else p
                for p in self.path
            ]
        )

    def children(self) -> list[Expression]:
        return [p for p in self.path if isinstance(p, Expression)]
