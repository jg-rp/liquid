from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import TYPE_CHECKING, Literal

from .exceptions import LiquidSyntaxError
from .expressions import Expression, KeywordArgument, Name, StringLiteral
from .tokens import *
from .tokens import TOKEN_NAMES, token_value

if TYPE_CHECKING:
    from ._markup import Block
    from .environment import LiquidEnvironment
    from .tokens import Token, TokenKind

PRECEDENCE_LOWEST: Literal[1] = 1
PRECEDENCE_LOGICAL_OR: Literal[2] = 2
PRECEDENCE_LOGICAL_AND: Literal[3] = 3
PRECEDENCE_LOGICAL_NOT: Literal[4] = 4
PRECEDENCE_LOGICAL_RIGHT: Literal[5] = 5
PRECEDENCE_COMPARISON: Literal[6] = 6
PRECEDENCE_MEMBERSHIP: Literal[7] = 7
PRECEDENCE_PIPE: Literal[8] = 8
PRECEDENCE_FILTER_ARG: Literal[9] = 9
PRECEDENCE_ADD: Literal[10] = 10
PRECEDENCE_MULL: Literal[11] = 11
PRECEDENCE_NEG: Literal[12] = 12
PRECEDENCE_PREFIX: Literal[13] = 13

type Precedence = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]


TERMINATE_EXPRESSION: frozenset[TokenKind] = frozenset(
    [
        TOKEN_WC,
        TOKEN_OUT_END,
        TOKEN_TAG_END,
        TOKEN_TEXT,
        TOKEN_RPAREN,
        TOKEN_EOI,
        TOKEN_IF,
        TOKEN_ELSE,
        TOKEN_INTERPOLATION_END,
    ]
)


class Parser(ABC):
    """A base parser from which different parser behavior can be derived."""

    __slots__ = (
        "env",
        "eoi",
        "length",
        "pos",
        "source",
        "template_name",
        "tokens",
        "whitespace_control_carry",
    )

    def __init__(
        self,
        env: LiquidEnvironment,
        source: str,
        template_name: str,
        tokens: list[Token],
    ) -> None:
        self.env = env
        self.source = source
        self.template_name = template_name
        self.tokens = tokens
        self.length = len(tokens)
        self.pos: int = 0
        self.eoi: Token = (TOKEN_EOI, len(source), len(source))
        self.whitespace_control_carry: Literal["-"] | None = None

    @classmethod
    def parse(cls, env: LiquidEnvironment, source: str, template_name: str) -> Block:
        return cls(env, source, template_name, env.tokenize(source)).parse_block(())

    @abstractmethod
    def parse_block(self, end: Collection[str]) -> Block:
        """Parse text and markup until reaching a named tag.

        Parameters
        ----------
        end
            Possible tag names that terminate the block.

        Returns
        -------
        block
            A sequence of nodes in the template syntax tree.
        """

    @abstractmethod
    def parse_expression(
        self, precedence: Precedence = PRECEDENCE_LOWEST, *, infix: bool = False
    ) -> Expression:
        """Parse a "common" expression from the token stream.

        Parameters
        ----------
        precedence
            The binding power of this sub expression.
        infix
            When true, accept infix operators when parsing the expression.
        """

    @abstractmethod
    def parse_line_statements(self) -> Block:
        """Parse newline terminated markup from the `{% liquid %}` tag."""

    @abstractmethod
    def parse_filtered_expression(
        self, precedence: Precedence = PRECEDENCE_LOWEST, *, infix: bool = False
    ) -> Expression:
        """Parse a "common" expression optionally followed by one or more filters.

        Parameters
        ----------
        precedence
            The binding power of this sub expression.
        infix
            When true, accept infix operators when parsing the expression.
        """

    @abstractmethod
    def parse_identifier(self) -> Name:
        """Parse an identifier

        Raises
        ------
        LiquidSyntaxError
            If the identifier is followed by path segments.
        """

    @abstractmethod
    def parse_name(self) -> Name:
        """Parse an identifier, possibly surrounded by quotes.

        Raises
        ------
        LiquidSyntaxError
            If the identifier is followed by path segments.
        """

    @abstractmethod
    def parse_string_literal(self) -> StringLiteral:
        """Parse a literal string surrounded by single or double quotes."""

    @abstractmethod
    def parse_arguments(
        self, require_commas: bool = True
    ) -> list[Expression | KeywordArgument]:
        """Parse positional and/or keyword arguments from the token stream.

        Assumes any leading commas have been consumed by the caller, if they are allowed.

        Parameters
        ----------
        require_commas
            When true, throw a syntax error if arguments are not separated by a comma.
        """

    @abstractmethod
    def parse_keyword_arguments(
        self, require_commas: bool = True
    ) -> list[KeywordArgument]:
        """Parse zero or more keyword arguments from the token stream.

        Assumes any leading commas have been consumed by the caller, if they are allowed.

        Parameters
        ----------
        require_commas
            When true, throw a syntax error if arguments are not separated by a comma.
        """

    @abstractmethod
    def parse_positional_arguments(
        self, require_commas: bool = True
    ) -> list[Expression]:
        """Parse zero or more positional arguments from the token stream.

        Assumes any leading commas have been consumed by the caller, if they are allowed.

        Parameters
        ----------
        require_commas
            When true, throw a syntax error if arguments are not separated by a comma.
        """

    def current(self) -> Token:
        """Return the current token without advancing the pointer."""
        if self.pos < self.length:
            return self.tokens[self.pos]
        return self.eoi

    def kind(self) -> TokenKind:
        """Return the kind of the current token without advancing the pointer."""
        if self.pos < self.length:
            return self.tokens[self.pos][0]
        return TOKEN_EOI

    def value(self) -> str:
        """Return the string value associated with the current token."""
        if self.pos < self.length:
            return token_value(self.tokens[self.pos], self.source)
        return ""

    def next(self) -> Token:
        """Return the current token and advance the pointer."""
        if self.pos < self.length:
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return self.eoi

    def peek(self, n: int = 1) -> Token:
        """Return the token at pos+n without advancing the pointer."""
        if self.pos + n < self.length:
            return self.tokens[self.pos + n]
        return self.eoi

    def peek_kind(self, n: int = 1) -> TokenKind:
        """Return the token kind at pos+n without advancing the pointer."""
        if self.pos + n < self.length:
            return self.tokens[self.pos + n][0]
        return TOKEN_EOI

    def eat(self, kind: TokenKind, message: str | None = None) -> Token:
        """Consume and return a token matching `kind`.

        Parameters
        ----------
        kind
            The expected type of the next token in the stream.
        message
            An custom error message to use in the event of a syntax error.

        Raises
        ------
        LiquidSyntaxError
            If the current token's kind does not match `kind`.
        """
        token = self.current()
        if token[0] != kind:
            raise LiquidSyntaxError(
                message or f"unexpected {token_value(token, self.source)!r}",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        self.pos += 1
        return token

    def eat_one_of(self, kinds: set[TokenKind]) -> Token:
        token = self.next()
        if token[0] not in kinds:
            raise LiquidSyntaxError(
                f"unexpected {TOKEN_NAMES[token[0]]!r}",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        return token

    def skip(self, kind: int) -> bool:
        if self.kind() == kind:
            self.pos += 1
            return True
        return False

    def carry_whitespace_control(self) -> None:
        if self.kind() == TOKEN_WC:
            self.pos += 1
            self.whitespace_control_carry = "-"
        else:
            self.whitespace_control_carry = None

    def eat_tag(self, tag_name: str) -> Token:
        self.eat(TOKEN_TAG_START, message=f"expected tag {tag_name!r}")

        if self.kind() == TOKEN_WC:
            self.pos += 1

        token = self.eat(TOKEN_TAG_NAME, message=f"expected tag {tag_name!r}")

        if value := token_value(token, self.source) != tag_name:
            raise LiquidSyntaxError(
                f"unexpected tag {value!r}",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        self.carry_whitespace_control()
        self.eat(TOKEN_TAG_END, message="expected a closing tag delimiter")
        return token

    def eat_empty_tag(self, tag_name: str) -> Token:
        self.eat(TOKEN_TAG_START, message=f"expected tag {tag_name!r}")

        if self.kind() == TOKEN_WC:
            self.pos += 1

        token = self.eat(TOKEN_TAG_NAME, message=f"expected tag {tag_name!r}")

        if value := token_value(token, self.source) != tag_name:
            raise LiquidSyntaxError(
                f"unexpected tag {value!r}",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        # Ignore everything between the tag name and the closing tag delimiter.
        while self.kind() not in TERMINATE_EXPRESSION:
            self.pos += 1

        self.carry_whitespace_control()
        self.eat(TOKEN_TAG_END, message="expected a closing tag delimiter")
        return token

    def expect_expression(self) -> None:
        if self.kind() in TERMINATE_EXPRESSION:
            raise LiquidSyntaxError(
                "expected an expression",
                token=self.current(),
                source=self.source,
                name=self.template_name,
            )

    def peek_tag_name(self) -> str:
        token = self.current()
        if token[0] == TOKEN_WC:
            token = self.peek()

        if token[0] != TOKEN_TAG_NAME:
            raise LiquidSyntaxError(
                "missing tag name",
                token=token,
                source=self.source,
                name=self.template_name,
            )

        return token_value(token, self.source)

    def peek_whitespace_control(self) -> str | None:
        token = self.peek()
        if token[0] == TOKEN_WC:
            return token_value(token, self.source)

    def skip_whitespace_control(self) -> None:
        if self.kind() == TOKEN_WC:
            self.pos += 1

    def tag(self, name: str) -> bool:
        """Return true if we're at the start of a tag named `name`."""
        token = self.peek()
        if token[0] == TOKEN_WC:
            token = self.peek(2)

        return token[0] == TOKEN_TAG_NAME and token_value(token, self.source) == name

    def tags(self, names: Collection[str]) -> str | None:
        """Return true if we're at the start of a tag and that tag's name is in `names`."""
        token = self.peek()
        if token[0] == TOKEN_WC:
            token = self.peek(2)

        if token[0] != TOKEN_TAG_NAME:
            return None

        name = token_value(token, self.source)

        if name in names:
            return name

        return None
