"""Tag and node definition for the built-in "for" tag."""

import sys

from typing import Optional
from typing import Any
from typing import List
from typing import Mapping
from typing import TextIO
from typing import Iterator

from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.expression import LoopExpression

from liquid.exceptions import BreakLoop
from liquid.exceptions import ContinueLoop

from liquid.lex import tokenize_loop_expression

from liquid.parse import get_parser
from liquid.parse import expect
from liquid.parse import parse_loop_expression

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG


TAG_FOR = sys.intern("for")
TAG_ENDFOR = sys.intern("endfor")
TAG_ELSE = sys.intern("else")

TAG_BREAK = sys.intern("break")
TAG_CONTINUE = sys.intern("continue")

ENDFORBLOCK = (TAG_ENDFOR, TAG_ELSE)
ENDFORELSEBLOCK = (TAG_ENDFOR,)


class ForLoop(Mapping[str, object]):
    """Loop helper variables."""

    __slots__ = (
        "name",
        "it",
        "length",
        "item",
        "first",
        "last",
        "index",
        "index0",
        "rindex",
        "rindex0",
        "_keys",
    )

    def __init__(self, name: str, it: Iterator[Any], length: int):
        self.name = name
        self.it = it
        self.length = length

        self.item = None
        self.first = False
        self.last = False
        self.index = 0
        self.index0 = -1
        self.rindex = self.length + 1
        self.rindex0 = self.length

        self._keys: List[str] = [
            "length",
            "index",
            "index0",
            "rindex",
            "rindex0",
            "first",
            "last",
        ]

    def __repr__(self) -> str:  # pragma: no cover
        return f"ForLoop(name='{self.name}', length={self.length})"

    def __getitem__(self, key: str) -> object:
        if key in self._keys:
            return getattr(self, key)
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._keys)

    def __next__(self) -> object:
        self.step()
        return next(self.it)

    def __iter__(self) -> Iterator[Any]:
        return self

    def __str__(self) -> str:
        return "ForLoop"

    def step(self) -> None:
        """Set the value for the current/next loop iteration and update forloop
        helper variables."""

        self.index += 1
        self.index0 += 1
        self.rindex -= 1
        self.rindex0 -= 1

        if self.index0 == 0:
            self.first = True
        else:
            self.first = False

        if self.rindex0 == 0:
            self.last = True
        else:
            self.last = False

        return None


class ForNode(Node):
    """Parse tree node for the built-in "for" tag."""

    __slots__ = ("tok", "expression", "block", "default")

    def __init__(
        self,
        tok: Token,
        expression: LoopExpression,
        block: BlockNode,
        default: Optional[BlockNode] = None,
    ):
        self.tok = tok
        self.expression = expression
        self.block = block
        self.default = default

    def __str__(self) -> str:
        tag_str = f"for ({self.expression}) {{ {self.block} }}"

        if self.default:
            tag_str += f" else {{ {self.default} }}"

        return tag_str

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        loop_iter, length = self.expression.evaluate(context)

        if length:
            name = self.expression.name

            forloop = ForLoop(
                name=name,
                it=loop_iter,
                length=length,
            )

            namespace = {
                "forloop": forloop,
                name: None,
            }

            # Extend the context. Essentially giving priority to `ForLoopDrop`, then
            # delegating `get` and `assign` to the outer context.
            with context.extend(namespace):

                for itm in forloop:
                    namespace[name] = itm

                    try:
                        self.block.render(context, buffer)
                    except ContinueLoop:
                        continue
                    except BreakLoop:
                        break

        elif self.default:
            self.default.render(context, buffer)

        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        loop_iter, length = await self.expression.evaluate_async(context)

        if length:
            name = self.expression.name

            forloop = ForLoop(
                name=name,
                it=loop_iter,
                length=length,
            )

            namespace = {
                "forloop": forloop,
                name: None,
            }

            # Extend the context. Essentially giving priority to `ForLoopDrop`, then
            # delegating `get` and `assign` to the outer context.
            with context.extend(namespace):

                for itm in forloop:
                    namespace[name] = itm

                    try:
                        await self.block.render_async(context, buffer)
                    except ContinueLoop:
                        continue
                    except BreakLoop:
                        break

        elif self.default:
            await self.default.render_async(context, buffer)

        return None


class BreakNode(Node):
    """Parse tree node for the built-in "break" tag."""

    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "`break`"

    def render_to_output(
        self,
        context: Context,
        buffer: TextIO,
    ) -> Optional[bool]:
        raise BreakLoop("break")


class ContinueNode(Node):
    """Parse tree node for the built-in "continue" tag."""

    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "`continue`"

    def render_to_output(
        self,
        context: Context,
        buffer: TextIO,
    ) -> Optional[bool]:
        raise ContinueLoop("continue")


class ForTag(Tag):
    """The built-in "for" tag."""

    name = TAG_FOR
    end = TAG_ENDFOR

    def parse(self, stream: TokenStream) -> Node:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG, value=TAG_FOR)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_loop_expression(stream.current.value)
        expr = parse_loop_expression(TokenStream(expr_iter))

        stream.next_token()

        block = parser.parse_block(stream, ENDFORBLOCK)
        default: Optional[BlockNode] = None

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            default = parser.parse_block(stream, ENDFORELSEBLOCK)

        expect(stream, TOKEN_TAG, value=TAG_ENDFOR)
        return ForNode(tok, expression=expr, block=block, default=default)


class BreakTag(Tag):
    """The built-in "break" tag."""

    name = TAG_BREAK
    block = False

    def parse(self, stream: TokenStream) -> BreakNode:
        expect(stream, TOKEN_TAG, value=TAG_BREAK)
        return BreakNode(stream.current)


class ContinueTag(Tag):
    """The built-in "continue" tag."""

    name = TAG_CONTINUE
    block = False

    def parse(self, stream: TokenStream) -> ContinueNode:
        expect(stream, TOKEN_TAG, value=TAG_CONTINUE)
        return ContinueNode(stream.current)
