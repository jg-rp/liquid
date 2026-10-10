from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Concatenate

from ._drop import is_iterable_drop
from ._missing import MISSING
from ._nothing import NOTHING
from .exceptions import LiquidFilterError

if TYPE_CHECKING:
    from ._context import RenderContext
    from .environment import LiquidEnvironment
    from .tokens import Token


type Filter = Callable[Concatenate[FilterContext, object, ...], object]


@dataclass(slots=True)
class FilterContext:
    context: RenderContext
    span: Token

    missing: object = field(init=False)
    env: LiquidEnvironment = field(init=False)

    def __post_init__(self) -> None:
        self.missing = MISSING
        self.env = self.context.env

    def get_item(self, obj: object, key: object, default: object = MISSING) -> object:
        if isinstance(obj, str) and isinstance(key, str):
            return key if key in obj else None

        if isinstance(obj, (int, float, Decimal)) and isinstance(
            key, (int, float, Decimal)
        ):
            return obj == key

        if self.is_nil(obj) or not isinstance(obj, Mapping):
            raise LiquidFilterError(
                f"can't read property {obj}[{key}]",
                token=self.span,
                source=self.context.template.source,
                name=self.context.template.name,
            )

        result, _ = self.context.resolve_path(obj, [key])  # type: ignore
        return default if result == NOTHING else result

    def input_array(self, obj: object) -> list[object]:
        """Coerce `obj` to a list suitable for filters that expect an array input."""
        if isinstance(obj, (list, tuple)):
            return _flatten(obj)  # type: ignore

        if is_iterable_drop(obj):
            return list(obj.__liquid_iter__(0, None, False))

        return [obj]

    def is_nil(self, obj: object) -> bool:
        return self.context.env.is_nil(obj)

    def truthy(self, obj: object) -> bool:
        return self.context.env.truthy(obj, self.context)

    def to_int(self, obj: object) -> int:
        return self.context.env.to_int(obj, self.context, self.span)

    def to_numeric[T](self, obj: object, default: T) -> float | int | Decimal | T:
        return self.context.env.to_numeric(obj, self.context, default)

    def to_str[T](self, obj: object, default: T) -> str | T:
        return (
            default
            if obj is None
            else self.context.env.to_str(obj, self.context, self.span)
        )

    def error(self, message: str) -> LiquidFilterError:
        return LiquidFilterError(
            message,
            token=self.span,
            source=self.context.template.source,
            name=self.context.template.name,
        )


def _flatten(it: Iterable[object], level: int = 5) -> list[object]:

    def flatten_(it: Iterable[object], level: int = 5) -> Generator[object]:
        for obj in it:
            if level < 1 or not isinstance(obj, (list, tuple)):
                yield obj
            else:
                yield from flatten_(obj, level=level - 1)  # type: ignore

    return list(flatten_(it, level))
