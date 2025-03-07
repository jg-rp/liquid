"""The built-in _echo_ tag."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from liquid.builtin.expressions import FilteredExpression
from liquid.builtin.expressions import Nil
from liquid.builtin.output import OutputNode
from liquid.tag import Tag
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG

if TYPE_CHECKING:
    from liquid.ast import Node
    from liquid.expression import Expression
    from liquid.stream import TokenStream

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
        if stream.current.kind == TOKEN_EOF:
            expr: Expression = Nil(stream.current)
        else:
            expr = FilteredExpression.parse(
                self.env, stream.into_inner(tag=token, eat=False)
            )
        return self.node_class(token, expr)
