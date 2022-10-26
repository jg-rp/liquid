"""Tag and node definition for the built-in "tablerow" tag."""
import sys

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

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.expression import LoopExpression
from liquid.expression import NIL
from liquid.limits import to_int

from liquid.parse import expect
from liquid.parse import get_parser

from liquid.tag import Tag
from liquid.stream import TokenStream


TAG_TABLEROW = sys.intern("tablerow")
TAG_ENDTABLEROW = sys.intern("endtablerow")

END_TAGBLOCK = frozenset((TAG_ENDTABLEROW,))


# pylint: disable=too-many-instance-attributes
class TableRow(Mapping[str, object]):
    """Table row helper variables."""

    __slots__ = (
        "name",
        "it",
        "length",
        "ncols",
        "_index",
        "_row",
        "_col",
    )

    _keys = frozenset(
        [
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
            "row",
        ]
    )

    def __init__(self, name: str, it: Iterator[Any], length: int, ncols: int) -> None:
        self.name = name
        self.it = it
        self.length = length
        self.ncols = ncols
        self._index = -1
        self._row = 1
        self._col = 0

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
        self.step()
        return next(self.it)

    @property
    def index(self) -> int:
        """The 1-based index of the current loop iteration."""
        return self._index + 1

    @property
    def index0(self) -> int:
        """The 0-based index of the current loop iteration."""
        return self._index

    @property
    def rindex(self) -> int:
        """The 1-based index, counting from the right, of the current loop iteration."""
        return self.length - self._index

    @property
    def rindex0(self) -> int:
        """The 0-based index, counting from the right, of the current loop iteration."""
        return self.length - self._index - 1

    @property
    def first(self) -> bool:
        """True if this is the first iteration, false otherwise."""
        return self._index == 0

    @property
    def last(self) -> bool:
        """True if this is the last iteration, false otherwise."""
        return self._index == self.length - 1

    @property
    def col(self) -> int:
        """The 1-based index of the current column."""
        return self._col

    @property
    def col0(self) -> int:
        """The 0-based index of the current column."""
        return self._col - 1

    @property
    def col_first(self) -> bool:
        """True if this is the first column. False otherwise"""
        return self._col == 1

    @property
    def col_last(self) -> bool:
        """True if this is the last iteration, false otherwise."""
        return self._col == self.ncols

    @property
    def row(self) -> int:
        """The current row number."""
        return self._row

    def step(self) -> None:
        """Step the forloop forward."""
        self._index += 1
        if self._col == self.ncols:
            self._col = 1
            self._row += 1
        else:
            self._col += 1


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

    def _int_or_zero(self, arg: object) -> int:
        try:
            return to_int(arg)
        except ValueError:
            return 0

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        name = self.expression.name
        loop_iter, length = self.expression.evaluate(context)

        if self.expression.cols and self.expression.cols != NIL:
            cols = self._int_or_zero(self.expression.cols.evaluate(context))
        else:
            cols = length

        context.raise_for_loop_limit(length)
        tablerow = TableRow(name, loop_iter, length, cols)

        namespace: Dict[str, object] = {
            "tablerowloop": tablerow,
        }

        buffer.write('<tr class="row1">\n')

        with context.extend(namespace):
            for item in tablerow:
                namespace[name] = item
                buffer.write(f'<td class="col{tablerow.col}">')
                self.block.render(context=context, buffer=buffer)
                buffer.write("</td>")

                if tablerow.col_last and not tablerow.last:
                    buffer.write(f'</tr>\n<tr class="row{tablerow.row + 1}">')

            buffer.write("</tr>\n")
        return True

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        name = self.expression.name
        loop_iter, length = await self.expression.evaluate_async(context)

        if self.expression.cols and self.expression.cols != NIL:
            cols = self._int_or_zero(await self.expression.cols.evaluate_async(context))
        else:
            cols = length

        context.raise_for_loop_limit(length)
        tablerow = TableRow(name, loop_iter, length, cols)

        namespace: Dict[str, object] = {
            "tablerowloop": tablerow,
        }

        buffer.write('<tr class="row1">\n')

        with context.extend(namespace):
            for item in tablerow:
                namespace[name] = item
                buffer.write(f'<td class="col{tablerow.col}">')
                await self.block.render_async(context=context, buffer=buffer)
                buffer.write("</td>")

                if tablerow.col_last and not tablerow.last:
                    buffer.write(f'</tr>\n<tr class="row{tablerow.row + 1}">')

            buffer.write("</tr>\n")
        return True

    def children(self) -> List[ChildNode]:
        return [
            ChildNode(
                linenum=self.block.tok.linenum,
                node=self.block,
                expression=self.expression,
                block_scope=["tablerowloop", self.expression.name],
            )
        ]


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
        loop_expression = self.env.parse_loop_expression_value(stream.current.value)
        stream.next_token()

        block = parser.parse_block(stream, END_TAGBLOCK)
        expect(stream, TOKEN_TAG, value=TAG_ENDTABLEROW)

        return TablerowNode(tok, expression=loop_expression, block=block)
