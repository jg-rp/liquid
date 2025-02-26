"""The built-in _echo_ tag."""

import sys

from liquid.ast import Node
from liquid.builtin.expressions import FilteredExpression
from liquid.builtin.output import OutputNode
from liquid.stream import TokenStream
from liquid.tag import Tag
from liquid.token import TOKEN_TAG

TAG_ECHO = sys.intern("echo")


class EchoNode(OutputNode):
    """The built-in _echo_ tag."""

    def __str__(self) -> str:
        return f"{{% echo {self.expression} %}}"


class EchoTag(Tag):
    """The built-in _echo_ tag."""

    name = TAG_ECHO
    block = False
    node_class = EchoNode

    def parse(self, stream: TokenStream) -> Node:  # noqa: D102
        token = stream.eat(TOKEN_TAG)
        return self.node_class(
            token, FilteredExpression.parse(self.env, stream.into_inner(eat=False))
        )
