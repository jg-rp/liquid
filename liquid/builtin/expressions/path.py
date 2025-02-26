"""A built-in expression for paths to a value/variable.

Note that a path might contain just one segment, in which case we might just
call it a "variable".
"""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING
from typing import Union

from liquid.expression import Expression
from liquid.limits import to_int
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_IDENTSTRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_WORD

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext
    from liquid import Token
    from liquid import TokenStream

Segments = list[Union[str, int, "Path"]]
Location = tuple[Union[str, int, "Location"], ...]


# This is use for pretty printing paths with shorthand notation where possible.
RE_PROPERTY = re.compile(r"[\u0080-\uFFFFa-zA-Z_][\u0080-\uFFFFa-zA-Z0-9_-]*")


class Path(Expression):
    __slots__ = ("path",)

    def __init__(self, token: Token, path: Segments):
        super().__init__(token)
        self.path = path

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Path) and self.path == other.path

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
            [p.evaluate(context) if isinstance(p, Path) else p for p in self.path],
            token=self.token,
        )

    async def evaluate_async(self, context: RenderContext) -> object:
        return await context.get_async(
            [
                await p.evaluate_async(context) if isinstance(p, Path) else p
                for p in self.path
            ],
            token=self.token,
        )

    def children(self) -> list[Expression]:
        return [p for p in self.path if isinstance(p, Expression)]

    @staticmethod
    def parse(env: Environment, tokens: TokenStream) -> Path:
        token = tokens.current
        segments: Segments = []

        # TODO: fix me regarding dots
        # TODO: floats and shorthand indexes
        while True:
            kind, value, index, _ = tokens.current

            if kind == TOKEN_WORD:
                segments.append(value)
            elif kind == TOKEN_IDENTINDEX:
                segments.append(to_int(value))
            elif kind == TOKEN_LBRACKET:
                next(tokens)
                segments.append(Path.parse(env, tokens))
                tokens.expect(TOKEN_RBRACKET)
            elif kind == TOKEN_DOT:
                pass
            else:
                break

            next(tokens)

        p = Path(token, segments)
        return p
