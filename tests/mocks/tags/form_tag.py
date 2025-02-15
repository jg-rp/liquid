"""Tag and node definition for the mock "form" tag."""

import sys
from collections import abc
from typing import Optional
from typing import TextIO

from liquid import ast
from liquid.context import Context
from liquid.expression import Identifier
from liquid.lex import tokenize_identifier
from liquid.parse import expect
from liquid.parse import get_parser
from liquid.parse import parse_identifier
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_TAG
from liquid.token import Token

TAG_FORM = sys.intern("form")
TAG_ENDFORM = sys.intern("endform")

END_FORMBLOCK = frozenset((TAG_ENDFORM,))


class CommentFormNode(ast.Node):
    """Parse tree node for the mock "form" tag."""

    __slots__ = ("tok", "article", "block")

    def __init__(self, tok: Token, article: Identifier, block: ast.BlockNode):
        self.tok = tok
        self.article = article
        self.block = block

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        article = self.article.evaluate(context)
        assert isinstance(article, abc.Mapping)

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
    """The mock "paginate" tag."""

    name = TAG_FORM
    end = TAG_ENDFORM

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)

        stream.expect(TOKEN_TAG, value=TAG_FORM)
        tok = stream.current
        stream.next_token()

        stream.expect(TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_identifier(stream.current.value))

        expect(expr_stream, TOKEN_IDENTIFIER)
        article = parse_identifier(expr_stream)
        expr_stream.next_token()

        # End of expression
        expect(expr_stream, TOKEN_EOF)

        # Advance the stream passed the expression and read the block.
        stream.next_token()
        block = parser.parse_block(stream, end=END_FORMBLOCK)
        stream.expect(TOKEN_TAG, value=TAG_ENDFORM)

        return CommentFormNode(tok, article=article, block=block)
