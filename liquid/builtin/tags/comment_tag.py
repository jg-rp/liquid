""""""
import sys
from typing import Optional, TextIO

from liquid.token import Token, TOKEN_TAG_NAME
from liquid.parse import expect, eat_block
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream
from liquid.compiler import Compiler

TAG_COMMENT = sys.intern("comment")
RAG_ENDCOMMENT = sys.intern("endcomment")


class CommentNode(ast.Node):
    __slots__ = ("tok", "statements")

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "/* */"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        return False

    def compile_node(self, compiler: Compiler):
        pass


class CommentTag(Tag):

    name = TAG_COMMENT
    end = RAG_ENDCOMMENT

    def parse(self, stream: TokenStream) -> CommentNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_COMMENT)
        stream.next_token()

        tag = CommentNode(stream.current)
        eat_block(stream, end=(RAG_ENDCOMMENT,))

        expect(stream, TOKEN_TAG_NAME, value=RAG_ENDCOMMENT)
        return tag
