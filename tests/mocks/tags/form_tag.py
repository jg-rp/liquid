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
from liquid.lex import TokenStream, tokenize_identifier
from liquid.expression import Identifier
from liquid.context import Context
from liquid.parse import get_parser, expect, parse_identifier


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

        buffer.write(
            f'<form id="article-{article["id"]}-comment-form" '
            'class="comment-form" method="post" action="">\n'
        )

        with context.extend({"form": form}):
            self.block.render(context, buffer)

        buffer.write("\n</form>")


class CommentFormTag(Tag):

    name = TAG_FORM
    end = TAG_ENDFORM

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_FORM)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_identifier(stream.current.value))

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
