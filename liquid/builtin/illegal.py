"""Tag definition for illegal or unregistered tags."""
from __future__ import annotations

from liquid.token import TOKEN_ILLEGAL, TOKEN_EXPRESSION
from liquid.tag import Tag
from liquid.stream import TokenStream
from liquid.exceptions import LiquidSyntaxError
from liquid.ast import IllegalNode


class Illegal(Tag):
    """Tag definition for dealing with illegal or unregistered tags."""

    name = TOKEN_ILLEGAL
    block = False

    def parse(self, stream: TokenStream) -> IllegalNode:
        tok = stream.current
        stream.next_token()

        if stream.current.type == TOKEN_EXPRESSION:
            stream.next_token()

        raise LiquidSyntaxError(f"unexpected tag '{tok.value}'", linenum=tok.linenum)
