from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Never

from .._drop import Drop
from .._nothing import Nothing
from ..exceptions import UndefinedVariableError
from .iterable import IterableDrop

if TYPE_CHECKING:
    from .._context import RenderContext
    from .._drop import ContextHint
    from ..tokens import Token


class Blank(Drop):
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string" | "data":
                return ""
            case "numeric":
                return 0
            case _:
                return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Blank, Empty)):
            return False

        if other is None or other is False or isinstance(other, Undefined):
            return True

        if isinstance(other, str):
            return not other or other.isspace()

        if isinstance(other, (list, tuple, dict)):
            return not other

        return False

    def __str__(self) -> str:
        return ""


BLANK = Blank()


class Empty(Drop):
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        match hint:
            case "string" | "data":
                return ""
            case "numeric":
                return 0
            case _:
                return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Empty):
            return True

        if other is None or isinstance(other, Blank):
            return False

        if isinstance(other, (list, tuple, dict, str)):
            return not other

        return False

    def __str__(self) -> str:
        return ""


EMPTY = Empty()


class Undefined(Drop):
    __slots__ = ("path", "source", "template_name", "token")

    def __init__(
        self, path: str, token: Token, source: str, template_name: str
    ) -> None:
        self.path = path
        self.token = token
        self.source = source
        self.template_name = template_name

    def poke(self) -> None:
        pass

    def __getitem__(self, key: str) -> object:
        if key in ("first", "last", "size"):
            return self
        raise KeyError

    def __contains__(self, item: object) -> bool:
        return item in ("first", "last", "size")

    def __len__(self) -> int:
        return 3

    def __liquid_iter__(
        self, start: int, end: int | None, reversed_: bool
    ) -> IterableDrop[object]:
        return IterableDrop[object]([], 0)

    def __eq__(self, other: object) -> bool:
        return other is None or isinstance(other, (Undefined, Nothing, Blank))


class StrictUndefined(Undefined):
    def _error(self) -> Never:
        raise UndefinedVariableError(
            f"{self.path} is undefined",
            token=self.token,
            source=self.source,
            name=self.template_name,
        )

    def __iter__(self) -> Iterator[str]:
        self._error()

    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        self._error()

    def __liquid_iter__(
        self, start: int, end: int | None, reversed_: bool
    ) -> IterableDrop[object]:
        self._error()

    def __len__(self) -> int:  # noqa: PLE0303
        self._error()

    def __getitem__(self, key: str) -> object:
        self._error()

    def __eq__(self, other: object) -> bool:
        self._error()

    def __lt__(self, other: object) -> bool:
        self._error()

    def __le__(self, other: object) -> bool:
        self._error()

    def __gt__(self, other: object) -> bool:
        self._error()

    def __ge__(self, other: object) -> bool:
        self._error()

    def __contains__(self, item: object) -> bool:
        self._error()

    def __str__(self) -> str:  # noqa: PLE0307
        self._error()

    def __bool__(self) -> bool:  # noqa: PLE0304
        self._error()


class FalsyStrictUndefined(StrictUndefined):
    def __liquid__(self, hint: ContextHint, context: RenderContext) -> object:
        if hint == "boolean":
            return False
        self._error()

    def __contains__(self, item: object) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return other is None or isinstance(other, (Undefined, Nothing, Blank))
