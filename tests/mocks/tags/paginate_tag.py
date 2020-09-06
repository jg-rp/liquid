import math
import sys
from typing import Optional, TextIO

from liquid.token import (
    Token,
    TOKEN_EXPRESSION,
    TOKEN_TAG_NAME,
    TOKEN_BY,
    TOKEN_IDENTIFIER,
    TOKEN_INTEGER,
    TOKEN_EOF,
)
from liquid.tag import Tag
from liquid import ast
from liquid.lex import TokenStream, get_expression_lexer
from liquid.expression import Identifier
from liquid.context import Context
from liquid.parse import get_parser, expect, parse_identifier, parse_integer_literal
from liquid.exceptions import LiquidTypeError

TAG_PAGINATE = sys.intern("paginate")
TAG_ENDPAGINATE = sys.intern("endpaginate")


class PaginateNode(ast.Node):

    __slots__ = ("tok", "identifier", "page_size", "block")

    def __init__(
        self, tok: Token, identifier: Identifier, page_size: int, block: ast.BlockNode
    ):
        self.tok = tok
        self.identifier = identifier
        self.page_size = page_size
        self.block = block

    def __str__(self):
        return f"paginate({self.identifier} by {self.page_size}) {{ {self.block} }}"

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        collection = self.identifier.evaluate(context)

        if not collection:
            raise LiquidTypeError(f"cannot paginate {self.identifier.tok.value}")

        collection_size = len(collection)
        page_count = math.ceil(collection_size / self.page_size)
        current_page = context.get("current_page", default=1)

        pagination = {
            "page_size": self.page_size,
            "current_page": current_page,
            "current_offset": current_page * self.page_size,
            "items": collection_size,
            "pages": page_count,
            "parts": [],
            "previous": None,
            "next": None,
        }

        if current_page > 1:
            pagination["previous"] = link("&laquo; Previous", current_page - 1)

        if current_page < page_count:
            pagination["next"] = link("Next &raquo;", current_page + 1)

        # XXX: Not an accurate port of the reference implementation.
        if page_count > 1:
            for page in range(1, page_count + 1):
                if current_page == page:
                    pagination["parts"].append(no_link(page))
                else:
                    pagination["parts"].append(link(page, page))

        ctx = context.extend({"paginate": pagination})
        self.block.render(ctx, buffer)


def link(title, page):
    return {
        "title": title,
        "url": f"/collections/frontpage?page={page}",
        "is_link": True,
    }


def no_link(title):
    return {"title": title, "is_link": False}


class PaginateTag(Tag):

    name = TAG_PAGINATE
    end = TAG_ENDPAGINATE

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)
        lexer = get_expression_lexer(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_PAGINATE)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_stream = lexer.tokenize(stream.current.value)

        # Read the identifier (the object to be paginated).
        expect(expr_stream, TOKEN_IDENTIFIER)
        identifier = parse_identifier(expr_stream)
        expr_stream.next_token()

        # Eat TOKEN_BY
        expect(expr_stream, TOKEN_BY)
        expr_stream.next_token()

        # Read the number of items per page.
        expect(expr_stream, TOKEN_INTEGER)
        page_size = parse_integer_literal(expr_stream)
        expr_stream.next_token()

        # End of expression
        expect(expr_stream, TOKEN_EOF)

        # Advance the stream passed the expression and read the block.
        stream.next_token()
        block = parser.parse_block(stream, end=(TAG_ENDPAGINATE,))
        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDPAGINATE)

        return PaginateNode(
            tok, identifier=identifier, page_size=page_size.value, block=block
        )
