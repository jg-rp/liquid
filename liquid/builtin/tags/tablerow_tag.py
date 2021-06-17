"""Tag and node definition for the built-in "tablerow" tag."""

import math
import sys

from itertools import islice

from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import TextIO
from typing import Iterator

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.expression import LoopExpression
from liquid.lex import tokenize_loop_expression

from liquid.parse import expect
from liquid.parse import parse_loop_expression
from liquid.parse import get_parser

from liquid.tag import Tag
from liquid.stream import TokenStream


TAG_TABLEROW = sys.intern("tablerow")
TAG_ENDTABLEROW = sys.intern("endtablerow")


class TableRow(Mapping[str, object]):
    """Table row helper variables."""

    __slots__ = (
        "name",
        "it",
        "length",
        "ncols",
        "item",
        "first",
        "last",
        "index",
        "index0",
        "rindex",
        "rindex0",
        "col",
        "col0",
        "col_first",
        "col_last",
        "_keys",
        "row",
        "nrows",
    )

    def __init__(self, name: str, it: Iterator[Any], length: int, ncols: int) -> None:
        self.name = name
        self.it = it
        self.length = length
        self.ncols = ncols
        self.item = None

        self.first = False
        self.last = False
        self.index = 0
        self.index0 = -1
        self.rindex = self.length + 1
        self.rindex0 = self.length

        self.col = 0
        self.col0 = -1
        self.col_first = True
        self.col_last = False

        # Zero based row counter is not exposed to templates.
        self.row = 0
        self.nrows = math.ceil(self.length / self.ncols)

        self._keys: List[str] = [
            "length",
            "index",
            "index0",
            "rindex",
            "rindex0",
            "first",
            "last",
            "col",
            "col0",
            "col_first",
            "col_last",
        ]

    def __repr__(self) -> str:  # pragma: no cover
        return f"TableRow(name='{self.name}', length={self.length})"

    def __getitem__(self, key: str) -> object:
        if key in self._keys:
            return getattr(self, key)
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> object:
        return next(self.it)

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

        self.col0 = self.index0 % self.ncols
        self.col = self.col0 + 1

        if self.col == 1:
            self.col_first = True
        else:
            self.col_first = False

        if self.col == self.ncols:
            self.col_last = True
        else:
            self.col_last = False

        if self.col == 1:
            self.row += 1


class TablerowNode(Node):
    """Parse tree node for the built-in "tablerow" tag."""

    __slots__ = ("tok", "expression", "block")

    def __init__(
        self,
        tok: Token,
        expression: LoopExpression,
        block: BlockNode,
    ):
        self.tok = tok
        self.expression = expression
        self.block = block

    def __str__(self) -> str:
        return f"tablerow({ self.expression }) {{ {self.block} }}"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        name = self.expression.name
        loop_iter, length = self.expression.evaluate(context)

        if self.expression.cols:
            cols = self.expression.cols.evaluate(context)
            assert isinstance(cols, int)
        else:
            cols = length

        loop_iter = grouper(loop_iter, cols)
        tablerow = TableRow(name, loop_iter, length, cols)

        namespace: Dict[str, object] = {
            "tablerowloop": tablerow,
            name: None,
        }

        with context.extend(namespace):
            for i, row in enumerate(tablerow):
                buffer.write(f'<tr class="row{i+1}">')

                for j, itm in enumerate(row):
                    tablerow.step()
                    namespace[name] = itm

                    buffer.write(f'<td class="col{j+1}">')
                    self.block.render(context=context, buffer=buffer)
                    buffer.write("</td>")

                buffer.write("</tr>")

        return None

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        name = self.expression.name
        loop_iter, length = await self.expression.evaluate_async(context)

        if self.expression.cols:
            cols = await self.expression.cols.evaluate_async(context)
            assert isinstance(cols, int)
        else:
            cols = length

        loop_iter = grouper(loop_iter, cols)
        tablerow = TableRow(name, loop_iter, length, cols)

        namespace: Dict[str, object] = {
            "tablerowloop": tablerow,
            name: None,
        }

        with context.extend(namespace):
            for i, row in enumerate(tablerow):
                buffer.write(f'<tr class="row{i+1}">')

                for j, itm in enumerate(row):
                    tablerow.step()
                    namespace[name] = itm

                    buffer.write(f'<td class="col{j+1}">')
                    await self.block.render_async(context=context, buffer=buffer)
                    buffer.write("</td>")

                buffer.write("</tr>")

        return None


class TablerowTag(Tag):
    """The built-in "tablerow" tag."""

    name = TAG_TABLEROW
    end = TAG_ENDTABLEROW

    def parse(self, stream: TokenStream) -> TablerowNode:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG, value=TAG_TABLEROW)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_loop_expression(stream.current.value)
        loop_expression = parse_loop_expression(TokenStream(expr_iter))
        stream.next_token()

        block = parser.parse_block(stream, (TAG_ENDTABLEROW,))
        expect(stream, TOKEN_TAG, value=TAG_ENDTABLEROW)

        return TablerowNode(tok, expression=loop_expression, block=block)


def grouper(iterator: Iterator[Any], n: int) -> Iterator[Any]:
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3) --> ABC DEF G"
    return iter(lambda: tuple(islice(iterator, n)), ())
