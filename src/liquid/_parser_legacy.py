from __future__ import annotations

from collections.abc import Collection
from typing import TYPE_CHECKING

from . import expressions
from ._markup import Block, Expression, Markup
from ._parser import (
    PRECEDENCE_COMPARISON,
    PRECEDENCE_FILTER_ARG,
    PRECEDENCE_LOGICAL_RIGHT,
    PRECEDENCE_LOWEST,
    PRECEDENCE_MEMBERSHIP,
    TERMINATE_EXPRESSION,
    Parser,
    Precedence,
)
from .exceptions import LiquidSyntaxError
from .tags.output import OutputStatement
from .tokens import *
from .tokens import TOKEN_NAMES, TokenKind, span, token_value

if TYPE_CHECKING:
    from .environment import Environment
    from .tokens import Token

# TODO: limit expression depth
# TODO: mark string literals as HTML safe

LEGACY_PRECEDENCES: dict[TokenKind, Precedence] = {
    TOKEN_AND: PRECEDENCE_LOGICAL_RIGHT,
    TOKEN_OR: PRECEDENCE_LOGICAL_RIGHT,
    TOKEN_CONTAINS: PRECEDENCE_MEMBERSHIP,
    TOKEN_EQ: PRECEDENCE_COMPARISON,
    TOKEN_NE: PRECEDENCE_COMPARISON,
    TOKEN_LT: PRECEDENCE_COMPARISON,
    TOKEN_LE: PRECEDENCE_COMPARISON,
    TOKEN_GT: PRECEDENCE_COMPARISON,
    TOKEN_GE: PRECEDENCE_COMPARISON,
}


class LegacyParser(Parser):
    """A single pass template parser compatible with Shopify/liquid v5.12.0."""

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
            TOKEN_PIPE,
        ]
    )

    PATH_PUNCTUATION: frozenset[TokenKind] = frozenset(
        [
            TOKEN_DOT,
            TOKEN_LBRACKET,
        ]
    )

    STRING_LITERAL_KINDS: frozenset[TokenKind] = frozenset(
        [
            TOKEN_SINGLE_QUOTED,
            TOKEN_DOUBLE_QUOTED,
        ]
    )

    KEYWORD_ARGUMENT_DELIMITERS: frozenset[TokenKind] = frozenset(
        [
            TOKEN_COLON,
        ]
    )

    __slots__ = ("precedences",)

    def __init__(
        self,
        env: Environment,
        source: str,
        template_name: str,
        tokens: list[Token],
    ) -> None:
        super().__init__(env, source, template_name, tokens)
        self.precedences = LEGACY_PRECEDENCES

    def parse_block(self, end: Collection[str]) -> Block:
        nodes: Block = []

        while 1:
            token = self.next()
            kind = token[0]

            if kind == TOKEN_TEXT:
                nodes.append(
                    self.env.trim(
                        token_value(token, self.source),
                        self.whitespace_control_carry,
                        self.peek_whitespace_control(),
                    )
                )

            elif kind == TOKEN_OUT_START:
                nodes.append(self.parse_output())

            elif kind == TOKEN_TAG_START:
                if self.peek_tag_name() in end:
                    self.pos -= 1
                    return nodes

                nodes.append(self.parse_tag())

            elif kind == TOKEN_EOI:
                return nodes

            else:
                raise LiquidSyntaxError(
                    f"unexpected {TOKEN_NAMES[kind]}",
                    token=token,
                    source=self.source,
                    name=self.template_name,
                )

    def parse_output(self) -> Markup:
        token = self.tokens[self.pos - 1]

        if self.kind() == TOKEN_WC and self.peek_kind() == TOKEN_OUT_END:
            # Special case for `{{-}}`
            self.carry_whitespace_control()
            self.eat(TOKEN_OUT_END)
            return OutputStatement(token, expressions.NullLiteral(token))

        self.skip_whitespace_control()
        expr = self.parse_filtered_expression(PRECEDENCE_LOWEST, infix=True)
        self.carry_whitespace_control()
        self.eat(TOKEN_OUT_END, message="missing output delimiter")
        return OutputStatement(token, expr)

    def parse_tag(self) -> Markup:
        self.skip_whitespace_control()
        token = self.eat(TOKEN_TAG_NAME, message="missing tag name")
        name = token_value(token, self.source)

        tag = self.env.tags.get(name)

        if tag is None:
            raise LiquidSyntaxError(
                f"unexpected tag {name!r}",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        return tag.parse(token, self)

    def parse_expression(
        self, precedence: Precedence = PRECEDENCE_LOWEST, *, infix: bool = False
    ) -> Expression:
        return self.parse_primary_expression(precedence, infix=infix)

    def parse_primary_expression(
        self, precedence: Precedence = PRECEDENCE_LOWEST, *, infix: bool = False
    ) -> Expression:
        left = self.parse_basic_expression()

        if not infix:
            return left

        while 1:
            kind = self.kind()

            if (
                self.precedences.get(kind, PRECEDENCE_LOWEST) < precedence
                or kind not in self.INFIX_OPERATORS
            ):
                break

            left = self.parse_infix(left)

        return left

    def parse_basic_expression(self) -> Expression:
        kind = self.kind()

        if kind == TOKEN_BLANK:
            return self.parse_blank()

        if kind in (TOKEN_DOUBLE_QUOTE, TOKEN_SINGLE_QUOTE):
            return self.parse_string_literal()

        if kind == TOKEN_EMPTY:
            return self.parse_empty()

        if kind == TOKEN_FALSE:
            return self.parse_false_literal()

        if kind == TOKEN_FLOAT:
            return self.parse_float_literal()

        if kind in (TOKEN_IDENT, TOKEN_IF, TOKEN_ELSE, TOKEN_NOT):
            return self.parse_path()

        if kind == TOKEN_INT:
            return self.parse_int_literal()

        if kind == TOKEN_LBRACKET:
            return self.parse_path()

        if kind == TOKEN_LPAREN:
            return self.parse_range_literal()

        if kind in (TOKEN_NIL, TOKEN_NULL):
            return self.parse_null_literal()

        if kind == TOKEN_TRUE:
            return self.parse_true_literal()

        token = self.current()
        raise LiquidSyntaxError(
            f"unexpected {TOKEN_NAMES[token[0]]}",
            token=token,
            source=self.source,
            name=self.template_name,
        )

    def parse_blank(self) -> Expression:
        # `blank` is a reserved word when it is not followed by segments.
        if self.peek_kind() in self.PATH_PUNCTUATION:
            return self.parse_path()
        return expressions.Blank(self.next())

    def parse_empty(self) -> Expression:
        # `empty` is a reserved word when it is not followed by segments.
        if self.peek_kind() in self.PATH_PUNCTUATION:
            return self.parse_path()
        return expressions.Empty(self.next())

    def parse_false_literal(self) -> Expression:
        # `false` is a reserved word when it is not followed by segments.
        if self.peek_kind() in self.PATH_PUNCTUATION:
            return self.parse_path()
        return expressions.BooleanLiteral(self.next(), False)

    def parse_true_literal(self) -> Expression:
        # `true` is a reserved word when it is not followed by segments.
        if self.peek_kind() in self.PATH_PUNCTUATION:
            return self.parse_path()
        return expressions.BooleanLiteral(self.next(), True)

    def parse_null_literal(self) -> Expression:
        # `null` and `nil` are reserved words when it is not followed by segments.
        if self.peek_kind() in self.PATH_PUNCTUATION:
            return self.parse_path()
        return expressions.NullLiteral(self.next())

    def parse_float_literal(self) -> Expression:
        token = self.next()
        return expressions.FloatLiteral(token, float(token_value(token, self.source)))

    def parse_int_literal(self) -> Expression:
        token = self.next()
        return expressions.IntegerLiteral(token, int(token_value(token, self.source)))

    def parse_range_literal(self) -> expressions.RangeLiteral:
        token = self.eat(TOKEN_LPAREN)
        start = self.parse_expression(PRECEDENCE_LOWEST, infix=False)
        self.eat(TOKEN_DOUBLE_DOT, message="expected a '..'")
        stop = self.parse_expression(PRECEDENCE_LOWEST, infix=False)
        self.eat(TOKEN_RPAREN, message="missing bracket")
        return expressions.RangeLiteral(token, start, stop)

    def parse_string_literal(self) -> expressions.StringLiteral:
        token = self.next()

        if self.kind() == token[0]:
            # Empty string
            return expressions.StringLiteral(token, "", span(token, self.next()))

        return expressions.StringLiteral(
            token,
            token_value(self.eat_one_of(self.STRING_LITERAL_KINDS), self.source),
            self.eat(token[0]),
        )

    def parse_path(self) -> expressions.Variable:
        token = self.current()
        kind = token[0]

        root: expressions.Name | expressions.StringLiteral | expressions.Variable

        if kind in (
            TOKEN_IDENT,
            TOKEN_BLANK,
            TOKEN_EMPTY,
            TOKEN_FALSE,
            TOKEN_TRUE,
            TOKEN_NULL,
            TOKEN_NIL,
            TOKEN_IF,
            TOKEN_ELSE,
            TOKEN_NOT,
        ):
            self.pos += 1
            root = expressions.Name(token, token_value(token, self.source))

        else:
            self.eat(TOKEN_LBRACKET)

            if self.kind() == TOKEN_IDENT:
                root = self.parse_path()
            else:
                root = self.parse_string_literal()

            self.eat(TOKEN_RBRACKET)

        return expressions.Variable(token, root, self.parse_path_selectors())

    def parse_path_selectors(self) -> list[expressions.PathSegment]:
        selectors: list[expressions.PathSegment] = []

        while 1:
            kind = self.kind()

            if kind == TOKEN_LBRACKET:
                selectors.append(self.parse_bracketed_selector())
            elif kind == TOKEN_DOT:
                self.pos += 1
                token = self.eat(TOKEN_IDENT, message="expected a name selector")
                selectors.append(
                    expressions.Name(token, token_value(token, self.source))
                )
            else:
                break

        return selectors

    def parse_bracketed_selector(self) -> expressions.PathSegment:
        self.eat(TOKEN_LBRACKET)
        token = self.next()
        kind = token[0]

        if kind == TOKEN_INT:
            selector = int(token_value(token, self.source))
            self.eat(TOKEN_RBRACKET)
            return expressions.IndexSelector(token, selector)

        if kind in (
            TOKEN_IDENT,
            TOKEN_BLANK,
            TOKEN_EMPTY,
            TOKEN_FALSE,
            TOKEN_TRUE,
            TOKEN_NULL,
            TOKEN_NIL,
            TOKEN_IF,
            TOKEN_ELSE,
            TOKEN_NOT,
        ):
            self.pos -= 1
            selector = self.parse_path()
            self.eat(TOKEN_RBRACKET)
            return selector

        if kind in (TOKEN_SINGLE_QUOTE, TOKEN_DOUBLE_QUOTE):
            self.pos -= 1
            selector = self.parse_string_literal()
            self.eat(TOKEN_RBRACKET)
            return selector

        if kind == TOKEN_RBRACKET:
            raise LiquidSyntaxError(
                "empty bracketed segment",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        if kind == TOKEN_LPAREN:
            self.pos -= 1
            selector = self.parse_range_literal()
            self.eat(TOKEN_RBRACKET)
            return selector

        raise LiquidSyntaxError(
            "expected an integer, identifier or string",
            token=token,
            source=self.source,
            name=self.template_name,
        )

    def parse_infix(self, left: Expression) -> Expression:
        op_token = self.next()
        kind = op_token[0]
        right = self.parse_expression(
            self.precedences.get(kind, PRECEDENCE_LOWEST), infix=True
        )

        if kind == TOKEN_OR:
            return expressions.LogicalOr(op_token, left, right)

        if kind == TOKEN_AND:
            return expressions.LogicalAnd(op_token, left, right)

        if kind == TOKEN_EQ:
            return expressions.Eq(op_token, left, right)

        if kind == TOKEN_NE:
            return expressions.Ne(op_token, left, right)

        if kind == TOKEN_LT:
            return expressions.Lt(op_token, left, right)

        if kind == TOKEN_LE:
            return expressions.Le(op_token, left, right)

        if kind == TOKEN_GT:
            return expressions.Gt(op_token, left, right)

        if kind == TOKEN_GE:
            return expressions.Ge(op_token, left, right)

        if kind == TOKEN_CONTAINS:
            return expressions.Contains(op_token, left, right)

        raise LiquidSyntaxError(
            f"unknown infix operator {token_value(op_token, self.source)!r}",
            token=op_token,
            source=self.source,
            name=self.template_name,
        )

    def parse_line_statements(self) -> Block:
        nodes: Block = []

        while 1:
            token = self.current()
            kind = token[0]

            if kind == TOKEN_TAG_START:
                self.pos += 1
                nodes.append(self.parse_tag())

            elif kind in (TOKEN_WC, TOKEN_TAG_END):
                break

            else:
                raise LiquidSyntaxError(
                    f"unexpected {TOKEN_NAMES[kind]} ({token_value(token, self.source)!r})",
                    token=token,
                    source=self.source,
                    name=self.template_name,
                )

        return nodes

    def parse_filtered_expression(
        self, precedence: Precedence = PRECEDENCE_LOWEST, *, infix: bool = False
    ) -> Expression:
        expr = self.parse_expression(precedence, infix=infix)

        if self.kind() == TOKEN_PIPE:
            expr = self.parse_filters(expr)

        return expr

    def parse_filters(self, left: Expression) -> Expression:
        token = self.eat(TOKEN_PIPE)
        filter_expr = self.parse_filter(token, left)

        while self.kind() == TOKEN_PIPE:
            filter_expr = self.parse_filter(self.next(), filter_expr)

        return filter_expr

    def parse_filter(self, token: Token, left: Expression) -> Expression:
        name_token = self.eat(TOKEN_IDENT, message="missing or malformed filter name")

        if self.kind() in self.TERMINATE_FILTER:
            # No arguments
            return expressions.Filtered(
                token,
                left,
                expressions.Name(name_token, token_value(name_token, self.source)),
                [],
            )

        self.eat(TOKEN_COLON, message="missing colon or pipe")
        args: list[Expression | expressions.KeywordArgument] = []

        while 1:
            kind = self.kind()

            if kind in self.TERMINATE_FILTER:
                break

            if (
                kind == TOKEN_IDENT
                and self.peek_kind() in self.KEYWORD_ARGUMENT_DELIMITERS
            ):
                param = self.parse_identifier()
                self.next()
                args.append(
                    expressions.KeywordArgument(
                        param.token, param, self.parse_expression(PRECEDENCE_FILTER_ARG)
                    )
                )
            else:
                args.append(self.parse_expression(PRECEDENCE_FILTER_ARG))

            if self.kind() in self.TERMINATE_FILTER:
                break

            self.eat(TOKEN_COMMA, message="missing comma or pipe")

        return expressions.Filtered(
            token,
            left,
            expressions.Name(name_token, token_value(name_token, self.source)),
            args,
        )

    def parse_identifier(self) -> expressions.Name:
        token = self.eat(TOKEN_IDENT)

        if self.kind() in self.PATH_PUNCTUATION:
            raise LiquidSyntaxError(
                "expected an identifier, found a path",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        return expressions.Name(token, token_value(token, self.source))

    def parse_name(self) -> expressions.Name:
        kind = self.kind()

        if kind == TOKEN_IDENT:
            return self.parse_identifier()

        if kind in (TOKEN_SINGLE_QUOTE, TOKEN_DOUBLE_QUOTE):
            expr = self.parse_string_literal()
            return expressions.Name(expr.token, expr.value)

        raise LiquidSyntaxError(
            "expected string or identifier",
            token=self.current(),
            source=self.source,
            name=self.template_name,
        )

    def parse_arguments(
        self, require_commas: bool = True
    ) -> list[Expression | expressions.KeywordArgument]:
        args: list[Expression | expressions.KeywordArgument] = []

        while 1:
            kind = self.kind()

            if kind in TERMINATE_EXPRESSION:
                break

            if (
                kind == TOKEN_IDENT
                and self.peek_kind() in self.KEYWORD_ARGUMENT_DELIMITERS
            ):
                # A named argument
                name = self.parse_identifier()
                self.next()
                args.append(
                    expressions.KeywordArgument(
                        name.token,
                        name,
                        self.parse_expression(PRECEDENCE_LOWEST, infix=False),
                    )
                )

            else:
                args.append(self.parse_expression(PRECEDENCE_LOWEST, infix=False))

            kind = self.kind()

            if require_commas and kind not in TERMINATE_EXPRESSION:
                self.eat(TOKEN_COMMA)
            elif kind == TOKEN_COMMA:
                self.pos += 1

        return args

    def parse_keyword_arguments(
        self, require_commas: bool = True
    ) -> list[expressions.KeywordArgument]:
        args: list[expressions.KeywordArgument] = []

        while 1:
            kind = self.kind()

            if kind in TERMINATE_EXPRESSION:
                break

            name = self.parse_identifier()
            self.eat_one_of(self.KEYWORD_ARGUMENT_DELIMITERS)

            args.append(
                expressions.KeywordArgument(
                    name.token,
                    name,
                    self.parse_expression(PRECEDENCE_LOWEST, infix=False),
                )
            )

            kind = self.kind()

            if require_commas and kind not in TERMINATE_EXPRESSION:
                self.eat(TOKEN_COMMA)
            elif kind == TOKEN_COMMA:
                self.pos += 1

        return args

    def parse_positional_arguments(
        self, require_commas: bool = True
    ) -> list[Expression]:
        args: list[Expression] = []

        while 1:
            kind = self.kind()

            if kind in TERMINATE_EXPRESSION:
                break

            args.append(self.parse_expression(PRECEDENCE_LOWEST, infix=False))

            kind = self.kind()

            if require_commas and kind not in TERMINATE_EXPRESSION:
                self.eat(TOKEN_COMMA)
            elif kind == TOKEN_COMMA:
                self.pos += 1

        return args
