import sys
from typing import Optional, TextIO

from liquid.token import (
    Token,
    TOKEN_EXPRESSION,
    TOKEN_TAG_NAME,
    TOKEN_IDENTIFIER,
    TOKEN_EOF,
)
from liquid.tag import Tag
from liquid import ast
from liquid.lex import TokenStream, get_expression_lexer
from liquid.expression import Identifier
from liquid.context import Context
from liquid.parse import get_parser, expect, parse_identifier

from liquid import Compiler
from liquid import Opcode
from liquid.object import CompiledBlock

TAG_FORM = sys.intern("form")
TAG_ENDFORM = sys.intern("endform")


class CommentFormNode(ast.Node):
    __slots__ = ("tok", "article", "block")

    def __init__(self, tok: Token, article: Identifier, block: ast.BlockNode):
        self.tok = tok
        self.article = article
        self.block = block

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        article = self.article.evaluate(context)
        form = {
            "posted_successfully?": context.get("posted_successfully", True),
            "errors": context.get(["comment", "errors"], []),
            "author": context.get(["comment", "author"]),
            "email": context.get(["comment", "email"]),
            "body": context.get(["comment", "body"]),
        }

        ctx = context.extend({"form": form})

        buffer.write(
            f'<form id="article-{article["id"]}-comment-form" '
            'class="comment-form" method="post" action="">\n'
        )
        self.block.render(ctx, buffer)
        buffer.write("\n</form>")

    def compile_node(self, compiler: Compiler):
        compiler.enter_scope()

        compiler.symbol_table.define(TAG_FORM)
        self.block.compile(compiler)

        compiler.emit(Opcode.LBL)  # Leave block

        free_symbols = compiler.symbol_table.free_symbols
        num_block_vars = compiler.symbol_table.locals.size
        assert num_block_vars == 1

        instructions = compiler.leave_scope()

        # num_arguments is always 1. The target article.
        compiled_block = CompiledBlock(
            instructions=instructions,
            num_locals=num_block_vars,
            num_arguments=1,
            num_free=len(free_symbols),
        )

        compiler.emit(Opcode.CONSTANT, compiler.add_constant(compiled_block))

        for free_symbol in reversed(free_symbols):
            compiler.load_symbol(free_symbol)

        # Target article
        self.article.compile(compiler)

        # Block name. The VM needs to lookup the appropriate function to
        # populate the "form" drop/mapping.
        compiler.emit(Opcode.CONSTANT, compiler.add_constant(TAG_FORM))

        compiler.emit(Opcode.EBL, compiled_block.num_arguments, compiled_block.num_free)


class CommentFormTag(Tag):

    name = TAG_FORM
    end = TAG_ENDFORM

    def parse(self, stream: TokenStream) -> ast.Node:
        lexer = get_expression_lexer(self.env)
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_FORM)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = lexer.tokenize(stream.current.value)

        expect(expr_stream, TOKEN_IDENTIFIER)
        article = parse_identifier(expr_stream)
        expr_stream.next_token()

        # End of expression
        expect(expr_stream, TOKEN_EOF)

        # Advance the stream passed the expression and read the block.
        stream.next_token()
        block = parser.parse_block(stream, end=(TAG_ENDFORM,))
        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDFORM)

        return CommentFormNode(tok, article=article, block=block)
