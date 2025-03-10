"""The built-in _liquid_ tag."""

from __future__ import annotations

import re
import sys
from functools import partial
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Pattern
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.exceptions import LiquidSyntaxError
from liquid.parser import get_parser
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid import Environment
    from liquid import RenderContext

TAG_LIQUID = sys.intern("liquid")


class LiquidNode(Node):
    """The built-in _liquid_ tag."""

    __slots__ = (
        "liquid_token",
        "block",
    )

    def __init__(self, token: Token, liquid_token: Optional[Token], block: BlockNode):
        super().__init__(token)
        self.liquid_token = liquid_token
        self.block = block
        self.blank = block.blank

    def __str__(self) -> str:
        # NOTE: We're using a string representation of the token, not the node.
        # Which might cause issues later.
        expr = self.liquid_token.value if self.liquid_token else ""
        return f"{{% liquid {expr} %}}"

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        return self.block.render(context, buffer)

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        return await self.block.render_async(context, buffer)

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.block


class LiquidTag(Tag):
    """The built-in "liquid" tag."""

    name = TAG_LIQUID
    block = False
    node_class = LiquidNode

    def __init__(self, env: Environment):
        super().__init__(env)

        comment_start_string = env.comment_start_string.replace("{", "")

        if comment_start_string:
            seq = re.escape(comment_start_string)
            rules = (
                (
                    "LIQUID_EXPR",
                    rf"[ \t]*(?P<name>(\w+|{seq}))[ \t]*(?P<expr>.*?)[ \t\r]*?(\n+|$)",
                ),
                ("SKIP", r"[\r\n]+"),
                (TOKEN_ILLEGAL, r"."),
            )
        else:
            rules = (
                (
                    "LIQUID_EXPR",
                    r"[ \t]*(?P<name>#|\w+)[ \t]*(?P<expr>.*?)[ \t\r]*?(\n+|$)",
                ),
                ("SKIP", r"[\r\n]+"),
                (TOKEN_ILLEGAL, r"."),
            )

        self._tokenize = partial(
            _tokenize_liquid_expression,
            rules=_compile_rules(rules),
            comment_start_string=comment_start_string,
        )

    def parse(self, stream: TokenStream) -> Node:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        token_: Optional[Token] = None

        if stream.current.kind == TOKEN_EOF:
            # Empty liquid tag. Empty block.
            block = BlockNode(token, [])
        elif stream.current.kind == TOKEN_TAG:
            parser = get_parser(self.env)
            block = parser.parse_block(stream, end=())
        else:
            token_ = stream.expect(TOKEN_EXPRESSION)
            block = get_parser(self.env).parse_block(
                TokenStream(
                    self._tokenize(
                        token_.value,
                        token=token_,
                    )
                ),
                end=(),
            )

        return self.node_class(token, token_, block=block)


def _tokenize_liquid_expression(
    source: str,
    rules: Pattern[str],
    token: Token,
    comment_start_string: str,
) -> Iterator[Token]:
    """Tokenize a "{% liquid %}" tag."""
    for match in rules.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()

        if kind == "LIQUID_EXPR":
            name = match.group("name")
            if name == comment_start_string:
                continue

            yield Token(
                TOKEN_TAG,
                value=name,
                start_index=token.start_index + match.start("name"),
                source=token.source,
            )

            if match.group("expr"):
                yield Token(
                    TOKEN_EXPRESSION,
                    value=match.group("expr"),
                    start_index=token.start_index + match.start("expr"),
                    source=token.source,
                )
        elif kind == "SKIP":
            continue
        else:
            raise LiquidSyntaxError(
                f"expected newline delimited tag expressions, found {value!r}",
                token=token,
            )


def _compile_rules(rules: Iterable[tuple[str, str]]) -> Pattern[str]:
    """Compile the given rules into a single regular expression."""
    pattern = "|".join(f"(?P<{name}>{pattern})" for name, pattern in rules)
    return re.compile(pattern, re.DOTALL)
