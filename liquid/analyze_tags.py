"""Analyze template tags from tokenized source text."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING
from typing import DefaultDict
from typing import Iterable
from typing import Mapping
from typing import Optional

from .span import Span
from .token import TOKEN_TAG

if TYPE_CHECKING:
    from .environment import Environment
    from .token import Token


DEFAULT_INNER_TAG_MAP = {
    "for": ["break", "continue"],
    "if": ["else", "elsif"],
    "case": ["when"],
    "unless": ["else", "elsif"],
}


InnerTagMap = Mapping[str, Iterable[str]]
TagMap = dict[str, list[Span]]


class TagAnalysis:
    """The result of analyzing a template's tags with `Environment.analyze_tags()`.

    Each of the following properties maps tag names to a list of their locations.
    Locations are (template_name, start_index) tuples.

    Note that `raw` tags are not included at all. The lexer converts them to text
    tokens before we get a chance to analyze them.

    Also be aware that reported `unexpected_tags` don't handle the possibility of an
    "inner" tag appearing in a partial template (using `{% include %}`), where
    appropriate enclosing block tags are in the parent template.

    Attributes:
        all_tags: A mapping of all tags to their locations. Includes "end", "inner"
            and unknown tags.
        tags: A mapping of tag names to their locations. Excludes "end" and "inner"
            tags.
        unclosed_tags: Block tags that don't have a matching "end" tag.
        unexpected_tags: Inner tags that are not properly enclosed by appropriate
            block tags. For example, an `{% else %}` that is not enclosed by a
            `{% for %}` or `{% unless %}` block.
        unknown_tags: Tags that are unknown to the environment.
    """

    def __init__(
        self,
        *,
        env: Environment,
        name: str,
        tokens: list[Token],
        inner_tags: Optional[InnerTagMap] = None,
    ) -> None:
        self.template_name = name

        # A mapping of all tags to their locations. Includes "end" and inner tags.
        self.all_tags = self._all_tags(tokens)

        # Reverse map of inner tags to possible enclosing block tags.
        inner_tags = inner_tags or DEFAULT_INNER_TAG_MAP
        self._inner_tags = defaultdict(set)
        for tag, inner in inner_tags.items():
            for inner_tag in inner:
                self._inner_tags[inner_tag].add(tag)

        # A mapping of tag names to their locations. Excludes inner tags and "end" tags.
        self.tags = {
            tag: loc
            for tag, loc in self.all_tags.items()
            if not tag.startswith("end") and tag not in self._inner_tags
        }

        (
            self.unclosed_tags,
            self.unexpected_tags,
            self.unknown_tags,
        ) = self._audit_tags(env, tokens)

    def _all_tags(self, tokens: list[Token]) -> TagMap:
        """Map tag names to their locations, similar to `Template.analyze` etc."""
        tags: DefaultDict[str, list[Span]] = defaultdict(list)
        for token in tokens:
            if token.kind == TOKEN_TAG:
                tags[token.value].append(Span(self.template_name, token.start_index))
        return dict(tags)

    def _audit_tags(  # noqa: PLR0912
        self,
        env: Environment,
        tokens: list[Token],
    ) -> tuple[TagMap, TagMap, TagMap]:
        block_stack: list[_BlockStackItem] = []
        unclosed_tags: TagMap = defaultdict(list)
        unexpected_tags: TagMap = defaultdict(list)
        unknown_tags: TagMap = defaultdict(list)

        # Relies on the "end" closing block tag convention.
        end_tags = {
            token.value
            for token in tokens
            if token.kind == TOKEN_TAG and token.value.startswith("end")
        }

        # Infer which tags are block tags. This may or may not match what the
        # environment's tag register believes are block tags.
        block_tags = {tag[3:] for tag in end_tags} | {
            tag.name for tag in env.tags.values() if tag.block
        }

        # Registered tags. "break" and "continue" are a special case.
        registered_tags = {
            name for name in env.tags if name not in ("break", "continue")
        }

        # Registered inline tags. We use this to find erroneous "end" tags.
        inline_tags = {tag.name for tag in env.tags.values() if not tag.block}

        # We use this to find unknown "end" tags.
        registered_end_blocks = {
            tag.end for tag in env.tags.values() if tag.block and tag.end
        }

        for token in tokens:
            if token.kind != TOKEN_TAG:
                continue

            tag_name = token.value

            if tag_name in block_tags:
                block_stack.append(_BlockStackItem(token))
            elif tag_name in end_tags:
                start_block_tag = block_stack.pop()
                if start_block_tag != tag_name[3:]:
                    # if start_block_tag.name not in inline_tags:
                    unclosed_tags[start_block_tag.name].append(
                        Span(self.template_name, start_block_tag.token.start_index)
                    )
                continue

            if tag_name not in registered_tags:
                # Possible enclosing tags for an inner tag.
                enclosing_tags: Iterable[str] = self._inner_tags.get(tag_name, [])
                if not enclosing_tags:
                    # Not an inner tag for any block.
                    unknown_tags[tag_name].append(
                        Span(self.template_name, token.start_index)
                    )
                elif not self._valid_inner_tag(
                    self._inner_tags.get(tag_name, []), block_stack
                ):
                    # An inner tag, but not valid for any blocks currently on the stack.
                    unexpected_tags[tag_name].append(
                        Span(self.template_name, token.start_index)
                    )

        # Catch any unclosed tags.
        for block in block_stack:
            unclosed_tags[block.name].append(
                Span(self.template_name, block.token.start_index)
            )

        # Catch bad "end" tags.
        for tag_name, locations in self.all_tags.items():
            if tag_name.startswith("end"):
                start_tag_name = tag_name[3:]
                if (
                    start_tag_name in inline_tags
                    and start_tag_name not in unknown_tags
                    or (
                        tag_name not in registered_end_blocks
                        and start_tag_name not in unknown_tags
                    )
                ):
                    unknown_tags[tag_name].extend(locations)

        return dict(unclosed_tags), dict(unexpected_tags), dict(unknown_tags)

    def _valid_inner_tag(
        self,
        tag_names: Iterable[str],
        block_stack: list[_BlockStackItem],
    ) -> bool:
        return any(tag_name in block_stack for tag_name in tag_names)


class _BlockStackItem:
    def __init__(self, token: Token) -> None:
        self.token = token
        self.name = token.value

    def __eq__(self, __o: object) -> bool:
        return __o == self.name or (
            isinstance(__o, _BlockStackItem) and self.name == __o.name
        )

    def __hash__(self) -> int:  # pragma: no cover
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"_BlockStackItem({self.name})"
