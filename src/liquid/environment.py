# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownVariableType=false
# pyright: reportReturnType=false
from __future__ import annotations

import json
import math
from collections.abc import Awaitable, Callable, Generator, Mapping, Sequence
from decimal import Decimal
from typing import TYPE_CHECKING, Any, ClassVar

import markupsafe

from . import filters, tags
from ._chain_map import ReadOnlyChainMap
from ._drop import has_html_safe_string, is_drop
from ._io import StringBuffer
from ._lexer import Lexer
from ._lexer_legacy import LegacyLexer
from ._nothing import Nothing
from ._parser_legacy import LegacyParser
from ._template import Template
from .drops import Undefined
from .exceptions import LiquidTypeError
from .loaders import DictLoader

if TYPE_CHECKING:
    from ._context import RenderContext
    from ._filter import Filter
    from ._loader import Loader
    from ._markup import Tag
    from ._parser import Parser
    from ._resource_limits import ResourceLimits
    from .tokens import Token


class Environment:
    standard_tags: ClassVar[dict[str, Tag]] = {
        "assign": tags.AssignTag,
        "break": tags.BreakTag,
        "capture": tags.CaptureTag,
        "case": tags.CaseTag,
        "comment": tags.CommentTag,
        "continue": tags.ContinueTag,
        "cycle": tags.CycleTag,
        "decrement": tags.DecrementTag,
        "doc": tags.DocTag,
        "echo": tags.EchoTag,
        "for": tags.ForTag,
        "if": tags.IfTag,
        "ifchanged": tags.IfChangedTag,
        "include": tags.IncludeTag,
        "increment": tags.IncrementTag,
        "liquid": tags.LiquidTag,
        "raw": tags.RawTag,
        "render": tags.RenderTag,
        "tablerow": tags.TableRowTag,
        "unless": tags.UnlessTag,
        "#": tags.InlineCommentTag,
    }

    standard_filters: ClassVar[dict[str, Filter]] = {
        "abs": filters.abs_,
        "append": filters.append,
        "at_least": filters.at_least,
        "at_most": filters.at_most,
        "base64_decode": filters.base64_decode,
        "base64_encode": filters.base64_encode,
        "base64_url_safe_decode": filters.base64_url_safe_decode,
        "base64_url_safe_encode": filters.base64_url_safe_encode,
        "ceil": filters.ceil,
        "capitalize": filters.capitalize,
        "compact": filters.compact,
        "concat": filters.concat,
        "date": filters.date,
        "default": filters.default,
        "divided_by": filters.divided_by,
        "downcase": filters.downcase,
        "escape_once": filters.escape_once,
        "escape": filters.escape,
        "escapejs": filters.escapejs,
        "find": filters.find,
        "find_index": filters.find_index,
        "first": filters.first,
        "floor": filters.floor,
        "has": filters.has,
        "join": filters.join,
        "last": filters.last,
        "lstrip": filters.lstrip,
        "map": filters.map_,
        "minus": filters.minus,
        "modulo": filters.modulo,
        "newline_to_br": filters.newline_to_br,
        "plus": filters.plus,
        "prepend": filters.prepend,
        "reject": filters.reject,
        "remove": filters.remove,
        "remove_first": filters.remove_first,
        "remove_last": filters.remove_last,
        "replace": filters.replace,
        "replace_first": filters.replace_first,
        "replace_last": filters.replace_last,
        "reverse": filters.reverse,
        "round": filters.round_,
        "rstrip": filters.rstrip,
        "safe": filters.safe,
        "size": filters.size,
        "slice": filters.slice_,
        "sort": filters.sort,
        "sort_natural": filters.sort_natural,
        "split": filters.split,
        "squish": filters.squish,
        "strip": filters.strip,
        "strip_html": filters.strip_html,
        "strip_newlines": filters.strip_newlines,
        "sum": filters.sum_,
        "times": filters.times,
        "truncate": filters.truncate,
        "truncatewords": filters.truncate_words,
        "uniq": filters.uniq,
        "upcase": filters.upcase,
        "url_decode": filters.url_decode,
        "url_encode": filters.url_encode,
        "where": filters.where,
    }

    def __init__(
        self,
        *,
        autoescape: bool = False,
        conventional_operator_precedence: bool = False,
        globals: Mapping[str, object] | None = None,
        iterable_strings: bool = False,
        loader: Loader | None = None,
        parser: type[Parser] = LegacyParser,
        resource_limits: ResourceLimits | None = None,
        strict_filters: bool = True,
        tokenizer: type[Lexer] = LegacyLexer,
        undefined: type[Undefined] = Undefined,
    ) -> None:
        self.loader = loader or DictLoader({})
        self.globals = globals
        self.undefined_type = undefined

        self.strict_filters = strict_filters
        self.autoescape = autoescape
        self.iterable_strings = iterable_strings

        self.tokenizer = tokenizer
        self.parser = parser

        self.conventional_operator_precedence = conventional_operator_precedence

        # TODO: Update to use ResourceLimits
        self.max_assign_score: int | None = None
        self.max_assign_score_cumulative: int | None = None
        self.max_render_score: int | None = None
        self.max_render_score_cumulative: int | None = None
        self.max_render_size: int | None = None
        self.max_context_depth: int = 30
        self.max_loop_iterations: int | None = None
        self.max_block_depth: int = 30

        self.tags: dict[str, Tag] = {}
        self.filters: dict[str, Filter] = {}

        self.buffer_factory: Callable[[], StringBuffer] = StringBuffer

        self.persistent_registers: list[str] = []

        self.setup_tags_and_filters()

    def setup_tags_and_filters(self) -> None:
        self.tags.update(self.standard_tags)
        self.filters.update(self.standard_filters)

    def get_template(
        self,
        name: str,
        *,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        return self.loader.load(self, name, globals, context, **kwargs)

    async def get_template_async(
        self,
        name: str,
        *,
        globals: Mapping[str, object] | None = None,
        context: RenderContext | None = None,
        **kwargs: object,
    ) -> Template:
        return await self.loader.load_async(self, name, globals, context, **kwargs)

    def parse(
        self,
        source: str,
        *,
        name: str = "",
        path: str | None = None,
        globals: Mapping[str, object] | None = None,
        matter: Mapping[str, object] | None = None,
        up_to_date: Callable[[], bool | Awaitable[bool]] | None = None,
    ) -> Template:
        return Template(
            self,
            source,
            name,
            self.parser.parse(self, source, name),
            path=path,
            globals=self.make_globals(globals),
            matter=matter,
            up_to_date=up_to_date,
        )

    def render(self, source: str, data: Mapping[str, object]) -> str:
        return self.parse(source).render(data)

    async def render_async(self, source: str, data: Mapping[str, object]) -> str:
        return await self.parse(source).render_async(data)

    def tokenize(self, source: str) -> list[Token]:
        return self.tokenizer.tokenize(self, source)

    def make_globals(
        self, data: Mapping[str, object] | None
    ) -> Mapping[str, object] | None:
        if data is None:
            return self.globals

        if self.globals is None:
            return data

        return ReadOnlyChainMap(data, self.globals)

    def serialize(self, obj: object, context: RenderContext, span: Token) -> str:
        """Stringify `obj` suitable for output."""
        if self.autoescape and has_html_safe_string(obj):
            return obj.__html__()

        if isinstance(obj, str):
            result = obj
        elif isinstance(obj, Sequence):
            result = (markupsafe.Markup("") if self.autoescape else "").join(
                self.to_str(item, context, span) for item in _flatten(obj)
            )
        else:
            result = self.to_str(obj, context, span)

        return markupsafe.escape(result) if self.autoescape else result

    def trim(self, text: str, left: str | None, right: str | None) -> str:
        if left == "-" and right == "-":
            return text.strip()

        if left == "-":
            return text.lstrip()

        if right == "-":
            return text.rstrip()

        return text

    def truthy(self, obj: object, context: RenderContext) -> bool:
        if is_drop(obj):
            obj = bool(obj)

        return not (obj is False or obj is None)

    def eq(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        if is_drop(right):
            if is_drop(left):
                return right == left.__liquid__("data", context)
            return right == left

        if is_drop(left):
            if is_drop(right):
                return left == right.__liquid__("data", context)
            return left == right

        if type(left) is bool and type(right) is int:
            return False

        if type(right) is bool and type(left) is int:
            return False

        return left == right

    def lt(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        if is_drop(left):
            if is_drop(right):
                try:
                    return left < right.__liquid__("data", context)
                except TypeError:
                    return False

            try:
                return left < right
            except TypeError:
                return False

        if is_drop(right):
            if is_drop(left):
                try:
                    return right > left.__liquid__("data", context)
                except TypeError:
                    return False

            try:
                return right > left
            except TypeError:
                return False

        if isinstance(left, str) and isinstance(right, str):
            return left < right

        if type(left) is bool or type(right) is bool:
            return False

        if isinstance(left, (int, float, Decimal)) and isinstance(
            right, (int, float, Decimal)
        ):
            return left < right

        if self.is_nil(left) or self.is_nil(right):
            return False

        raise LiquidTypeError(
            f"{left.__class__.__name__} and {right.__class__.__name__} are not comparable",
            token=span,
            source=context.template.source,
            name=context.template.name,
        )

    def le(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        if is_drop(right):
            if is_drop(left):
                try:
                    return right >= left.__liquid__("data", context)
                except TypeError:
                    return False

            try:
                return right >= left
            except TypeError:
                return False

        if is_drop(left):
            if is_drop(right):
                try:
                    return left <= right.__liquid__("data", context)
                except TypeError:
                    return False

            try:
                return left <= right
            except TypeError:
                return False

        if isinstance(left, str) and isinstance(right, str):
            return left <= right

        if type(left) is bool or type(right) is bool:
            return False

        if isinstance(left, (int, float, Decimal)) and isinstance(
            right, (int, float, Decimal)
        ):
            return left <= right

        if self.is_nil(left) or self.is_nil(right):
            return False

        return self.eq(left, right, context, span)

    def contains(
        self, left: object, right: object, context: RenderContext, span: Token
    ) -> bool:
        if is_drop(left):
            return right in left

        if not (self.truthy(left, context) and self.truthy(right, context)):
            return False

        if isinstance(left, str):
            return left.find(self.to_str(right, context, span)) != -1

        if isinstance(left, Sequence):
            try:
                return left.index(right) != -1 and self.truthy(right, context)
            except ValueError:
                return False

        if isinstance(left, Mapping):
            return right in left

        raise LiquidTypeError(
            f"{left.__class__.__name__} is not a container",
            token=span,
            source=context.template.source,
            name=context.template.name,
        )

    def undefined(
        self, name: str, span: Token, source: str, template_name: str
    ) -> object:
        return self.undefined_type(name, span, source, template_name)

    def to_int(self, obj: object, context: RenderContext, span: Token) -> int:
        if isinstance(obj, int | float | Decimal):
            return math.trunc(obj)

        try:
            return math.trunc(float(str(obj)))
        except (TypeError, ValueError):
            raise LiquidTypeError(
                "invalid integer",
                token=span,
                source=context.template.source,
                name=context.template.name,
            )

    def to_numeric(
        self, obj: object, context: RenderContext, default: int | Decimal = 0
    ) -> float | int | Decimal:
        if isinstance(obj, int | float | Decimal):
            return obj

        if isinstance(obj, str):
            try:
                return int(obj)
            except ValueError:
                pass

            try:
                return float(obj)
            except ValueError:
                return default

        if is_drop(obj):
            return obj.__liquid__("numeric", context)  # type: ignore

        return default

    def to_str(self, obj: object, context: RenderContext, span: Token) -> str:
        if obj is None:
            return ""

        if isinstance(obj, str):
            return obj

        if is_drop(obj):
            return str(obj)
            # return obj.__liquid__("string", context)

        if isinstance(obj, Mapping | Sequence):
            return self._inspect(obj, context)

        if type(obj) is bool:
            return str(obj).lower()

        return str(obj)

    def to_array(
        self, obj: object, context: RenderContext, span: Token
    ) -> list[object]:
        if isinstance(obj, str) and not self.iterable_strings:
            return [] if not obj else [obj]

        if is_drop(obj):
            return list(obj)

        if isinstance(obj, Sequence):
            return list(obj)  # pyright: ignore[reportUnknownArgumentType]

        if isinstance(obj, Mapping):
            return [(k, v) for k, v in obj.items()]  # pyright: ignore[reportUnknownVariableType]

        if self.is_nil(obj) or type(obj) is bool:
            return []

        return [obj]

    def is_nil(self, obj: object) -> bool:
        return obj == None or isinstance(obj, (Undefined, Nothing))

    def _inspect(
        self,
        obj: object,
        context: RenderContext,
        circular_placeholder: str = '"[Circular]"',
    ) -> str:
        """Stringify `value` using Ruby `=>` notation."""
        seen: set[int] = set()

        def stringify(val: Any) -> str | None:
            if val is None:
                return "null"

            if isinstance(val, bool):
                return "true" if val else "false"

            if isinstance(val, (int, float)):
                if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                    return "null"
                return str(val)

            if isinstance(val, Decimal):
                if val.is_nan() or val.is_infinite():
                    return "null"
                return str(val)

            # Handle strings, bytes, and bytearrays as scalars (not Sequences)
            if isinstance(val, (str, bytes, bytearray)):
                if isinstance(val, (bytes, bytearray)):
                    val = val.decode("utf-8", errors="replace")
                return json.dumps(val)

            if isinstance(val, Mapping):
                val_id = id(val)
                if val_id in seen:
                    return circular_placeholder

                seen.add(val_id)
                try:
                    entries: list[str] = []
                    for k, v in val.items():
                        formatted_val = stringify(v)
                        if formatted_val is not None:
                            formatted_key = json.dumps(str(k))
                            entries.append(f"{formatted_key}=>{formatted_val}")
                    return "{" + ", ".join(entries) + "}"
                finally:
                    seen.remove(val_id)

            if isinstance(val, Sequence):
                val_id = id(val)
                if val_id in seen:
                    return circular_placeholder

                seen.add(val_id)
                try:
                    items: list[str] = []
                    for item in val:
                        formatted_val = stringify(item)
                        items.append("null" if formatted_val is None else formatted_val)
                    return "[" + ", ".join(items) + "]"
                finally:
                    seen.remove(val_id)

            # Fallback for custom objects
            return json.dumps(str(val))

        result = stringify(obj)
        return "null" if result is None else result


def _flatten(it: Sequence[object], level: int = 5) -> list[object]:

    def flatten_(it: Sequence[object], level: int = 5) -> Generator[object]:
        for obj in it:
            if level < 1 or not isinstance(obj, (list, tuple)):
                yield obj
            else:
                yield from flatten_(obj, level=level - 1)

    return list(flatten_(it, level))
