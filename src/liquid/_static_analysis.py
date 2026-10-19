from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union

from . import expressions
from ._context import RenderContext
from .exceptions import LiquidError
from .tokens import token_value

if TYPE_CHECKING:
    from ._markup import Expression, Node
    from ._template import Template
    from .tokens import Token


@dataclass(slots=True, kw_only=True)
class Location:
    template: Template
    token: Token

    def line_col(self, index: int) -> tuple[int, int]:
        cumulative_length = 0
        target_line_index = -1

        for i, line in enumerate(self.template.lines):
            cumulative_length += len(line)
            if index < cumulative_length:
                target_line_index = i
                break

        if target_line_index == -1:
            raise LiquidError("index out of bounds")

        line_number = target_line_index + 1
        line = self.template.lines[target_line_index]
        column_number = index - cumulative_length - len(line)
        return line_number, column_number

    def span(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return self.line_col(self.token[1]), self.line_col(self.token[2])

    def value(self) -> str:
        return token_value(self.token, self.template.source)


@dataclass(slots=True, kw_only=True)
class Loc:
    start_index: int
    end_index: int
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    value: str
    template_name: str
    template_path: str | None


type Segments = list[int | str | Segments]


@dataclass(slots=True, kw_only=True)
class Var(Loc):
    segments: Segments
    path: str


type Vars = dict[str, list[Var]]

type Locations = dict[str, list[Loc]]

RE_PROPERTY = re.compile(r"[a-zA-Z_][a-zA-Z0-9_-]*\??")


@dataclass(slots=True, kw_only=True)
class StaticVariable:
    segments: Segments
    location: Location

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StaticVariable) and self.segments == other.segments

    def root(self) -> str:
        segment = self.segments[0] if self.segments else ""
        if isinstance(segment, list):
            return self._to_str(segment)
        return str(segment)

    def __str__(self) -> str:
        return self._to_str(self.segments)

    def _to_str(self, segments: Segments) -> str:
        def segment_str(segment: int | str | Segments) -> str:
            if isinstance(segment, list):
                return f"[{self._to_str(segment)}]"
            if isinstance(segment, str) and RE_PROPERTY.match(segment):
                return f".{segment}"
            return f"[{segment}]"

        return "".join(segment_str(s) for s in segments)


class StaticScope:
    def __init__(self, globals: set[str]) -> None:
        self.stack: list[set[str]] = [globals]

    def add(self, name: str) -> None:
        self.stack[0].add(name)

    def __contains__(self, key: str) -> bool:
        for scope in self.stack:
            if key in scope:
                return True

        return False

    def pop(self) -> set[str] | None:
        return self.stack.pop() if self.stack else None

    def push(self, scope: set[str]) -> StaticScope:
        self.stack.append(scope)
        return self


class VariableMap:
    def __init__(self) -> None:
        self.data: dict[str, list[StaticVariable]] = {}

    def add(self, key: StaticVariable) -> None:
        v = self.get(key)
        if v is not None:
            v.append(key)

    def get(self, key: StaticVariable) -> list[StaticVariable] | None:
        k = key.root()
        if k not in self.data:
            self.data[k] = []
        return self.data[k]

    def to_dict(self) -> Vars:
        obj: Vars = {}

        for k, v in self.data.items():
            a: list[Var] = []

            for sv in v:
                ((start_line, start_column), (end_line, end_column)) = (
                    sv.location.span()
                )

                a.append(
                    Var(
                        segments=sv.segments,
                        path=str(sv),
                        start_index=sv.location.token[1],
                        end_index=sv.location.token[2],
                        start_line=start_line,
                        start_column=start_column,
                        end_line=end_line,
                        end_column=end_column,
                        value=sv.location.value(),
                        template_name=sv.location.template.name,
                        template_path=sv.location.template.path,
                    )
                )

            obj[k] = a

        return obj


@dataclass(slots=True, kw_only=True)
class TemplateAnalysis:
    variables: Vars
    locals: Vars
    globals: Vars
    filters: Locations
    tags: Locations
