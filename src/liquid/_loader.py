from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._template import Template
    from .environment import Environment


@dataclass(slots=True, kw_only=True)
class TemplateSource:
    """Template source text and meta data."""

    name: str
    text: str
    path: str | None = None
    matter: Mapping[str, object] | None = None
    up_to_date: Callable[[], bool | Awaitable[bool]] | None = None


class Loader(ABC):
    """Template loader base class."""

    @abstractmethod
    def get_source(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource: ...

    async def get_source_async(
        self,
        env: Environment,
        name: str,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> TemplateSource:
        return self.get_source(env, name, context, **kwargs)

    def load(
        self,
        env: Environment,
        name: str,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        source = self.get_source(env, name, context, **kwargs)
        return env.parse(
            source.text,
            name=source.name,
            path=source.path,
            globals=globals,
            matter=source.matter,
            up_to_date=source.up_to_date,
        )

    async def load_async(
        self,
        env: Environment,
        name: str,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        source = await self.get_source_async(env, name, context, **kwargs)
        return env.parse(
            source.text,
            name=source.name,
            path=source.path,
            globals=globals,
            matter=source.matter,
            up_to_date=source.up_to_date,
        )
