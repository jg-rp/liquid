from __future__ import annotations

from typing import TYPE_CHECKING

from . import expressions
from ._parser import (
    PRECEDENCE_COMPARISON,
    PRECEDENCE_LOGICAL_AND,
    PRECEDENCE_LOGICAL_NOT,
    PRECEDENCE_LOGICAL_OR,
    PRECEDENCE_LOGICAL_RIGHT,
    PRECEDENCE_LOWEST,
    PRECEDENCE_MEMBERSHIP,
    PRECEDENCE_PIPE,
    Precedence,
)
from ._parser_legacy import LegacyParser
from .tokens import *
from .tokens import TokenKind

if TYPE_CHECKING:
    from ._markup import Expression
    from .environment import Environment
    from .tokens import Token

CONVENTIONAL_PRECEDENCES: dict[TokenKind, Precedence] = {
    TOKEN_AND: PRECEDENCE_LOGICAL_AND,
    TOKEN_OR: PRECEDENCE_LOGICAL_OR,
    TOKEN_NOT: PRECEDENCE_LOGICAL_NOT,
    TOKEN_CONTAINS: PRECEDENCE_MEMBERSHIP,
    TOKEN_EQ: PRECEDENCE_COMPARISON,
    TOKEN_NE: PRECEDENCE_COMPARISON,
    TOKEN_LT: PRECEDENCE_COMPARISON,
    TOKEN_LE: PRECEDENCE_COMPARISON,
    TOKEN_GT: PRECEDENCE_COMPARISON,
    TOKEN_GE: PRECEDENCE_COMPARISON,
    TOKEN_PIPE: PRECEDENCE_PIPE,
}

LEGACY_PRECEDENCES: dict[TokenKind, Precedence] = {
    TOKEN_AND: PRECEDENCE_LOGICAL_RIGHT,
    TOKEN_OR: PRECEDENCE_LOGICAL_RIGHT,
    TOKEN_NOT: PRECEDENCE_LOGICAL_NOT,
    TOKEN_CONTAINS: PRECEDENCE_MEMBERSHIP,
    TOKEN_EQ: PRECEDENCE_COMPARISON,
    TOKEN_NE: PRECEDENCE_COMPARISON,
    TOKEN_LT: PRECEDENCE_COMPARISON,
    TOKEN_LE: PRECEDENCE_COMPARISON,
    TOKEN_GT: PRECEDENCE_COMPARISON,
    TOKEN_GE: PRECEDENCE_COMPARISON,
    TOKEN_PIPE: PRECEDENCE_PIPE,
}


class ExtendedParser(LegacyParser):
    """A parser that extends Shopify/liquid syntax with composable expressions."""

    INFIX_OPERATORS: frozenset[TokenKind] = frozenset(
        [
            TOKEN_AND,
            TOKEN_OR,
            TOKEN_CONTAINS,
            TOKEN_EQ,
            TOKEN_NE,
            TOKEN_LT,
            TOKEN_LE,
            TOKEN_GT,
            TOKEN_GE,
            TOKEN_PIPE,
        ]
    )

    TERMINATE_FILTER: frozenset[TokenKind] = frozenset(
        [
            TOKEN_WC,
            TOKEN_OUT_END,
            TOKEN_TAG_END,
            TOKEN_TEXT,
            TOKEN_RPAREN,
            TOKEN_EOI,
            TOKEN_IF,
            TOKEN_ELSE,
            TOKEN_RBRACKET,
            TOKEN_RBRACE,
            TOKEN_PIPE,
            TOKEN_AND,
            TOKEN_OR,
            TOKEN_CONTAINS,
            TOKEN_EQ,
            TOKEN_NE,
            TOKEN_LT,
            TOKEN_LE,
            TOKEN_GT,
            TOKEN_GE,
        ]
    )

    KEYWORD_ARGUMENT_DELIMITERS: frozenset[TokenKind] = frozenset(
        [
            TOKEN_COLON,
            TOKEN_ASSIGN,
        ]
    )

    def __init__(
        self,
        env: Environment,
        source: str,
        template_name: str,
        tokens: list[Token],
    ) -> None:
        super().__init__(env, source, template_name, tokens)
        if env.conventional_operator_precedence:
            self.precedences = CONVENTIONAL_PRECEDENCES
        else:
            self.precedences = LEGACY_PRECEDENCES

    def parse_expression(
        self, precedence: Precedence = PRECEDENCE_LOWEST, *, infix: bool = True
    ) -> Expression:
        # Ignore `infix`. Infix operators are valid in all contexts in the extended
        # parser.
        expr = self.parse_primary_expression(precedence, infix=True)
        return self.parse_ternary_expression(expr) if self.kind() == TOKEN_IF else expr

    def parse_filtered_expression(
        self, precedence: Precedence = PRECEDENCE_LOWEST, *, infix: bool = False
    ) -> Expression:
        # Delegate to `parse_expression`. Filters are valid in all contexts in the
        # extended parser.

        # Ignore `infix`. Infix operators are valid in all contexts in the extended
        # parser.
        return self.parse_expression(precedence, infix=True)

    def parse_ternary_expression(self, consequence: Expression) -> Expression:
        self.eat(TOKEN_IF)

        condition = self.parse_primary_expression()
        alternative: Expression | None = None

        if self.kind() == TOKEN_ELSE:
            self.pos += 1
            alternative = self.parse_primary_expression()

        return expressions.Ternary(
            consequence.token, consequence, condition, alternative
        )

    def parse_basic_expression(self) -> Expression:
        kind = self.kind()

        if kind == TOKEN_LPAREN:
            return self.parse_range_or_group()

        if kind == TOKEN_NOT:
            return self.parse_not_expression()

        return super().parse_basic_expression()

    def parse_not_expression(self) -> Expression:
        token = self.next()
        return expressions.LogicalNot(
            token, self.parse_expression(PRECEDENCE_LOGICAL_NOT)
        )

    def parse_range_or_group(self) -> Expression:
        token = self.eat(TOKEN_LPAREN)
        expr = self.parse_expression()

        if self.kind() == TOKEN_DOUBLE_DOT:
            self.pos += 1
            stop = self.parse_expression(PRECEDENCE_LOWEST, infix=False)
            self.eat(TOKEN_RPAREN, message="missing bracket")
            return expressions.RangeLiteral(token, expr, stop)

        closing_token = self.eat(TOKEN_RPAREN, message="unbalanced brackets")
        segments: list[expressions.PathSegment] | None = None

        if self.kind() in self.PATH_PUNCTUATION:
            segments = self.parse_path_selectors()

        return expressions.Group(token, expr, segments, closing_token)
