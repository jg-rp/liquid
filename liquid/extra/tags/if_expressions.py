"""If expression nodes and tags.

Drop-in replacements for the standard output statement, `assign` tag
and `echo` tag that support inline `if` expressions, optionally including
the logical `not` operator and grouping terms with parentheses.
"""

from liquid.builtin.statement import Statement
from liquid.builtin.statement import StatementNode
from liquid.builtin.tags.assign_tag import AssignTag
from liquid.builtin.tags.echo_tag import EchoTag
from liquid.expression import Expression
from liquid.stream import TokenStream
from liquid.token import TOKEN_STATEMENT

# ruff: noqa: D102 D205


class InlineIfStatement(Statement):
    """A drop-in replacement for the standard output statement that supports
    inline `if` expressions.
    """

    def parse(self, stream: TokenStream) -> StatementNode:
        tok = stream.current
        stream.expect(TOKEN_STATEMENT)
        return StatementNode(
            tok, self.env.parse_conditional_expression_value(tok.value, tok.linenum)
        )


class InlineIfAssignTag(AssignTag):
    """A drop-in replacement for the standard `assign` tag that supports
    inline `if` expressions.
    """

    def _parse_expression(self, value: str, linenum: int) -> Expression:
        return self.env.parse_conditional_expression_value(value, linenum)


class InlineIfEchoTag(EchoTag):
    """A drop-in replacement for the standard `echo` tag that supports
    inline `if` expressions.
    """

    def _parse_expression(self, value: str, linenum: int) -> Expression:
        return self.env.parse_conditional_expression_value(value, linenum)


class InlineIfStatementWithParens(Statement):
    """A drop-in replacement for the standard output statement that supports
    inline `if` expressions with the logical `not` operator and grouping
    terms with parentheses.
    """

    def parse(self, stream: TokenStream) -> StatementNode:
        tok = stream.current
        stream.expect(TOKEN_STATEMENT)
        return StatementNode(
            tok,
            self.env.parse_conditional_expression_value_with_parens(
                tok.value, tok.linenum
            ),
        )


class InlineIfAssignTagWithParens(AssignTag):
    """A drop-in replacement for the standard `assign` tag that supports
    inline `if` expressions with the logical `not` operator and grouping
    terms with parentheses.
    """

    def _parse_expression(self, value: str, linenum: int) -> Expression:
        return self.env.parse_conditional_expression_value_with_parens(value, linenum)


class InlineIfEchoTagWithParens(EchoTag):
    """A drop-in replacement for the standard `echo` tag that supports
    inline `if` expressions with the logical `not` operator and grouping
    terms with parentheses.
    """

    def _parse_expression(self, value: str, linenum: int) -> Expression:
        return self.env.parse_conditional_expression_value_with_parens(value, linenum)
