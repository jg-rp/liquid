"""An "if" tag that supports `not`.

A drop-in replacement for the standard `if` tag that supports the
logical `not` operator and grouping terms with parentheses.
"""

from liquid.builtin.tags.if_tag import IfTag
from liquid.expression import Expression
from liquid.stream import TokenStream
from liquid.token import TOKEN_EXPRESSION


class IfNotTag(IfTag):
    """A drop-in replacement for the standard `if` tag that supports the
    logical `not` operator and grouping terms with parentheses.
    """  # noqa: D205

    def parse_expression(self, stream: TokenStream) -> Expression:
        """Pare a boolean expression from a stream of tokens."""
        stream.expect(TOKEN_EXPRESSION)
        return self.env.parse_boolean_expression_value_with_parens(
            stream.current.value, stream.current.start_index
        )
