"""Tag and node definition for the built-in "echo" tag."""

import sys


from liquid.ast import Node
from liquid.builtin.statement import StatementNode

from liquid.expression import NIL
from liquid.expression import Expression
from liquid.parse import expect

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_EOF

TAG_ECHO = sys.intern("echo")


class EchoNode(StatementNode):
    """Parse tree node for the built-in "echo" tag."""

    def __repr__(self) -> str:  # pragma: no cover
        return f"EchoNode(tok={self.tok}, expression={self.expression!r})"


class EchoTag(Tag):
    """The built-in "echo" tag."""

    name = TAG_ECHO
    block = False

    def _parse_expression(self, value: str) -> Expression:
        return self.env.parse_filtered_expression_value(value)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_ECHO)
        tok = stream.current
        stream.next_token()

        if stream.current.type == TOKEN_EOF:
            expr: Expression = NIL
        else:
            expect(stream, TOKEN_EXPRESSION)
            expr = self._parse_expression(stream.current.value)
        return EchoNode(tok, expression=expr)
