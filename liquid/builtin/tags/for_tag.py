import collections.abc
import sys
from typing import Optional, Any, List, TextIO, Union

from liquid.token import Token, TOKEN_EXPRESSION, TOKEN_TAG_NAME
from liquid.parse import get_parser, expect, parse_loop_expression
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream, get_expression_lexer
from liquid.expression import LoopExpression
from liquid.exceptions import BreakLoop, ContinueLoop
from liquid.compiler import Compiler
from liquid.code import Opcode

TAG_FOR = sys.intern("for")
TAG_ENDFOR = sys.intern("endfor")
TAG_ELSE = sys.intern("else")

TAG_BREAK = sys.intern("break")
TAG_CONTINUE = sys.intern("continue")

ENDFORBLOCK = (TAG_ENDFOR, TAG_ELSE)
ENDFORELSEBLOCK = (TAG_ENDFOR,)


class ForLoop(collections.abc.Mapping):
    """Loop helper variables."""

    __slots__ = (
        "name",
        "length",
        "item",
        "first",
        "last",
        "index",
        "index0",
        "rindex",
        "rindex0",
        "keys",
    )

    # TODO: Change `name` to `id` because it could be an int?
    def __init__(self, name: Union[str, int], length: int):
        self.name = name
        self.length = length

        self.item = None
        self.first = False
        self.last = False
        self.index = 0
        self.index0 = -1
        self.rindex = self.length + 1
        self.rindex0 = self.length

        self.keys: List[str] = [
            "length",
            "index",
            "index0",
            "rindex",
            "rindex0",
            "first",
            "last",
        ]

    def __repr__(self):  # pragma: no cover
        return f"ForLoop(name='{self.name}', length={self.length})"

    def __getitem__(self, key):
        if key in self.keys:
            return getattr(self, key)
        raise KeyError(key)

    def __len__(self):
        return len(self.keys)

    def __iter__(self):
        return iter(self.keys)

    def step(self, item: Any):
        """Set the value for the current/next loop iteration and update forloop
        helper variables."""
        self.item = item

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


class ForLoopDrop(collections.abc.Mapping):
    """Wrap a `ForLoop` so it can be used as a `Context` namepsace."""

    __slots__ = ("forloop", "name")

    def __init__(self, name: Union[str, int], length: int):
        self.name = name
        self.forloop = ForLoop(name, length)

    def __contains__(self, item):
        if item in ("forloop", self.name):
            return True
        return False

    def __getitem__(self, key):
        if key == "forloop":
            return self.forloop
        if key == self.name:
            return self.forloop.item
        raise KeyError(str(key))

    def __len__(self):
        return 2

    def __iter__(self):
        return iter(["forloop", self.name])

    def __str__(self):
        return "ForLoop"

    def step(self, item):
        self.forloop.step(item)


class ForNode(ast.Node):
    """A parse tree node representing a for loop tag block."""

    __slots__ = ("tok", "expression", "block", "default")

    statement = False

    def __init__(
        self,
        tok: Token,
        expression: LoopExpression,
        block: ast.BlockNode = None,
        default: Optional[ast.BlockNode] = None,
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

    def render_to_output(self, context: Context, buffer: TextIO):
        loop_iter = self.expression.evaluate(context)
        loop_items = list(loop_iter)  # Need the length ahead of time.

        if loop_items:
            # A `ForLoopDrop` maintains read-only helper variables for the lifetime of the
            # loop block. Each time we iterate the loop, we step the helper class to
            # advance its various counters.
            drop = ForLoopDrop(name=str(self.expression.name), length=len(loop_items))

            # Extend the context. Essentially giving priority to `ForLoopDrop`, then
            # delegating `get` and `assign` to the outer context.
            ctx = context.extend(drop)

            for itm in loop_items:
                # Step the forloop helper. `ForLoop` does not initialised with an item,
                # so we must step at the start of each iteration, not the end.
                drop.step(itm)

                try:
                    self.block.render(ctx, buffer)
                except ContinueLoop:
                    continue
                except BreakLoop:
                    break

        else:
            # Empty iterator, try default
            if self.default:
                self.default.render(context, buffer)

    def compile_node(self, compiler: Compiler):
        symbol = compiler.symbol_table.define(self.expression.name)
        self.expression.compile(compiler)

        for_pos = compiler.emit(Opcode.FOR, symbol.index, 9999, 9999)

        # Jump to default if empty iterator
        jump_to_default_pos = compiler.emit(Opcode.JIE, 9999, symbol.index)

        top_of_loop = compiler.emit(Opcode.JSI, 9999, symbol.index)  # Jump past default
        self.block.compile(compiler)

        compiler.emit(Opcode.STE, symbol.index)
        compiler.emit(Opcode.JMP, top_of_loop)

        after_loop_block_pos = len(compiler.current_instructions())
        compiler.change_operand(jump_to_default_pos, after_loop_block_pos, symbol.index)

        if self.default:
            self.default.compile(compiler)
        else:
            compiler.emit(Opcode.NOP)

        after_default_pos = len(compiler.current_instructions())
        compiler.change_operand(top_of_loop, after_default_pos, symbol.index)
        compiler.change_operand(for_pos, symbol.index, top_of_loop, after_default_pos)


class BreakNode(ast.Node):
    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "`break`"

    def render_to_output(self, context: Context, buffer: TextIO):
        raise BreakLoop("break")

    def compile_node(self, compiler: Compiler):
        compiler.emit(Opcode.BRK)


class ContinueNode(ast.Node):
    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "`continue`"

    def render_to_output(self, context: Context, buffer: TextIO):
        raise ContinueLoop("continue")

    def compile_node(self, compiler: Compiler):
        compiler.emit(Opcode.CON)


class ForTag(Tag):
    """Loop over items in an array, pairs of items in a hash, or integers in a range.

    For loop blocks share scope with their document. So assigning to a variable inside
    a for loop will add to the document's "local" namespace and persist after the loop
    has finished.

    To support nested loops and to remove "forloop" helpers, after each loop has finished,
    we push a "ForLoopDrop" to the context scope, then pop it after.
    """

    name = TAG_FOR
    end = TAG_ENDFOR

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)
        lexer = get_expression_lexer(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_FOR)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = lexer.tokenize(stream.current.value)
        expr = parse_loop_expression(expr_iter)

        tag = ForNode(tok, expression=expr)
        stream.next_token()

        tag.block = parser.parse_block(stream, ENDFORBLOCK)

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            tag.default = parser.parse_block(stream, ENDFORELSEBLOCK)

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDFOR)
        return tag


class BreakTag(Tag):

    name = TAG_BREAK

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> BreakNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_BREAK)
        return BreakNode(stream.current)


class ContinueTag(Tag):

    name = TAG_CONTINUE

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> ContinueNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_CONTINUE)
        return ContinueNode(stream.current)
