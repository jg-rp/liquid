from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ._context import RenderContext
    from .tokens import Token


class Filter(Protocol):
    def __call__(
        self,
        context: FilterContext,
        left: object,
        *args: object,
        **kwargs: object,
    ) -> object: ...


@dataclass(slots=True)
class FilterContext:
    context: RenderContext
    span: Token

    # TODO: methods
