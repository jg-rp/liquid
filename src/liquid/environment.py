from __future__ import annotations

from collections.abc import Callable, Mapping
from decimal import Decimal
from io import StringIO
from typing import TYPE_CHECKING

from . import filters, tags
from ._nothing import Nothing
from .drops import Undefined

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._filter import Filter
    from ._markup import Tag
    from ._template import Template
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
        self.autoescape = False
        self.string_first_and_last = False

        self.tags: dict[str, Tag] = {}
        self.filters: dict[str, Filter] = {}

        self.buffer_factory: Callable[[], StringIO] = StringIO

        self.persistent_registers: list[str] = []

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
        self.tags["ifchanged"] = tags.IfChangedTag
        self.tags["include"] = tags.IncludeTag
        self.tags["increment"] = tags.IncrementTag
        self.tags["liquid"] = tags.LiquidTag
        self.tags["raw"] = tags.RawTag
        self.tags["render"] = tags.RenderTag
        self.tags["tablerow"] = tags.TableRowTag
        self.tags["unless"] = tags.UnlessTag

        # TODO: make this a self.filters.update({...})

        self.filters["abs"] = filters.abs_
        self.filters["append"] = filters.append
        self.filters["at_least"] = filters.at_least
        self.filters["at_most"] = filters.at_most
        self.filters["base64_decode"] = filters.base64_decode
        self.filters["base64_encode"] = filters.base64_encode
        self.filters["base64_url_safe_decode"] = filters.base64_url_safe_decode
        self.filters["base64_url_safe_encode"] = filters.base64_url_safe_encode
        self.filters["capitalize"] = filters.capitalize
        self.filters["compact"] = filters.compact
        self.filters["concat"] = filters.concat
        self.filters["date"] = filters.date
        self.filters["default"] = filters.default
        self.filters["divided_by"] = filters.divided_by
        self.filters["downcase"] = filters.downcase
        self.filters["escape"] = filters.escape
        self.filters["escape_once"] = filters.escape_once
        self.filters["find"] = filters.find
        self.filters["find_index"] = filters.find_index
        self.filters["first"] = filters.first
        self.filters["floor"] = filters.floor
        self.filters["has"] = filters.has
        self.filters["join"] = filters.join
        self.filters["last"] = filters.last
        self.filters["lstrip"] = filters.lstrip
        self.filters["map"] = filters.map_
        self.filters["minus"] = filters.minus
        self.filters["modulo"] = filters.modulo
        self.filters["newline_to_br"] = filters.newline_to_br
        self.filters["plus"] = filters.plus
        self.filters["prepend"] = filters.prepend
        self.filters["reject"] = filters.reject
        self.filters["remove"] = filters.remove
        self.filters["remove_first"] = filters.remove_first
        self.filters["remove_last"] = filters.remove_last
        self.filters["replace"] = filters.replace
        self.filters["replace_first"] = filters.replace_first
        self.filters["replace_last"] = filters.replace_last
        self.filters["reverse"] = filters.reverse
        self.filters["round"] = filters.round_
        self.filters["rstrip"] = filters.rstrip
        self.filters["slice"] = filters.slice_
        self.filters["sort"] = filters.sort
        self.filters["sort_natural"] = filters.sort_natural
        self.filters["split"] = filters.split
        self.filters["squish"] = filters.squish
        self.filters["strip"] = filters.strip
        self.filters["strip_html"] = filters.strip_html
        self.filters["strip_newlines"] = filters.strip_newlines
        self.filters["sum"] = filters.sum_
        self.filters["times"] = filters.times
        self.filters["truncate"] = filters.truncate
        self.filters["truncate_words"] = filters.truncate_words

    def get_template(
        self,
        name: str,
        *,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        # TODO:
        raise NotImplementedError

    async def get_template_async(
        self,
        name: str,
        *,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        # TODO:
        raise NotImplementedError

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

    def to_numeric[T](
        self, obj: object, context: RenderContext, default: T
    ) -> float | int | Decimal | T:
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

    def is_nil(self, obj: object) -> bool:
        return obj == None or isinstance(obj, (Undefined, Nothing))
