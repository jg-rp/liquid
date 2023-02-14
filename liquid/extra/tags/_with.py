"""Node and tag definitions for `with`."""
# pylint: disable=missing-class-docstring
from __future__ import annotations

import sys

from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.expression import Expression
from liquid.expressions import parse_keyword_arguments

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF


if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment

TAG_WITH = sys.intern("with")
TAG_ENDWITH = sys.intern("endwith")


class WithKeywordArg(NamedTuple):
    name: str
    expr: Expression


class WithNode(Node):
    __slots__ = ("tok", "args", "block")

    def __init__(self, tok: Token, args: Dict[str, Expression], block: BlockNode):
        self.tok = tok
        self.args = args
        self.block = block

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        namespace = {k: v.evaluate(context) for k, v in self.args.items()}

        with context.extend(namespace):
            return self.block.render(context, buffer)

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        namespace = {k: await v.evaluate_async(context) for k, v in self.args.items()}
        with context.extend(namespace):
            return await self.block.render_async(context, buffer)

    def children(self) -> List[ChildNode]:
        return [
            ChildNode(
                linenum=self.tok.linenum, node=self.block, block_scope=list(self.args)
            ),
            *[
                ChildNode(linenum=self.tok.linenum, expression=expr)
                for expr in self.args.values()
            ],
        ]


class WithTag(Tag):
    name = TAG_WITH
    end = TAG_ENDWITH

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_WITH)
        tok = next(stream)

        # Parse keyword arguments
        expect(stream, TOKEN_EXPRESSION)
        args = parse_keyword_arguments(stream.current.value)
        stream.next_token()

        # Parse the block
        block = self.parser.parse_block(stream, (TAG_ENDWITH, TOKEN_EOF))
        expect(stream, TOKEN_TAG, value=TAG_ENDWITH)

        return WithNode(tok=tok, args=args, block=block)
