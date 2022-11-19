"""A drop-in replacement for the standard `if` tag that supports the
logical `not` operator and grouping terms with parentheses."""

from liquid.builtin.tags.if_tag import IfTag
from liquid.expression import Expression
from liquid.expressions import parse_boolean_expression_with_parens
from liquid.parse import expect
from liquid.stream import TokenStream
from liquid.token import TOKEN_EXPRESSION


class IfNotTag(IfTag):
    """A drop-in replacement for the standard `if` tag that supports the
    logical `not` operator and grouping terms with parentheses."""

    def parse_expression(self, stream: TokenStream) -> Expression:
        """Pare a boolean expression from a stream of tokens."""
        expect(stream, TOKEN_EXPRESSION)
        return parse_boolean_expression_with_parens(stream.current.value)
