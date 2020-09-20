""""""
import sys
from typing import TextIO

from liquid.token import Token, TOKEN_TAG_NAME, TOKEN_EXPRESSION
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream
from liquid.parse import expect
from liquid.compiler import Compiler
from liquid.code import Opcode

TAG_DECREMENT = sys.intern("decrement")


class DecrementNode(ast.Node):
    __slots__ = ("tok", "identifier")

    def __init__(self, tok: Token, identifier: str):
        self.tok = tok
        self.identifier = identifier

    def __str__(self) -> str:
        return f"{self.identifier} -= 1"

    def render_to_output(self, context: Context, buffer: TextIO):
        buffer.write(str(context.decrement(self.identifier)))

    def compile_node(self, compiler: Compiler):
        symbol = compiler.symbol_table.define_counter(self.identifier)
        compiler.emit(Opcode.DEC, symbol.index)


class DecrementTag(Tag):
    """

    Increment and decrement tags share a namespace.
    """

    name = TAG_DECREMENT

    def __init__(self, env, block: bool = False):
        super().__init__(env, block)

    def parse(self, stream: TokenStream) -> DecrementNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_DECREMENT)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)

        # The tag expression is assumed to be an unquoted identifier.
        # TODO: Validate identifier
        return DecrementNode(tok=tok, identifier=stream.current.value)
