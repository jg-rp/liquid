from __future__ import annotations

from collections.abc import Callable
from io import StringIO
from typing import TYPE_CHECKING

from . import tags

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._filter import Filter
    from ._markup import Tag
    from .tokens import Token


class LiquidEnvironment:
    comment_start_delimiter: str = "{#"
    comment_end_delimiter: str = "#}"

    output_start_delimiter: str = "{{"
    output_end_delimiter: str = "}}"

    tag_start_delimiter: str = "{%"
    tag_end_delimiter: str = "%}"

    def __init__(self) -> None:
        self.strict_filters = True
        self.tags: dict[str, Tag] = {}
        self.filters: dict[str, Filter] = {}

        self.buffer_factory: Callable[[], StringIO] = StringIO

        self.setup_tags_and_filters()

    def setup_tags_and_filters(self) -> None:
        self.tags["assign"] = tags.AssignTag
        self.tags["break"] = tags.BreakTag
        self.tags["capture"] = tags.CaptureTag
        self.tags["case"] = tags.CaseTag
        self.tags["comment"] = tags.CommentTag
        self.tags["continue"] = tags.ContinueTag
        self.tags["cycle"] = tags.CycleTag
        self.tags["decrement"] = tags.DecrementTag
        self.tags["doc"] = tags.DocTag
        self.tags["echo"] = tags.EchoTag
        self.tags["for"] = tags.ForTag
        self.tags["if"] = tags.IfTag
        self.tags["increment"] = tags.IncrementTag

    def tokenize(self, source: str) -> list[Token]:
        # TODO:
        raise NotImplementedError

    def serialize(self, obj: object, context: RenderContext, span: Token) -> str:
        # TODO:
        raise NotImplementedError

    def trim(self, text: str, left: str | None, right: str | None) -> str:
        # TODO:
        raise NotImplementedError

    def truthy(self, obj: object, context: RenderContext) -> bool:
        # TODO:
        raise NotImplementedError

    def eq(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        # TODO:
        raise NotImplementedError

    def lt(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        # TODO:
        raise NotImplementedError

    def le(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        # TODO:
        raise NotImplementedError

    def contains(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        # TODO:
        raise NotImplementedError

    def undefined(
        self, name: str, span: Token, source: str, template_name: str
    ) -> object:
        # TODO:
        raise NotImplementedError

    def to_int(self, obj: object, context: RenderContext, span: Token) -> int:
        # TODO:
        raise NotImplementedError

    def to_str(self, obj: object, context: RenderContext, span: Token) -> str:
        # TODO:
        raise NotImplementedError

    def to_array(
        self, obj: object, context: RenderContext, span: Token
    ) -> list[object]:
        # TODO:
        raise NotImplementedError
