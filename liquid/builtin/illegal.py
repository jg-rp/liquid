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

    def parse(self, stream: TokenStream) -> IllegalNode:  # noqa: D102
        token = stream.eat(TOKEN_TAG)

        if stream.current.kind == TOKEN_EXPRESSION:
            stream.next_token()

        raise LiquidSyntaxError(f"unexpected tag '{token.value}'", token=token)
