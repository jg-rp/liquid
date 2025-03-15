"""The built-in _tablerow_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import TextIO

from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import LoopExpression
from liquid.exceptions import BreakLoop
from liquid.exceptions import ContinueLoop
from liquid.limits import to_int
from liquid.parser import get_parser
from liquid.tag import Tag
from liquid.token import TOKEN_TAG
from liquid.token import Token

if TYPE_CHECKING:
    from liquid.context import RenderContext
    from liquid.expression import Expression
    from liquid.stream import TokenStream


TAG_TABLEROW = sys.intern("tablerow")
TAG_ENDTABLEROW = sys.intern("endtablerow")

END_TAGBLOCK = frozenset((TAG_ENDTABLEROW,))


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
        """True if this is the first column. False otherwise."""
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
    """The built-in _tablerow_ tag."""

    interrupts = True
    """If _true_, handle `break` and `continue` interrupts inside a tablerow loop."""

    __slots__ = ("expression", "block")

    def __init__(
        self,
        token: Token,
        expression: LoopExpression,
        block: BlockNode,
    ):
        super().__init__(token)
        self.expression = expression
        self.block = block
        self.blank = False

    def __str__(self) -> str:
        return f"tablerow({self.expression}) {{ {self.block} }}"

    def _int_or_zero(self, arg: object) -> int:
        try:
            return to_int(arg)
        except ValueError:
            return 0

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Return this node's children."""
        name = self.expression.identifier
        loop_iter, length = self.expression.evaluate(context)

        if self.expression.cols:
            cols = self._int_or_zero(self.expression.cols.evaluate(context))
        else:
            cols = length

        context.raise_for_loop_limit(length)
        tablerow = TableRow(name, loop_iter, length, cols)

        namespace: dict[str, object] = {
            "tablerowloop": tablerow,
        }

        buffer.write('<tr class="row1">\n')
        _break = False

        with context.extend(namespace):
            for item in tablerow:
                namespace[name] = item
                buffer.write(f'<td class="col{tablerow.col}">')

                try:
                    self.block.render(context=context, buffer=buffer)
                except BreakLoop:
                    if self.interrupts:
                        _break = True
                    else:
                        raise
                except ContinueLoop:
                    if not self.interrupts:
                        raise

                buffer.write("</td>")

                if tablerow.col_last and not tablerow.last:
                    buffer.write(f'</tr>\n<tr class="row{tablerow.row + 1}">')

                if _break:
                    break

        buffer.write("</tr>\n")
        return True

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Return this node's children."""
        name = self.expression.identifier
        loop_iter, length = await self.expression.evaluate_async(context)

        if self.expression.cols:
            cols = self._int_or_zero(await self.expression.cols.evaluate_async(context))
        else:
            cols = length

        context.raise_for_loop_limit(length)
        tablerow = TableRow(name, loop_iter, length, cols)

        namespace: dict[str, object] = {
            "tablerowloop": tablerow,
        }

        buffer.write('<tr class="row1">\n')
        _break = False

        with context.extend(namespace):
            for item in tablerow:
                namespace[name] = item
                buffer.write(f'<td class="col{tablerow.col}">')

                try:
                    await self.block.render_async(context=context, buffer=buffer)
                except BreakLoop:
                    if self.interrupts:
                        _break = True
                    else:
                        raise
                except ContinueLoop:
                    if not self.interrupts:
                        raise

                buffer.write("</td>")

                if tablerow.col_last and not tablerow.last:
                    buffer.write(f'</tr>\n<tr class="row{tablerow.row + 1}">')

                if _break:
                    break

        buffer.write("</tr>\n")
        return True

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.block

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield self.expression

    def block_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the node's block scope."""
        yield Identifier(self.expression.identifier, token=self.expression.token)
        yield Identifier("tablerowloop", token=self.token)


class TablerowTag(Tag):
    """The built-in _tablerow_ tag."""

    name = TAG_TABLEROW
    end = TAG_ENDTABLEROW
    node_class = TablerowNode

    def parse(self, stream: TokenStream) -> TablerowNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)
        tokens = stream.into_inner(tag=token)
        expr = LoopExpression.parse(self.env, tokens)
        block = get_parser(self.env).parse_block(stream, END_TAGBLOCK)
        stream.expect(TOKEN_TAG, value=TAG_ENDTABLEROW)
        return self.node_class(token, expression=expr, block=block)
