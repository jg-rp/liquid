"""Manage undefined template variables.

When rendering a Liquid template, if a variable name can not be resolved, an instance of
liquid.Undefined, or a subclass, is used instead.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import Optional

from liquid.exceptions import UndefinedError

if TYPE_CHECKING:
    from liquid import Token

UNDEFINED = object()


class Undefined(Mapping[Any, object]):
    """The default undefined type.

    Always evaluates to an empty string. Can be iterated over and indexed without error.
    """

    __slots__ = ("name", "obj", "hint", "token")

    def __init__(
        self,
        name: str,
        *,
        token: Optional[Token] = None,
        obj: object = UNDEFINED,
        hint: Optional[str] = None,
    ):
        self.name = name
        self.token = token
        self.obj = obj
        self.hint = hint

    def __contains__(self, item: object) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Undefined) or other is None

    def __getitem__(self, key: str) -> object:
        return self

    def __len__(self) -> int:
        return 0

    def __iter__(self) -> Iterator[Any]:
        return iter([])

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:  # pragma: no cover
        return f"Undefined({self.name})"

    def __int__(self) -> int:
        return 0

    def __hash__(self) -> int:
        return hash(self.name)

    def __reversed__(self) -> Iterable[Any]:
        return []

    def __liquid__(self) -> object:
        return None

    def poke(self) -> bool:
        """Prod the type, giving it the opportunity to raise an exception."""
        return True


class DebugUndefined(Undefined):
    """An undefined that returns debug information when rendered."""

    __slots__ = ()

    def __str__(self) -> str:
        if self.hint:
            return self.hint
        if self.obj is not UNDEFINED:
            return f"{type(self.obj).__name__} has no attribute '{self.name}'"
        return f"'{self.name}' is undefined"

    def __repr__(self) -> str:  # pragma: no cover
        return f"Undefined({self.name})"


class StrictUndefined(Undefined):
    """An undefined that raises an exception for everything other than `repr`."""

    __slots__ = ("msg",)

    # Properties that don't raise an UndefinedError.
    allowed_properties = frozenset(
        [
            "__repr__",
            # "__class__",
            "force_liquid_default",
            "name",
            "hint",
            "obj",
            "msg",
            "path",
            "token",
        ]
    )

    def __init__(
        self,
        name: str,
        *,
        token: Optional[Token],
        obj: object = UNDEFINED,
        hint: Optional[str] = None,
    ):
        super().__init__(name, token=token, obj=obj, hint=hint)
        self.msg = self.hint if self.hint else f"'{self.name}' is undefined"

    def __getattribute__(self, name: str) -> object:
        if name in object.__getattribute__(self, "allowed_properties"):
            return object.__getattribute__(self, name)
        raise UndefinedError(object.__getattribute__(self, "msg"), token=self.token)

    def __contains__(self, item: object) -> bool:
        raise UndefinedError(self.msg, token=self.token)

    def __eq__(self, other: object) -> bool:
        raise UndefinedError(self.msg, token=self.token)

    def __getitem__(self, key: str) -> object:
        raise UndefinedError(self.msg, token=self.token)

    def __len__(self) -> int:
        raise UndefinedError(self.msg, token=self.token)

    def __iter__(self) -> Iterator[Any]:
        raise UndefinedError(self.msg, token=self.token)

    def __str__(self) -> str:
        raise UndefinedError(self.msg, token=self.token)

    def __repr__(self) -> str:
        return f"StrictUndefined({self.name})"

    def __bool__(self) -> bool:
        raise UndefinedError(self.msg, token=self.token)

    def __int__(self) -> int:
        raise UndefinedError(self.msg, token=self.token)

    def __hash__(self) -> int:
        raise UndefinedError(self.msg, token=self.token)

    def __reversed__(self) -> Iterable[Any]:
        raise UndefinedError(self.msg, token=self.token)


class StrictDefaultUndefined(StrictUndefined):
    """An undefined that plays nicely with the `default` filter."""

    # Force the `default` filter to return its default value
    # without inspecting this class type.
    force_liquid_default = True

    # # Properties that don't raise an UndefinedError.
    # allowed_properties = frozenset(
    #     [
    #         "__repr__",
    #         "force_liquid_default",
    #         "name",
    #         "hint",
    #         "obj",
    #         "msg",
    #     ]
    # )


class FalsyStrictUndefined(StrictUndefined):
    """An strict undefined type that can be tested for truthiness."""

    allowed_properties = frozenset(
        [
            "__repr__",
            "__bool__",
            "__eq__",
            "__liquid__",
            "__class__",
            "name",
            "hint",
            "obj",
            "msg",
            "force_liquid_default",
            "path",
            "token",
        ]
    )

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return other is False


def is_undefined(obj: object) -> bool:
    """Return `True` if `obj` is undefined. `False` otherwise."""
    return isinstance(obj, Undefined)
