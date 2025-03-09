"""Tag definition for illegal or unregistered tags."""

from liquid.ast import IllegalNode
from liquid.exceptions import LiquidSyntaxError
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_TAG


class Illegal(Tag):
    """Tag definition for illegal or unregistered tags."""

    name = TOKEN_ILLEGAL
    block = False

    def parse(self, stream: TokenStream) -> IllegalNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.expect(TOKEN_TAG)

        if stream.peek.kind == TOKEN_EXPRESSION:
            next(stream)

        msg = (
            "missing tag name" if not token.value else f"unexpected tag '{token.value}'"
        )
        raise LiquidSyntaxError(msg, token=token)
